from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.HomeView.as_view(), name = 'home'),
    path('add-invoice/', views.AddInvoiceView.as_view(), name='add-invoice'),
    path('view-invoice/<int:pk>/', views.InvoiceVisualizationView.as_view(), name='view-invoice'),
    path('invoice-pdf/<int:pk>/', views.get_invoice_pdf, name="invoice-pdf"),
    path('invoice/update/<int:pk>/', views.UpdateInvoiceView.as_view(), name='update-invoice'),
]