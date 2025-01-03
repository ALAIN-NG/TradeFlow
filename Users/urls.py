from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name = 'signup'),
    path('', views.LoginView.as_view(), name = 'login'),
    path('login/', views.LoginView.as_view(), name = 'login'),
    path('add-customer/', views.AddCustomerView.as_view(), name='add-customer'),
    path('add-seller/', views.AddSellerView.as_view(), name='add-seller'),
    path('add-manager/', views.AddManagerView.as_view(), name='add-manager'),
    path('person-view/', views.PersonView.as_view(), name = 'person-view'),
    path('update-person/<int:pk>/', views.UpdatePersonView.as_view(), name='update-person'),
]