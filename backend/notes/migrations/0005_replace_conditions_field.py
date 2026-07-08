from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0004_migrate_conditions_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='note',
            name='conditions',
        ),
        migrations.RenameField(
            model_name='note',
            old_name='conditions_new',
            new_name='conditions',
        ),
    ]
