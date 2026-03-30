from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0004_add_stock_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplierproduct',
            name='is_active',
            field=models.BooleanField(default=True, db_index=True),
        ),
        migrations.AddField(
            model_name='supplierproduct',
            name='consecutive_404s',
            field=models.IntegerField(default=0),
        ),
    ]
