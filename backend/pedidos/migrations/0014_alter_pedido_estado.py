from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0013_cupones_descuento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='estado',
            field=models.CharField(
                choices=[
                    ('iniciado', 'Iniciado'),
                    ('pendiente', 'Pendiente'),
                    ('pagado', 'Pagado'),
                    ('confirmado', 'Confirmado'),
                    ('enviado', 'Enviado'),
                    ('fallido', 'Fallido'),
                    ('cancelado', 'Cancelado'),
                    ('en_disputa', 'En disputa'),
                    ('contracargo', 'Contracargo'),
                ],
                default='pendiente',
                max_length=20,
            ),
        ),
    ]
