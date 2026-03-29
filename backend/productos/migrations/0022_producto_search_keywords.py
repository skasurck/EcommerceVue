from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0021_listadeseos'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='search_keywords',
            field=models.TextField(
                blank=True,
                default='',
                help_text='Palabras clave generadas automáticamente por IA para mejorar la búsqueda (sinónimos, abreviaciones, términos alternativos).',
            ),
        ),
    ]
