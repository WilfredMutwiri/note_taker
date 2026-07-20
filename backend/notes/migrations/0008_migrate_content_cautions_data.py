from django.db import migrations


def migrate_forward(apps, schema_editor):
    Note = apps.get_model('notes', 'Note')

    for note in Note.objects.all():
        # Fold the deprecated superior/other benefit prose into the new content list
        # rather than dropping it, so nothing existing gets silently lost.
        note.content_new = [
            text for text in [note.superior_benefits, note.other_benefits, note.content] if text
        ]
        note.cautions_new = [note.cautions] if note.cautions else []
        note.save(update_fields=['content_new', 'cautions_new'])


def migrate_backward(apps, schema_editor):
    Note = apps.get_model('notes', 'Note')

    for note in Note.objects.all():
        note.content = '\n\n'.join(note.content_new)
        note.cautions = '\n\n'.join(note.cautions_new)
        note.save(update_fields=['content', 'cautions'])


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0007_note_alternatives_note_cautions_new_note_content_new'),
    ]

    operations = [
        migrations.RunPython(migrate_forward, migrate_backward),
    ]
