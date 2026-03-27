import logging
import os
from io import BytesIO

from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from PIL import Image

logger = logging.getLogger(__name__)


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    telefono = models.CharField(max_length=20, blank=True)
    empresa = models.CharField(max_length=150, blank=True)
    foto = models.ImageField(upload_to='perfiles/', null=True, blank=True)
    rol = models.CharField(
        max_length=20,
        choices=[
            ("cliente", "Cliente"),
            ("admin", "Administrador"),
            ("super_admin", "Super Administrador"),
        ],
        default="cliente",
    )

    def __str__(self):
        return f"Perfil de {self.user.username}"

    def save(self, *args, **kwargs):
        if self.rol in ("admin", "super_admin"):
            if not self.user.is_staff:
                self.user.is_staff = True
                self.user.save(update_fields=["is_staff"])
        else:
            if self.user.is_staff:
                self.user.is_staff = False
                self.user.save(update_fields=["is_staff"])

        # Convertir foto de perfil a WebP
        if self.pk:
            try:
                old_instance = Perfil.objects.get(pk=self.pk)
                foto_changed = old_instance.foto != self.foto
            except Perfil.DoesNotExist:
                old_instance = None
                foto_changed = False
        else:
            old_instance = None
            foto_changed = False

        is_new_foto = self.pk is None and self.foto
        if (is_new_foto or foto_changed) and self.foto and not self.foto.name.lower().endswith('.webp'):
            if foto_changed and old_instance and old_instance.foto:
                old_instance.foto.delete(save=False)
            try:
                self.foto.open()
                with Image.open(self.foto) as img:
                    img.load()
                base_name = os.path.splitext(os.path.basename(self.foto.name))[0]
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if 'A' in img.mode:
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img)
                    img = background
                buffer = BytesIO()
                img.save(buffer, format='WEBP', quality=85)
                filename = f"{slugify(base_name)}_{get_random_string(7)}.webp"
                self.foto.save(filename, ContentFile(buffer.getvalue()), save=False)
            except Exception as e:
                logger.exception("Error convirtiendo foto de perfil a WebP: %s", e)

        super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)
