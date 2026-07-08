from rest_framework import serializers

from .models import Note


class ConditionsField(serializers.ListField):
    child = serializers.CharField()

    def to_representation(self, value):
        # `value` is the M2M related manager. Iterating `.all()` (not `.values_list()`)
        # is what lets this use the queryset's `prefetch_related('conditions')` cache
        # instead of issuing a fresh query per note — see NoteViewSet.get_queryset.
        return sorted(c.name for c in value.all())


class NoteSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    verificationNote = serializers.CharField(source='verification_note', read_only=True)
    conditions = ConditionsField()

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
