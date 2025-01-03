from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
    path('article-view/', views.ArticleView.as_view(), name = 'article-view'),
    path('update-article/<int:pk>/', views.UpdateArticleView.as_view(), name='update-article'), 
    path('add-article/', views.AddArticleView.as_view(), name='add-article'),
]
