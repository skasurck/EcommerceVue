from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("productos", "0022_producto_search_keywords"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="producto",
            name="rating_promedio",
            field=models.DecimalField(db_index=True, decimal_places=2, default=0, max_digits=3),
        ),
        migrations.AddField(
            model_name="producto",
            name="total_resenas",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name="Resena",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("calificacion", models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ("comentario", models.TextField(blank=True, default="")),
                ("verificado", models.BooleanField(default=False, help_text="True si el usuario compró el producto.")),
                ("creado", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("producto", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="resenas", to="productos.producto")),
                ("usuario", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="resenas", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-creado"],
                "unique_together": {("producto", "usuario")},
            },
        ),
    ]
