from django.db import models


class Condition(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @classmethod
    def bulk_get_or_create(cls, names):
        # Case-insensitive lookup so AI-generated casing variance ("High Cholesterol" vs
        # "high cholesterol") doesn't fragment into duplicate near-identical rows.
        result = []
        for raw in names:
            name = raw.strip()
            if not name:
                continue
            condition = cls.objects.filter(name__iexact=name).first() or cls.objects.create(name=name)
            result.append(condition)
        return result


class Note(models.Model):
    SOURCE_MANUAL = 'manual'
    SOURCE_PDF = 'pdf'
    SOURCE_WEB = 'web'
    SOURCE_CHOICES = [
        (SOURCE_MANUAL, 'Manual'),
        (SOURCE_PDF, 'AI-summarized (PDF)'),
        (SOURCE_WEB, 'AI web research'),
    ]

    VERIFICATION_UNVERIFIED = 'unverified'
    VERIFICATION_WEB_CONFIRMED = 'web_confirmed'
    VERIFICATION_AI_CORRECTED = 'ai_corrected'
    VERIFICATION_AI_RESEARCH = 'ai_research'
    VERIFICATION_CHOICES = [
        (VERIFICATION_UNVERIFIED, 'Unverified'),
        (VERIFICATION_WEB_CONFIRMED, 'Web-confirmed'),
        (VERIFICATION_AI_CORRECTED, 'AI-corrected'),
        (VERIFICATION_AI_RESEARCH, 'AI research'),
    ]

    title = models.CharField(max_length=255, db_index=True)
    subject = models.CharField(max_length=255, db_index=True)
    type = models.CharField(max_length=50, default='food')
    conditions = models.ManyToManyField(Condition, related_name='notes', blank=True)
    summary = models.TextField()
    content = models.TextField()
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default=SOURCE_MANUAL)
    source_file = models.FileField(upload_to='notes/pdfs/', null=True, blank=True)
    verification = models.CharField(
        max_length=20, choices=VERIFICATION_CHOICES, default=VERIFICATION_UNVERIFIED
    )
    verification_note = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
