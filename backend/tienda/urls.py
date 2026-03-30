"""
URL configuration for tienda project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from suppliers.views import supplier_status

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from productos.views import editar_producto
from productos.seo import producto_seo_view

urlpatterns = [
    path('mktska-panel-x7k2/admin/', admin.site.urls),
    path('productos/editar/<int:pk>/', editar_producto, name='editar_producto'),
    path('producto/<int:pk>/', producto_seo_view, name='producto_seo'),
    path('api/', include('productos.urls')),
    path('api/', include('usuarios.urls')),
    path('api/', include('carrito.urls')),
    path('api/', include('pedidos.urls')),
    path('api/pagos/', include('pagos.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/suppliers/', include('suppliers.urls')),
    path('api/promotions/', include('promotions.urls')),
    path("api/suppliers/status", supplier_status),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)