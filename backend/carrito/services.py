from __future__ import annotations

from typing import Optional

from django.db import transaction

from .models import Cart, CartItem, CartReservation


def _get_cart_from_session(session) -> Optional[Cart]:
    cart_id = session.get("cart_id")
    if not cart_id:
        return None
    try:
        return Cart.objects.select_related("user").get(pk=cart_id)
    except Cart.DoesNotExist:
        session.pop("cart_id", None)
        session.modified = True
        return None


def merge_carts(source: Cart, target: Cart) -> Cart:
    if source.pk == target.pk:
        return target

    with transaction.atomic():
        for item in source.items.select_related("producto"):
            target_item, created = CartItem.objects.get_or_create(
                cart=target, producto=item.producto, defaults={"cantidad": 0}
            )
            if created:
                target_item.cantidad = item.cantidad
            else:
                target_item.cantidad += item.cantidad
            target_item.save(update_fields=["cantidad"])

        try:
            src_res = source.reservation
        except CartReservation.DoesNotExist:
            src_res = None

        if src_res:
            tgt_res, created = CartReservation.objects.get_or_create(
                cart=target,
                defaults={
                    "started_at": src_res.started_at,
                    "expires_at": src_res.expires_at,
                },
            )
            if not created:
                updated = False
                if src_res.started_at < tgt_res.started_at:
                    tgt_res.started_at = src_res.started_at
                    updated = True
                if src_res.expires_at > tgt_res.expires_at:
                    tgt_res.expires_at = src_res.expires_at
                    updated = True
                if updated:
                    tgt_res.save(update_fields=["started_at", "expires_at"])
            src_res.delete()

        source.delete()
    return target


def ensure_cart_for_request(request) -> Cart:
    """Obtiene el carrito correspondiente a la sesión o usuario actual."""

    session = request.session
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        session_cart = _get_cart_from_session(session)
        if session_cart and session_cart.user_id not in (None, request.user.id):
            session_cart = None
            session.pop("cart_id", None)
        if session_cart and session_cart.pk != cart.pk:
            cart = merge_carts(session_cart, cart)
        session["cart_id"] = cart.pk
        session.modified = True
        return cart

    cart = _get_cart_from_session(session)
    if cart is None or not cart.is_guest:
        cart = Cart.objects.create()
    session["cart_id"] = cart.pk
    session.modified = True
    return cart


def sync_session_cart_with_user(session, user) -> Cart:
    """Fusiona el carrito de sesión (si existe) con el del usuario autenticado."""

    cart, _ = Cart.objects.get_or_create(user=user)
    cart_id = session.get("cart_id")
    if cart_id and cart_id != cart.pk:
        try:
            session_cart = Cart.objects.get(pk=cart_id)
        except Cart.DoesNotExist:
            session_cart = None
        if session_cart and session_cart.user_id not in (None, user.id):
            session_cart = None
            session.pop("cart_id", None)
        if session_cart and session_cart.pk != cart.pk:
            cart = merge_carts(session_cart, cart)
    session["cart_id"] = cart.pk
    session.modified = True
    return cart


def clear_cart(cart: Cart) -> None:
    CartItem.objects.filter(cart=cart).delete()
    CartReservation.objects.filter(cart=cart).delete()
