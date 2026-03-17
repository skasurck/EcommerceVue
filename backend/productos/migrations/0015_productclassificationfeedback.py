from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("productos", "0014_remove_producto_categoria_alter_producto_estado_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductClassificationFeedback",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("input_text", models.TextField()),
                ("target_main", models.CharField(db_index=True, max_length=128)),
                ("target_sub", models.CharField(db_index=True, max_length=255)),
                (
                    "source",
                    models.CharField(
                        choices=[("manual_single", "Manual single"), ("manual_bulk", "Manual bulk")],
                        default="manual_single",
                        max_length=32,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "producto",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="classification_feedback",
                        to="productos.producto",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at", "-id"],
            },
        ),
    ]
