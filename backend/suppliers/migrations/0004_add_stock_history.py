from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0003_add_odoo_id_cache'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupplierStockHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recorded_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('available_qty', models.IntegerField()),
                ('in_stock', models.BooleanField()),
                ('supplier_product', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='stock_history',
                    to='suppliers.supplierproduct',
                )),
            ],
            options={
                'ordering': ['-recorded_at'],
            },
        ),
        migrations.AddIndex(
            model_name='supplierstockhistory',
            index=models.Index(fields=['supplier_product', 'recorded_at'], name='suppliers_s_supplie_idx'),
        ),
    ]
