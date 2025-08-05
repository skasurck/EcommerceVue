from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    telefono = models.CharField(max_length=20, blank=True)
    empresa = models.CharField(max_length=150, blank=True)
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
        super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)
