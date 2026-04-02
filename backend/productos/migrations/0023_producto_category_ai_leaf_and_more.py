from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("productos", "0022_producto_search_keywords"),
    ]

    operations = [
        migrations.AddField(
            model_name="producto",
            name="category_ai_leaf",
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
        migrations.AddField(
            model_name="producto",
            name="category_ai_match_type",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name="producto",
            name="category_ai_main",
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
        migrations.AlterField(
            model_name="producto",
            name="category_ai_sub",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
