from django.db import migrations, models
from django.utils.text import slugify


def poblar_slugs(apps, schema_editor):
    Producto = apps.get_model('productos', 'Producto')
    productos = Producto.objects.filter(slug='').order_by('id')
    for p in productos.iterator():
        base = slugify(p.nombre)
        if not base:
            base = f'producto-{p.pk}'
        slug = base[:200]
        n = 1
        while Producto.objects.filter(slug=slug).exclude(pk=p.pk).exists():
            suffix = f'-{n}'
            slug = base[:200 - len(suffix)] + suffix
            n += 1
        p.slug = slug
        p.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0024_producto_rating_promedio_producto_total_resenas_and_more'),
    ]

    operations = [
        # Paso 1: agregar campo sin restricción unique (permite vacíos temporalmente)
        migrations.AddField(
            model_name='producto',
            name='slug',
            field=models.SlugField(max_length=200, blank=True, default='', db_index=True),
        ),
        # Paso 2: poblar slugs en todos los productos existentes
        migrations.RunPython(poblar_slugs, migrations.RunPython.noop),
        # Paso 3: agregar restricción unique ahora que todos tienen slug
        migrations.AlterField(
            model_name='producto',
            name='slug',
            field=models.SlugField(max_length=200, unique=True, blank=True, db_index=True),
        ),
        # Campo aprobada en Resena (si lo detectó makemigrations)
        migrations.AddField(
            model_name='resena',
            name='aprobada',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
