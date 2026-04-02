"""
Script para generar slugs en productos existentes.
Ejecutar DESPUÉS de correr las migraciones:

  python manage.py shell < populate_slugs.py

O también:
  python manage.py shell -c "exec(open('populate_slugs.py').read())"
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

from django.utils.text import slugify
from productos.models import Producto

productos_sin_slug = Producto.objects.filter(slug='')
total = productos_sin_slug.count()
print(f"Productos sin slug: {total}")

actualizados = 0
for p in productos_sin_slug.iterator():
    base = slugify(p.nombre)
    if not base:
        base = f'producto-{p.pk}'
    slug = base[:200]
    n = 1
    while Producto.objects.filter(slug=slug).exclude(pk=p.pk).exists():
        suffix = f'-{n}'
        slug = base[:200 - len(suffix)] + suffix
        n += 1
    Producto.objects.filter(pk=p.pk).update(slug=slug)
    actualizados += 1
    if actualizados % 100 == 0:
        print(f"  {actualizados}/{total}...")

print(f"Listo: {actualizados} slugs generados.")
