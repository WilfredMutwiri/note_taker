from django.db import models


class Note(models.Model):
    SOURCE_MANUAL = 'manual'
    SOURCE_PDF = 'pdf'
    SOURCE_CHOICES = [
        (SOURCE_MANUAL, 'Manual'),
        (SOURCE_PDF, 'AI-summarized (PDF)'),
    ]

    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    type = models.CharField(max_length=50, default='food')
    conditions = models.JSONField(default=list)
    summary = models.TextField()
    content = models.TextField()
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default=SOURCE_MANUAL)
    source_file = models.FileField(upload_to='notes/pdfs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
