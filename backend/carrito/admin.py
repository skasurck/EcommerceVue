from django.contrib import admin
from .models import Cart, CartItem, CartReservation


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "updated_at")
    search_fields = ("id", "user__username")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "producto", "cantidad")
    search_fields = ("cart__id", "cart__user__username", "producto__nombre")
    list_select_related = ("cart", "producto")


@admin.register(CartReservation)
class CartReservationAdmin(admin.ModelAdmin):
    list_display = ("cart", "started_at", "expires_at")
    search_fields = ("cart__id", "cart__user__username")