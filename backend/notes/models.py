from django.db import models


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

    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    type = models.CharField(max_length=50, default='food')
    conditions = models.JSONField(default=list)
    summary = models.TextField()
    content = models.TextField()
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default=SOURCE_MANUAL)
    source_file = models.FileField(upload_to='notes/pdfs/', null=True, blank=True)
    verification = models.CharField(
        max_length=20, choices=VERIFICATION_CHOICES, default=VERIFICATION_UNVERIFIED
    )
    verification_note = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
