# Generated manually to align DB schema with current Notification model
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_notification_is_read_notification_monitor_id_and_more'),
    ]

    operations = [
        # Estos campos no existen en el modelo actual y están causando errores NOT NULL
        migrations.RemoveField(
            model_name='notification',
            name='is_read',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='monitor_id',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='monitor_name',
        ),
    ]


