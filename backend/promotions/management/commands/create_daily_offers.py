
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from promotions.models import DailyOffer, PromotionSettings
from suppliers.models import SupplierProduct, ProductSupplierMap
from productos.models import Producto

class Command(BaseCommand):
    help = 'Creates daily offers for 10 random products.'

    def handle(self, *args, **options):
        settings = PromotionSettings.load()
        if not settings.daily_offers_enabled:
            self.stdout.write(self.style.WARNING('Daily offers are disabled in settings. Exiting.'))
            return

        self.stdout.write(self.style.SUCCESS('Daily offers are enabled. Starting to create offers...'))

        # Deactivate yesterday's offers
        yesterday = timezone.now() - timedelta(days=1)
        deactivated_offers = DailyOffer.objects.filter(is_active=True, start_date__lte=yesterday)
        
        for offer in deactivated_offers:
            offer.is_active = False
            try:
                # Find the corresponding main product and remove the discount
                product_map = ProductSupplierMap.objects.get(supplier_sku=offer.product.supplier_sku)
                main_product = product_map.product
                main_product.precio_rebajado = None
                main_product.save()
                self.stdout.write(self.style.SUCCESS(f'Discount removed for: {main_product.nombre}'))
            except ProductSupplierMap.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Could not find ProductSupplierMap for SKU {offer.product.supplier_sku}'))
        
        if deactivated_offers.exists():
            DailyOffer.objects.bulk_update(deactivated_offers, ['is_active'])
            self.stdout.write(self.style.WARNING(f'Deactivated {deactivated_offers.count()} old offers.'))

        # Select 10 random products for new offers
        candidate_products = SupplierProduct.objects.filter(
            in_stock=True, 
            price_supplier__gt=0
        ).exclude(
            daily_offers__is_active=True
        )

        if candidate_products.count() < 10:
            self.stdout.write(self.style.ERROR('Not enough products to create 10 new offers.'))
            return

        selected_products = random.sample(list(candidate_products), 10)
        new_offers_count = 0
        now = timezone.now()
        
        for supplier_product in selected_products:
            try:
                # Find the corresponding main product
                product_map = ProductSupplierMap.objects.get(supplier_sku=supplier_product.supplier_sku)
                main_product = product_map.product

                original_price = main_product.precio_normal
                sale_price = (original_price * Decimal('0.95')).quantize(Decimal('0.01'))
                
                # Create the daily offer
                DailyOffer.objects.create(
                    product=supplier_product,
                    original_price=original_price,
                    sale_price=sale_price,
                    start_date=now,
                    end_date=now + timedelta(days=1),
                    is_active=True
                )
                
                # Update the main product's discounted price
                main_product.precio_rebajado = sale_price
                main_product.save()

                self.stdout.write(self.style.SUCCESS(f'- Offer created for: {main_product.nombre} (Sale Price: {sale_price})'))
                new_offers_count += 1
            except ProductSupplierMap.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Could not find ProductSupplierMap for SKU {supplier_product.supplier_sku}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'- Failed to create offer for {supplier_product.name}: {e}'))

        self.stdout.write(f'\nProcess finished. Total offers created: {new_offers_count}')

