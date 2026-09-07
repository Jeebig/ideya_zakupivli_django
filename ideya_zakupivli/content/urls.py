from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    path("rozyasnennya/", views.ArticleListView.as_view(), name='article_list'),
    path("rozyasnennya/<slug:slug>/", views.ArticleDetailView.as_view(), name='article_detail'),
    path("novyny/", views.NewsListView.as_view(), name='news_list'),
    path("novyny/<slug:slug>/", views.NewsDetailView.as_view(), name='news_detail'),
    path("faq/", views.FAQListView.as_view(), name='faq_list'),
]
