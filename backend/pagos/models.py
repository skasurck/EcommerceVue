from django.db import models


class ConfiguracionTransferencia(models.Model):
    """
    Singleton — siempre se usa el registro con id=1.
    Guarda los datos bancarios que se muestran en el checkout.
    """
    banco         = models.CharField('Banco', max_length=100, blank=True)
    clabe         = models.CharField('CLABE interbancaria', max_length=18, blank=True)
    numero_cuenta = models.CharField('Número de cuenta', max_length=20, blank=True)
    beneficiario  = models.CharField('Beneficiario', max_length=200, blank=True)
    instrucciones = models.TextField('Instrucciones adicionales', blank=True)
    activa        = models.BooleanField('Mostrar en checkout', default=True)

    class Meta:
        verbose_name = 'Configuración de transferencia'

    def __str__(self):
        return f'Transferencia — {self.banco}'

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
