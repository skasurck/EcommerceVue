from django.core.management.base import BaseCommand
from productos.models import ImagenProducto

class Command(BaseCommand):
    help = 'Reprocesa todas las imágenes de la galería de productos para convertirlas a formato WebP.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('--- Iniciando el reprocesamiento de imágenes de la galería ---'))
        
        imagenes_a_procesar = ImagenProducto.objects.exclude(imagen__exact='')
        
        total_imagenes = imagenes_a_procesar.count()
        if total_imagenes == 0:
            self.stdout.write(self.style.WARNING('No se encontraron imágenes en la galería para procesar.'))
            return

        self.stdout.write(f'Se encontraron {total_imagenes} imágenes para procesar.')
        
        procesadas_correctamente = 0
        errores = 0

        for i, imagen_producto in enumerate(imagenes_a_procesar):
            self.stdout.write(f'Procesando imagen {i + 1}/{total_imagenes} (ID: {imagen_producto.pk})...', ending='')
            
            try:
                # Llamamos a save() con el flag para forzar el reprocesamiento
                imagen_producto.save(reprocess_image=True)
                self.stdout.write(self.style.SUCCESS(' OK'))
                procesadas_correctamente += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f' ERROR: {e}'))
                errores += 1

        self.stdout.write(self.style.SUCCESS('\n--- Proceso de reprocesamiento de galería completado ---'))
        self.stdout.write(f'Total de imágenes analizadas: {total_imagenes}')
        self.stdout.write(self.style.SUCCESS(f'Imágenes procesadas correctamente: {procesadas_correctamente}'))
        if errores > 0:
            self.stdout.write(self.style.ERROR(f'Imágenes con errores: {errores}'))
        else:
            self.stdout.write('No hubo errores durante el proceso.')
