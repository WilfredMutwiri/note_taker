from django.db.models import Case, IntegerField, Q, When
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import Condition, Food, Note
from .serializers import NoteSerializer
from .services.ai import summarize_document
from .services.pdf import extract_text
from .services.web_search import search_for_note

# Common words that are too generic to usefully match on their own when a query is
# split into individual terms below.
STOPWORDS = {
    'a', 'an', 'the', 'and', 'or', 'for', 'of', 'to', 'in', 'on', 'with',
    'is', 'are', 'be', 'can', 'help', 'helps', 'good',
}


def _search_terms(q):
    # Match the full phrase, plus each significant individual word — a practitioner
    # typing "high blood pressure remedies" should still find a local note titled
    # "Blood Pressure" or tagged with condition "Hypertension symptoms", not just an
    # exact substring of the whole phrase. This is deliberately generous: a false-positive
    # local match (shown alongside others) is far cheaper than an unnecessary web search
    # that might fragment an existing note into a near-duplicate.
    words = [w for w in q.split() if len(w) > 2 and w.lower() not in STOPWORDS]
    return list(dict.fromkeys([q, *words]))


def _note_fields_from_ai_result(result):
    return {
        'type': result['type'],
        'title': result['title'],
        'subject': result['subject'],
        'summary': result['summary'],
        'content': result['content'],
        'cautions': result['cautions'],
        'alternatives': result['alternatives'],
        'dosage': result['dosage'],
    }


def _set_note_relations(note, result):
    note.conditions.set(Condition.bulk_get_or_create(result['conditions']))
    note.superior_foods.set(Food.bulk_get_or_create(result['superiorFoods']))
    note.other_foods.set(Food.bulk_get_or_create(result['otherFoods']))


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

    def get_queryset(self):
        queryset = Note.objects.all().prefetch_related('conditions', 'superior_foods', 'other_foods')
        q = self.request.query_params.get('q', '').strip()
        if not q:
            return queryset

        term_filter = Q()
        for term in _search_terms(q):
            term_filter |= (
                Q(title__icontains=term)
                | Q(subject__icontains=term)
                | Q(conditions__name__icontains=term)
                | Q(superior_foods__name__icontains=term)
                | Q(other_foods__name__icontains=term)
            )

        # Practitioner-authored/uploaded notes are shown ahead of AI web-research notes
        # when both match, so a search doesn't get crowded out by web results when a
        # local note already covers the same ground.
        return (
            queryset.filter(term_filter)
            .distinct()
            .annotate(
                is_web=Case(When(source=Note.SOURCE_WEB, then=1), default=0, output_field=IntegerField())
            )
            .order_by('is_web', '-created_at')
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        q = request.query_params.get('q', '').strip()
        if q and not data:
            researched = search_for_note(q)
            if researched:
                note = Note.objects.create(
                    **_note_fields_from_ai_result(researched),
                    source=Note.SOURCE_WEB,
                    verification=Note.VERIFICATION_AI_RESEARCH,
                )
                _set_note_relations(note, researched)
                data = [self.get_serializer(note).data]

        return Response(data)

    def perform_create(self, serializer):
        condition_names = serializer.validated_data.pop('conditions', [])
        instance = serializer.save()
        instance.conditions.set(Condition.bulk_get_or_create(condition_names))

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        # ManualNoteForm submits `content` as a single free-text string from its textarea;
        # the model now stores it as a list of bullet-style points, so wrap it into a
        # single-item list here rather than requiring the frontend to change its UI.
        content_text = data.get('content', '')
        if isinstance(content_text, str):
            if not data.get('summary'):
                data['summary'] = content_text[:220]
            data['content'] = [content_text] if content_text else []
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201, headers=self.get_success_headers(serializer.data))

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_pdf(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'detail': 'No file provided.'}, status=400)

        text = extract_text(file)
        file.seek(0)
        summarized = summarize_document(text, file.name)
        if summarized is None:
            return Response(
                {'detail': "This document doesn't appear to be about a food or a disease."},
                status=422,
            )

        note = Note.objects.create(
            **_note_fields_from_ai_result(summarized),
            source=Note.SOURCE_PDF,
            source_file=file,
            verification=summarized['verification'],
            verification_note=summarized['verification_note'],
        )
        _set_note_relations(note, summarized)
        return Response(self.get_serializer(note).data, status=201)

    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        note = self.get_object()

        if note.source == Note.SOURCE_PDF:
            if not note.source_file:
                return Response({'detail': 'This note has no source PDF to regenerate from.'}, status=400)
            filename = note.source_file.name.rsplit('/', 1)[-1]
            with note.source_file.open('rb') as file:
                text = extract_text(file)
            summarized = summarize_document(text, filename)
            if summarized is None:
                return Response(
                    {'detail': "This document doesn't appear to be about a food or a disease."},
                    status=422,
                )
        elif note.source == Note.SOURCE_WEB:
            researched = search_for_note(note.subject)
            if not researched:
                return Response(
                    {'detail': 'Could not refresh this research note right now. Try again shortly.'},
                    status=502,
                )
            summarized = {**researched, 'verification': Note.VERIFICATION_AI_RESEARCH, 'verification_note': ''}
        else:
            return Response({'detail': 'This note cannot be regenerated.'}, status=400)

        for field, value in _note_fields_from_ai_result(summarized).items():
            setattr(note, field, value)
        note.verification = summarized['verification']
        note.verification_note = summarized['verification_note']
        note.save()
        _set_note_relations(note, summarized)
        return Response(self.get_serializer(note).data)

    def perform_destroy(self, instance):
        if instance.source_file:
            instance.source_file.delete(save=False)
        instance.delete()
