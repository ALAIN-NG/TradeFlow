from django.urls import path
from . import views

urlpatterns = [
    path('customer/', views.index, name='customer-home'),
    path('panier/', views.panier, name='panier'),
    path('commande/', views.order, name='commandes'),
    path('update_article/', views.update_article, name='update_article'),
    path('traitement-commande/', views.traitementOrder, name="traitement-commande")


]
