"""
Reprocesa todas las imágenes del slider para aplicar el nuevo límite de tamaño (640×960 mobile, 1440×900 desktop).
Uso: python manage.py reprocess_slider_images
"""
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from PIL import Image

from productos.models import HomeSliderImage


class Command(BaseCommand):
    help = "Redimensiona y recomprime las imágenes del slider a los nuevos tamaños máximos."

    def _process_field(self, instance, field, max_size, label):
        if not field:
            return False
        try:
            field.open()
            with Image.open(field) as img:
                img.load()

            original_size = img.size
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if "A" in img.mode:
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background

            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            new_size = img.size

            buf = BytesIO()
            img.save(buf, format="WEBP", quality=82)
            import os
            base = os.path.splitext(os.path.basename(field.name))[0]
            filename = f"{slugify(base)}_{get_random_string(7)}.webp"

            # Borrar archivo viejo y guardar el nuevo
            field.delete(save=False)
            field.save(filename, ContentFile(buf.getvalue()), save=False)
            self.stdout.write(
                f"  {label}: {original_size} → {new_size}  ({buf.tell() // 1024} KiB)"
            )
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  {label} ERROR: {e}"))
            return False

    def handle(self, *args, **kwargs):
        slides = HomeSliderImage.objects.all()
        total = slides.count()
        self.stdout.write(f"Procesando {total} slides...")

        for slide in slides:
            self.stdout.write(f"\nSlide #{slide.pk} — {slide.titulo or '(sin título)'}")
            changed = False
            changed |= self._process_field(slide, slide.imagen, (1440, 900), "desktop")
            changed |= self._process_field(slide, slide.imagen_mobile, (640, 960), "mobile ")
            if changed:
                # Guardar solo los campos de imagen para no disparar lógica de save()
                slide.save(update_fields=["imagen", "imagen_mobile"])

        self.stdout.write(self.style.SUCCESS("\nListo."))
