from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path("", views.HomeView.as_view(), name='home'),
    path("pro-mene/", views.AboutView.as_view(), name='about'),
    path("privacy/", views.LegalPageView.as_view(), {'page': 'privacy'}, name='privacy'),
    path("umovy-korystuvannya/", views.LegalPageView.as_view(), {'page': 'terms'}, name='terms'),
    path("umovy-poslug/", views.LegalPageView.as_view(), {'page': 'services_terms'}, name='services_terms'),
    path("zberihannya-dokumentiv/", views.LegalPageView.as_view(), {'page': 'documents'}, name='documents'),
    path("disklaimer/", views.LegalPageView.as_view(), {'page': 'disclaimer'}, name='disclaimer'),
    path("robots.txt", views.robots_txt, name='robots'),
    path("sitemap.xml", views.sitemap_xml, name='sitemap'),
    path("subscribe/", views.subscribe, name='subscribe'),
]
