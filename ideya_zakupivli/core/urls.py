from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path("", views.HomeView.as_view(), name='home'),
    path("pro-mene/", views.AboutView.as_view(), name='about'),
    path("subscribe/", views.subscribe, name='subscribe'),
]
