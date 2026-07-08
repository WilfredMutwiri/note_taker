from django.db import migrations


def migrate_conditions_forward(apps, schema_editor):
    Note = apps.get_model('notes', 'Note')
    Condition = apps.get_model('notes', 'Condition')

    for note in Note.objects.all():
        condition_ids = []
        for raw_name in note.conditions:
            name = raw_name.strip()
            if not name:
                continue
            condition = Condition.objects.filter(name__iexact=name).first()
            if not condition:
                condition = Condition.objects.create(name=name)
            condition_ids.append(condition.id)
        note.conditions_new.set(condition_ids)


def migrate_conditions_backward(apps, schema_editor):
    Note = apps.get_model('notes', 'Note')
    for note in Note.objects.all():
        note.conditions = list(note.conditions_new.values_list('name', flat=True))
        note.save(update_fields=['conditions'])


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0003_condition_alter_note_created_at_alter_note_subject_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_conditions_forward, migrate_conditions_backward),
    ]
