from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from productos.category_tree import CATEGORY_TREE
from productos.models import Categoria


class Command(BaseCommand):
    help = "Borra todas las categorías y carga el árbol maestro definido en productos.category_tree."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Eliminando categorías existentes...")
        Categoria.objects.all().delete()

        self.stdout.write("Cargando nuevo árbol de categorías...")
        created = 0

        def create_node(node, parent=None):
            nonlocal created
            cat = Categoria.objects.create(
                nombre=node["name"],
                slug=node.get("slug") or slugify(node["name"]),
                parent=parent,
            )
            created += 1
            for child in node.get("children") or []:
                create_node(child, cat)

        for root in CATEGORY_TREE:
            create_node(root, parent=None)

        self.stdout.write(self.style.SUCCESS(f"Se cargaron {created} categorías."))
