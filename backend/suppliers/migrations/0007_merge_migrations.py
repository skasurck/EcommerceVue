from django.db import migrations


class Migration(migrations.Migration):
    """
    Merge migration to resolve conflict between:
    - 0006_add_supplier_sync_log (added via git)
    - 0006_merge_20260330_1309  (created manually on the server on 2026-03-30)
    """

    dependencies = [
        ('suppliers', '0006_add_supplier_sync_log'),
        ('suppliers', '0006_merge_20260330_1309'),
    ]

    operations = [
    ]
