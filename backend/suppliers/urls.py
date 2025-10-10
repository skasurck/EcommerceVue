from django.urls import path

from suppliers.views import SupermexLatestProductsView, SupermexRunView

urlpatterns = [
    path('supermex/run/', SupermexRunView.as_view(), name='suppliers-supermex-run'),
    path('supermex/products/', SupermexLatestProductsView.as_view(), name='suppliers-supermex-products'),
]
