from django.urls import path, re_path
from . import views

app_name = 'content'

urlpatterns = [
    path("rozyasnennya/", views.ArticleListView.as_view(), name='article_list'),
    path("rozyasnennya/ofitsiyni/", views.OfficialExplanationListView.as_view(), name='official_list'),
    path("normatyvna-baza/", views.NormativeActListView.as_view(), name='normative_list'),
    re_path(r"^rozyasnennya/(?P<slug>[-\w]+)/$", views.ArticleDetailView.as_view(), name='article_detail'),
    path("novyny/", views.NewsListView.as_view(), name='news_list'),
    re_path(r"^novyny/(?P<slug>[-\w]+)/$", views.NewsDetailView.as_view(), name='news_detail'),
    path("faq/", views.FAQListView.as_view(), name='faq_list'),
]
