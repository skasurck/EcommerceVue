from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('productos', '0026_merge_20260402_0935'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EventoUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, db_index=True, max_length=64)),
                ('visitor_id', models.CharField(blank=True, db_index=True, max_length=64)),
                ('tipo', models.CharField(choices=[
                    ('view', 'Vista de producto'),
                    ('view_list', 'Vista de listado'),
                    ('add_cart', 'Añadir al carrito'),
                    ('remove_cart', 'Quitar del carrito'),
                    ('wishlist_add', 'Añadir a wishlist'),
                    ('wishlist_remove', 'Quitar de wishlist'),
                    ('purchase', 'Compra'),
                    ('search', 'Búsqueda'),
                    ('click_rec', 'Click en recomendación'),
                    ('impression_rec', 'Impresión de recomendación'),
                ], db_index=True, max_length=20)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('ip_hash', models.CharField(blank=True, max_length=64)),
                ('user_agent', models.CharField(blank=True, max_length=255)),
                ('is_bot', models.BooleanField(db_index=True, default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('categoria', models.ForeignKey(blank=True, null=True,
                    on_delete=models.deletion.SET_NULL, to='productos.categoria')),
                ('producto', models.ForeignKey(blank=True, db_index=True, null=True,
                    on_delete=models.deletion.SET_NULL, to='productos.producto')),
                ('usuario', models.ForeignKey(blank=True, db_index=True, null=True,
                    on_delete=models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='eventousuario',
            index=models.Index(fields=['usuario', '-created_at'], name='tracking_ev_usuario_idx'),
        ),
        migrations.AddIndex(
            model_name='eventousuario',
            index=models.Index(fields=['visitor_id', '-created_at'], name='tracking_ev_visitor_idx'),
        ),
        migrations.AddIndex(
            model_name='eventousuario',
            index=models.Index(fields=['producto', 'tipo', '-created_at'], name='tracking_ev_prodtipo_idx'),
        ),
        migrations.AddIndex(
            model_name='eventousuario',
            index=models.Index(fields=['tipo', '-created_at'], name='tracking_ev_tipo_idx'),
        ),
        migrations.CreateModel(
            name='AgregadoDiarioProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(db_index=True)),
                ('views', models.PositiveIntegerField(default=0)),
                ('add_carts', models.PositiveIntegerField(default=0)),
                ('wishlist_adds', models.PositiveIntegerField(default=0)),
                ('purchases', models.PositiveIntegerField(default=0)),
                ('impressions_rec', models.PositiveIntegerField(default=0)),
                ('clicks_rec', models.PositiveIntegerField(default=0)),
                ('producto', models.ForeignKey(on_delete=models.deletion.CASCADE,
                    related_name='agregados_tracking', to='productos.producto')),
            ],
            options={
                'unique_together': {('producto', 'fecha')},
            },
        ),
        migrations.AddIndex(
            model_name='agregadodiarioproducto',
            index=models.Index(fields=['-fecha', 'producto'], name='tracking_agg_fechaprod_idx'),
        ),
        migrations.CreateModel(
            name='CoOcurrenciaProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fuente', models.CharField(choices=[
                    ('co_view', 'Co-view'),
                    ('co_cart', 'Co-add-cart'),
                    ('co_purchase', 'Co-purchase'),
                ], db_index=True, max_length=20)),
                ('score', models.FloatField(default=0.0)),
                ('actualizado', models.DateTimeField(auto_now=True)),
                ('destino', models.ForeignKey(on_delete=models.deletion.CASCADE,
                    related_name='co_destino', to='productos.producto')),
                ('origen', models.ForeignKey(on_delete=models.deletion.CASCADE,
                    related_name='co_origen', to='productos.producto')),
            ],
            options={
                'unique_together': {('origen', 'destino', 'fuente')},
            },
        ),
        migrations.AddIndex(
            model_name='coocurrenciaproducto',
            index=models.Index(fields=['origen', 'fuente', '-score'], name='tracking_co_origen_idx'),
        ),
        migrations.CreateModel(
            name='ConsentimientoTracking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visitor_id', models.CharField(blank=True, db_index=True, max_length=64)),
                ('acepta_analytics', models.BooleanField(default=False)),
                ('acepta_personalizacion', models.BooleanField(default=False)),
                ('ip_hash', models.CharField(blank=True, max_length=64)),
                ('user_agent', models.CharField(blank=True, max_length=255)),
                ('version_aviso', models.CharField(default='v1', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('usuario', models.OneToOneField(blank=True, null=True,
                    on_delete=models.deletion.CASCADE,
                    related_name='consentimiento_tracking',
                    to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='consentimientotracking',
            constraint=models.UniqueConstraint(
                condition=models.Q(('usuario__isnull', True), models.Q(('visitor_id', ''), _negated=True)),
                fields=('visitor_id',),
                name='uniq_visitor_consent_anon',
            ),
        ),
    ]
