from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import Note
from .serializers import NoteSerializer
from .services.ai import summarize_document
from .services.pdf import extract_text


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

    def get_queryset(self):
        queryset = Note.objects.all()
        q = self.request.query_params.get('q', '').strip().lower()
        if not q:
            return queryset

        matching_ids = [
            note.id
            for note in queryset
            if q in note.title.lower()
            or q in note.subject.lower()
            or any(q in condition.lower() for condition in note.conditions)
        ]
        return queryset.filter(id__in=matching_ids)

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
            conditions=summarized['conditions'],
            summary=summarized['summary'],
            content=summarized['content'],
            source=Note.SOURCE_PDF,
            source_file=file,
        )
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
        note.conditions = summarized['conditions']
        note.summary = summarized['summary']
        note.content = summarized['content']
        note.save()
        return Response(self.get_serializer(note).data)

    def perform_destroy(self, instance):
        if instance.source_file:
            instance.source_file.delete(save=False)
        instance.delete()
