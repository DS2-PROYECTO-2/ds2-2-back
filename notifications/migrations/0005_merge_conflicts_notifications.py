from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0003_add_conversation_message_type"),
        ("notifications", "0004_remove_is_read_and_monitor_fields"),
    ]

    operations = [
        # Merge migration; no schema changes, solo unifica el grafo de migraciones.
    ]
