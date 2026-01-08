from django.core.management.base import BaseCommand
from django.db import transaction

from productos.models import Categoria, Producto


def _split_segment(raw: str) -> tuple[str, str | None]:
    """Divide un segmento en (nombre, slug opcional)."""
    raw = raw.strip()
    if "(" in raw and raw.endswith(")"):
        name_part, slug_part = raw.rsplit("(", 1)
        return name_part.strip(), slug_part.rstrip(")").strip() or None
    return raw, None


def get_or_create_category_by_path(path: str) -> Categoria | None:
    """
    Busca o crea una categoría por una ruta tipo 'Main > Sub > Hoja'.
    Crea las categorías intermedias si no existen.
    Devuelve la categoría hoja o None si la ruta es inválida.
    """
    if not path:
        return None

    parts = [seg.strip() for seg in str(path).split(">") if seg.strip()]
    if not parts:
        return None

    current_parent = None
    last_category = None

    for i, raw_part in enumerate(parts):
        name, slug = _split_segment(raw_part)
        
        # Buscar la categoría existente
        qs = Categoria.objects.filter(nombre=name, parent=current_parent)
        if slug:
            qs = qs.filter(slug=slug)
        
        category = qs.first()

        if not category:
            # Si no existe, crearla
            category = Categoria.objects.create(
                nombre=name,
                slug=slug or slugify(name),
                parent=current_parent,
            )
            # Imprimir que se creó solo si no es la primera iteración y no es la raíz del tree que creamos al principio
            # if current_parent is not None or i > 0:
            #     # Considerar si se debe imprimir para cada creación o solo para la final
            #     # self.stdout.write(f"  -> Creada categoría en la ruta: '{' > '.join(parts[:i+1])}'")
            pass # Manejaremos la impresión de nuevas categorías al final, o con un logger más sofisticado.
        
        current_parent = category
        last_category = category
    
    return last_category

class Command(BaseCommand):
    help = "Aplica las categorías sugeridas por la IA a los productos."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Buscando productos con categorías sugeridas por IA...")

        products_to_update = Producto.objects.filter(
            category_ai_main__isnull=False,
            categoria__isnull=True,
        )

        if not products_to_update.exists():
            self.stdout.write(self.style.SUCCESS("No hay productos nuevos para actualizar."))
            return

        self.stdout.write(f"Se encontraron {products_to_update.count()} productos para actualizar.")

        updated_count = 0
        created_categories = {} # Para llevar un registro de las nuevas categorías creadas

        for product in products_to_update:
            main_cat_name = product.category_ai_main
            sub_cat_path = product.category_ai_sub

            if not main_cat_name:
                continue

            # Construir la ruta completa para get_or_create_category_by_path
            full_path = main_cat_name
            if sub_cat_path:
                full_path = f"{main_cat_name} > {sub_cat_path}"

            target_category = get_or_create_category_by_path(full_path)

            if target_category:
                product.categoria = target_category
                product.save(update_fields=["categoria"])
                updated_count += 1
                # if target_category.pk not in created_categories: # Esto requeriría una forma de saber si fue 'creada' o 'encontrada'
                #    created_categories[target_category.pk] = target_category.nombre
            else:
                self.stdout.write(self.style.WARNING(f"  -> No se pudo determinar la categoría para el producto {product.id} con ruta: '{full_path}'"))

        # if created_categories:
        #     self.stdout.write(self.style.NOTICE(f"Se crearon nuevas categorías: {', '.join(created_categories.values())}"))

        self.stdout.write(self.style.SUCCESS(f"¡Proceso completado! Se actualizaron {updated_count} productos."))
