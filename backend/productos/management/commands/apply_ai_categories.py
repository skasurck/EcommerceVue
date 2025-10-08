from django.core.management.base import BaseCommand
from django.db import transaction
from productos.models import Producto, Categoria

class Command(BaseCommand):
    help = 'Aplica las categorías sugeridas por la IA a los productos.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Buscando productos con categorías sugeridas por IA...")

        products_to_update = Producto.objects.filter(
            category_ai_main__isnull=False,
            categoria__isnull=True
        )

        if not products_to_update.exists():
            self.stdout.write(self.style.SUCCESS("No hay productos nuevos para actualizar."))
            return

        self.stdout.write(f"Se encontraron {products_to_update.count()} productos para actualizar.")

        updated_count = 0
        for product in products_to_update:
            main_cat_name = product.category_ai_main
            sub_cat_name = product.category_ai_sub

            if not main_cat_name:
                continue

            main_category, created = Categoria.objects.get_or_create(
                nombre=main_cat_name,
                parent=None  # Explícitamente busca una categoría principal
            )
            if created:
                self.stdout.write(f"  -> Creada categoría principal: '{main_cat_name}'")

            target_category = main_category
            if sub_cat_name:
                sub_category, created = Categoria.objects.get_or_create(
                    nombre=sub_cat_name,
                    parent=main_category
                )
                if created:
                    self.stdout.write(f"    -> Creada subcategoría: '{sub_cat_name}'")
                target_category = sub_category
            
            product.categoria = target_category
            product.save(update_fields=['categoria'])
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"¡Proceso completado! Se actualizaron {updated_count} productos."))