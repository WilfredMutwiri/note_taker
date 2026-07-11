from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import Condition, Food, Note
from .serializers import NoteSerializer
from .services.ai import summarize_document
from .services.pdf import extract_text
from .services.web_search import search_for_note


def _note_fields_from_ai_result(result):
    return {
        'type': result['type'],
        'title': result['title'],
        'subject': result['subject'],
        'summary': result['summary'],
        'content': result['content'],
        'superior_benefits': result['superiorBenefits'],
        'other_benefits': result['otherBenefits'],
        'dosage': result['dosage'],
        'cautions': result['cautions'],
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

        return queryset.filter(
            Q(title__icontains=q)
            | Q(subject__icontains=q)
            | Q(conditions__name__icontains=q)
            | Q(superior_foods__name__icontains=q)
            | Q(other_foods__name__icontains=q)
        ).distinct()

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
        if not data.get('summary'):
            data['summary'] = data.get('content', '')[:220]
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
        if note.source != Note.SOURCE_PDF or not note.source_file:
            return Response({'detail': 'This note has no source PDF to regenerate from.'}, status=400)

        filename = note.source_file.name.rsplit('/', 1)[-1]
        with note.source_file.open('rb') as file:
            text = extract_text(file)
        summarized = summarize_document(text, filename)

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
