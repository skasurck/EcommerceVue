from django.db import models


TIPO_VIEW = 'view'
TIPO_VIEW_LIST = 'view_list'
TIPO_ADD_CART = 'add_cart'
TIPO_REMOVE_CART = 'remove_cart'
TIPO_WISHLIST_ADD = 'wishlist_add'
TIPO_WISHLIST_REMOVE = 'wishlist_remove'
TIPO_PURCHASE = 'purchase'
TIPO_SEARCH = 'search'
TIPO_CLICK_REC = 'click_rec'
TIPO_IMPRESSION_REC = 'impression_rec'

TIPO_CHOICES = [
    (TIPO_VIEW, 'Vista de producto'),
    (TIPO_VIEW_LIST, 'Vista de listado'),
    (TIPO_ADD_CART, 'Añadir al carrito'),
    (TIPO_REMOVE_CART, 'Quitar del carrito'),
    (TIPO_WISHLIST_ADD, 'Añadir a wishlist'),
    (TIPO_WISHLIST_REMOVE, 'Quitar de wishlist'),
    (TIPO_PURCHASE, 'Compra'),
    (TIPO_SEARCH, 'Búsqueda'),
    (TIPO_CLICK_REC, 'Click en recomendación'),
    (TIPO_IMPRESSION_REC, 'Impresión de recomendación'),
]

TIPOS_VALIDOS = {t for t, _ in TIPO_CHOICES}


class EventoUsuario(models.Model):
    usuario = models.ForeignKey(
        'auth.User', null=True, blank=True,
        on_delete=models.SET_NULL, db_index=True,
    )
    session_key = models.CharField(max_length=64, db_index=True, blank=True)
    visitor_id = models.CharField(max_length=64, db_index=True, blank=True)

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, db_index=True)
    producto = models.ForeignKey(
        'productos.Producto', null=True, blank=True,
        on_delete=models.SET_NULL, db_index=True,
    )
    categoria = models.ForeignKey(
        'productos.Categoria', null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    metadata = models.JSONField(default=dict, blank=True)

    ip_hash = models.CharField(max_length=64, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    is_bot = models.BooleanField(default=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['usuario', '-created_at']),
            models.Index(fields=['visitor_id', '-created_at']),
            models.Index(fields=['producto', 'tipo', '-created_at']),
            models.Index(fields=['tipo', '-created_at']),
        ]

    def __str__(self):
        ident = self.usuario_id or self.visitor_id or self.session_key
        return f"{self.tipo} · prod={self.producto_id} · {ident}"


class AgregadoDiarioProducto(models.Model):
    producto = models.ForeignKey(
        'productos.Producto', on_delete=models.CASCADE,
        related_name='agregados_tracking',
    )
    fecha = models.DateField(db_index=True)
    views = models.PositiveIntegerField(default=0)
    add_carts = models.PositiveIntegerField(default=0)
    wishlist_adds = models.PositiveIntegerField(default=0)
    purchases = models.PositiveIntegerField(default=0)
    impressions_rec = models.PositiveIntegerField(default=0)
    clicks_rec = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('producto', 'fecha')
        indexes = [models.Index(fields=['-fecha', 'producto'])]

    def __str__(self):
        return f"{self.fecha} · {self.producto_id}"


FUENTE_CO_VIEW = 'co_view'
FUENTE_CO_CART = 'co_cart'
FUENTE_CO_PURCHASE = 'co_purchase'

FUENTE_CHOICES = [
    (FUENTE_CO_VIEW, 'Co-view'),
    (FUENTE_CO_CART, 'Co-add-cart'),
    (FUENTE_CO_PURCHASE, 'Co-purchase'),
]


class CoOcurrenciaProducto(models.Model):
    origen = models.ForeignKey(
        'productos.Producto', on_delete=models.CASCADE,
        related_name='co_origen',
    )
    destino = models.ForeignKey(
        'productos.Producto', on_delete=models.CASCADE,
        related_name='co_destino',
    )
    fuente = models.CharField(max_length=20, choices=FUENTE_CHOICES, db_index=True)
    score = models.FloatField(default=0.0)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('origen', 'destino', 'fuente')
        indexes = [models.Index(fields=['origen', 'fuente', '-score'])]

    def __str__(self):
        return f"{self.origen_id} → {self.destino_id} ({self.fuente}: {self.score})"


class ConsentimientoTracking(models.Model):
    usuario = models.OneToOneField(
        'auth.User', null=True, blank=True,
        on_delete=models.CASCADE, related_name='consentimiento_tracking',
    )
    visitor_id = models.CharField(max_length=64, db_index=True, blank=True)
    acepta_analytics = models.BooleanField(default=False)
    acepta_personalizacion = models.BooleanField(default=False)
    ip_hash = models.CharField(max_length=64, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    version_aviso = models.CharField(max_length=20, default='v1')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['visitor_id'],
                condition=models.Q(usuario__isnull=True) & ~models.Q(visitor_id=''),
                name='uniq_visitor_consent_anon',
            ),
        ]

    def __str__(self):
        ident = self.usuario_id or self.visitor_id
        return f"Consent {ident} (analytics={self.acepta_analytics})"
