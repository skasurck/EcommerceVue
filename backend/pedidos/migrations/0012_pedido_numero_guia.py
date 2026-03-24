from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0011_alter_pedido_metodo_pago'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='numero_guia',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]
