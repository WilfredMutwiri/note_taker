from rest_framework import serializers

from .models import Note


class TagListField(serializers.ListField):
    """Serializes any M2M-of-named-things field (Condition, Food, ...) as a plain list of
    name strings. Used for `conditions`, `superiorFoods`, and `otherFoods`."""

    child = serializers.CharField()

    def to_representation(self, value):
        # `value` is the M2M related manager. Iterating `.all()` (not `.values_list()`)
        # is what lets this use the queryset's `prefetch_related(...)` cache instead of
        # issuing a fresh query per note — see NoteViewSet.get_queryset.
        return sorted(item.name for item in value.all())


class NoteSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    verificationNote = serializers.CharField(source='verification_note', read_only=True)
    conditions = TagListField()
    superiorBenefits = serializers.CharField(source='superior_benefits', read_only=True)
    otherBenefits = serializers.CharField(source='other_benefits', read_only=True)
    dosage = serializers.CharField(read_only=True)
    cautions = serializers.CharField(read_only=True)
    superiorFoods = TagListField(source='superior_foods', read_only=True)
    otherFoods = TagListField(source='other_foods', read_only=True)

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
            'superiorBenefits',
            'otherBenefits',
            'dosage',
            'cautions',
            'superiorFoods',
            'otherFoods',
            'source',
            'verification',
            'verificationNote',
            'createdAt',
        ]
        read_only_fields = [
            'id',
            'source',
            'verification',
            'verificationNote',
            'createdAt',
            'superiorBenefits',
            'otherBenefits',
            'dosage',
            'cautions',
            'superiorFoods',
            'otherFoods',
        ]
