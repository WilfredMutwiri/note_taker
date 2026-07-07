from rest_framework import serializers

from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

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
            'createdAt',
        ]
        read_only_fields = ['id', 'source', 'createdAt']
