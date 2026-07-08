from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import Condition, Note
from .serializers import NoteSerializer
from .services.ai import summarize_document
from .services.pdf import extract_text
from .services.web_search import search_for_note


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

    def get_queryset(self):
        queryset = Note.objects.all().prefetch_related('conditions')
        q = self.request.query_params.get('q', '').strip()
        if not q:
            return queryset

        return queryset.filter(
            Q(title__icontains=q) | Q(subject__icontains=q) | Q(conditions__name__icontains=q)
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
                    title=researched['title'],
                    subject=researched['subject'],
                    summary=researched['summary'],
                    content=researched['content'],
                    source=Note.SOURCE_WEB,
                    verification=Note.VERIFICATION_AI_RESEARCH,
                )
                note.conditions.set(Condition.bulk_get_or_create(researched['conditions']))
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
            title=summarized['title'],
            subject=summarized['subject'],
            summary=summarized['summary'],
            content=summarized['content'],
            source=Note.SOURCE_PDF,
            source_file=file,
            verification=summarized['verification'],
            verification_note=summarized['verification_note'],
        )
        note.conditions.set(Condition.bulk_get_or_create(summarized['conditions']))
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

        note.title = summarized['title']
        note.subject = summarized['subject']
        note.summary = summarized['summary']
        note.content = summarized['content']
        note.verification = summarized['verification']
        note.verification_note = summarized['verification_note']
        note.save()
        note.conditions.set(Condition.bulk_get_or_create(summarized['conditions']))
        return Response(self.get_serializer(note).data)

    def perform_destroy(self, instance):
        if instance.source_file:
            instance.source_file.delete(save=False)
        instance.delete()
