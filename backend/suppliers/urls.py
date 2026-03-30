from django.urls import path

from suppliers.views import (
    SupermexLatestProductsView, SupermexRunView, SupermexSalesStatsView,
    SupermexStockSyncView, SupermexTaskStatusView,
)

urlpatterns = [
    path('supermex/run/', SupermexRunView.as_view(), name='suppliers-supermex-run'),
    path('supermex/stock-sync/', SupermexStockSyncView.as_view(), name='suppliers-supermex-stock-sync'),
    path('supermex/task/<str:task_id>/', SupermexTaskStatusView.as_view(), name='suppliers-supermex-task'),
    path('supermex/products/', SupermexLatestProductsView.as_view(), name='suppliers-supermex-products'),
    path('supermex/sales-stats/', SupermexSalesStatsView.as_view(), name='suppliers-supermex-sales-stats'),
]
