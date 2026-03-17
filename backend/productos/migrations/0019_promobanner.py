from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0018_homesliderimage_titulo_color'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromoBanner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(blank=True, default='', max_length=120)),
                ('descripcion', models.CharField(blank=True, default='', max_length=255)),
                ('imagen', models.ImageField(upload_to='promo_banners/')),
                ('titulo_color', models.CharField(blank=True, default='#ffffff', max_length=7)),
                ('enlace', models.CharField(blank=True, default='', max_length=500)),
                ('orden', models.PositiveIntegerField(db_index=True, default=0)),
                ('activo', models.BooleanField(db_index=True, default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['orden', 'id'],
            },
        ),
    ]
