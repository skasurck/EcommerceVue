from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ConfiguracionTransferencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banco', models.CharField(blank=True, max_length=100, verbose_name='Banco')),
                ('clabe', models.CharField(blank=True, max_length=18, verbose_name='CLABE interbancaria')),
                ('numero_cuenta', models.CharField(blank=True, max_length=20, verbose_name='Número de cuenta')),
                ('beneficiario', models.CharField(blank=True, max_length=200, verbose_name='Beneficiario')),
                ('instrucciones', models.TextField(blank=True, verbose_name='Instrucciones adicionales')),
                ('activa', models.BooleanField(default=True, verbose_name='Mostrar en checkout')),
            ],
            options={
                'verbose_name': 'Configuración de transferencia',
            },
        ),
    ]
