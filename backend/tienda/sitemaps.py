from django.contrib.sitemaps import Sitemap
from django.db.models import Max

from productos.models import Categoria, Marca, Producto


class StaticPagesSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"
    protocol = "https"

    def items(self):
        return [
            "/",
            "/productos",
            "/categorias",
            "/contacto",
            "/politica-de-privacidad",
            "/terminos-y-condiciones",
            "/politica-de-devoluciones",
        ]

    def location(self, item):
        return item


class ProductoSitemap(Sitemap):
    priority = 0.9
    changefreq = "daily"
    protocol = "https"

    def items(self):
        return (
            Producto.objects.filter(visibilidad=True, estado="publicado")
            .exclude(slug="")
            .order_by("-fecha_creacion")
        )

    def lastmod(self, obj):
        return obj.fecha_creacion

    def location(self, obj):
        return f"/producto/{obj.slug}"


class CategoriaSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"
    protocol = "https"

    def items(self):
        return (
            Categoria.objects.filter(
                productos__visibilidad=True,
                productos__estado="publicado",
            )
            .annotate(last_product_date=Max("productos__fecha_creacion"))
            .distinct()
            .order_by("id")
        )

    def lastmod(self, obj):
        return obj.last_product_date

    def location(self, obj):
        return f"/categoria/{obj.id}"


class MarcaSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"
    protocol = "https"

    def items(self):
        return (
            Marca.objects.filter(
                producto__visibilidad=True,
                producto__estado="publicado",
            )
            .annotate(last_product_date=Max("producto__fecha_creacion"))
            .distinct()
            .order_by("nombre", "id")
        )

    def lastmod(self, obj):
        return obj.last_product_date

    def location(self, obj):
        return f"/marca/{obj.id}"

