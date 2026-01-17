import os
from django.core.management.base import BaseCommand
from django.db.models import Q
from productos.models import Producto
from django.conf import settings

class Command(BaseCommand):
    help = 'Reprocesa todas las imágenes de productos existentes para convertirlas a formato WebP y generar miniaturas WebP.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('--- Iniciando el reprocesamiento de imágenes de productos ---'))
        
        # Obtener todos los productos que tienen una imagen principal
        productos_a_procesar = Producto.objects.filter(
            Q(imagen_principal__isnull=False) & ~Q(imagen_principal='')
        )
        
        total_productos = productos_a_procesar.count()
        if total_productos == 0:
            self.stdout.write(self.style.WARNING('No se encontraron productos con imágenes para procesar.'))
            return

        self.stdout.write(f'Se encontraron {total_productos} productos para procesar.')
        
        procesados_correctamente = 0
        errores = 0

        for i, producto in enumerate(productos_a_procesar):
            self.stdout.write(f'Procesando producto {i + 1}/{total_productos}: "{producto.nombre}" (ID: {producto.pk})...', ending='')
            
            try:
                # Ahora pasamos el flag `reprocess_image=True` para forzar la conversión.
                producto.save(reprocess_image=True)
                self.stdout.write(self.style.SUCCESS(' OK'))
                procesados_correctamente += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f' ERROR: {e}'))
                errores += 1

        self.stdout.write(self.style.SUCCESS('\n--- Proceso de reprocesamiento completado ---'))
        self.stdout.write(f'Total de productos analizados: {total_productos}')
        self.stdout.write(self.style.SUCCESS(f'Imágenes procesadas correctamente: {procesados_correctamente}'))
        if errores > 0:
            self.stdout.write(self.style.ERROR(f'Productos con errores: {errores}'))
        else:
            self.stdout.write('No hubo errores durante el proceso.')
