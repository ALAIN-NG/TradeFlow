from django.urls import path
from . import views

urlpatterns = [
    path('client/', views.client_page, name="client-page"),
    path('vendeur/', views.vendeur_page, name="vendeur-page"),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('manager-dashboard/', views.manager_dashboard.as_view(), name='manager-dashboard'),
    path('seller-dashboard/', views.seller_dashboard, name='seller-dashboard'),
    path('manage-clients/', views.manage_clients, name='manage-clients'),
    path('manage-sellers/', views.manage_sellers, name='manage-sellers'),
    path('manage-managers/', views.manage_managers, name='manage-managers'),
    path('manage-articles/', views.manage_articles, name='manage-articles'),
    path('view-sales-stats/', views.view_sales_stats, name='view-sales-stats'),
    path('api/sales-by-period/', views.sales_by_period, name='sales_by_period'),
    path('api/top-selling-articles/', views.top_selling_articles, name='top_selling_articles'),
    path('api/seller-performance/', views.seller_performance, name='seller_performance'),
    path('api/paid-unpaid-invoices/', views.paid_unpaid_invoices, name='paid_unpaid_invoices'),
    path('sales-trends/', views.sales_trends, name='sales_trends'),
    path('dashboard/', views.dashboard, name='dashboard'),
]


 
