from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0005_add_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupplierSyncLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('stock_sync', 'Sync de stock y precios'), ('importacion', 'Importación de productos nuevos'), ('stock_then_import', 'Sync + Importación')], max_length=30)),
                ('estado', models.CharField(choices=[('running', 'En progreso'), ('completed', 'Completado'), ('failed', 'Fallido')], default='running', max_length=20)),
                ('fecha_inicio', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('fecha_fin', models.DateTimeField(blank=True, null=True)),
                ('total', models.IntegerField(default=0)),
                ('updated', models.IntegerField(default=0)),
                ('unchanged', models.IntegerField(default=0)),
                ('errors', models.IntegerField(default=0)),
                ('deactivated', models.IntegerField(default=0)),
                ('new_imported', models.IntegerField(default=0)),
                ('skipped_existing', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['-fecha_inicio'],
            },
        ),
        migrations.CreateModel(
            name='SupplierSyncLogEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('error', 'Error'), ('cambio', 'Cambio')], max_length=10)),
                ('supplier_sku', models.CharField(blank=True, max_length=64)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('url', models.URLField(blank=True)),
                ('mensaje_error', models.TextField(blank=True)),
                ('campo', models.CharField(blank=True, max_length=50)),
                ('valor_anterior', models.CharField(blank=True, max_length=100)),
                ('valor_nuevo', models.CharField(blank=True, max_length=100)),
                ('sync_log', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='suppliers.suppliersynclog')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
