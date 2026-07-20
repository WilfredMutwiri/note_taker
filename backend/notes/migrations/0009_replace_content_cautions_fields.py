from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0008_migrate_content_cautions_data'),
    ]

    operations = [
        migrations.RemoveField(model_name='note', name='content'),
        migrations.RemoveField(model_name='note', name='cautions'),
        migrations.RemoveField(model_name='note', name='superior_benefits'),
        migrations.RemoveField(model_name='note', name='other_benefits'),
        migrations.RenameField(model_name='note', old_name='content_new', new_name='content'),
        migrations.RenameField(model_name='note', old_name='cautions_new', new_name='cautions'),
    ]
