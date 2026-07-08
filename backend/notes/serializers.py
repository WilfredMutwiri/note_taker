from rest_framework import serializers

from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    verificationNote = serializers.CharField(source='verification_note', read_only=True)

    class Meta:
        model = Note
        fields = [
            'id',
            'title',
            'subject',
            'type',
            'conditions',
            'summary',
            'content',
            'source',
            'verification',
            'verificationNote',
            'createdAt',
        ]
        read_only_fields = ['id', 'source', 'verification', 'verificationNote', 'createdAt']
