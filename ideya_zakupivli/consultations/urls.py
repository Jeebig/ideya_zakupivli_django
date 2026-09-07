from django.urls import path
from . import views

app_name = 'consultations'

urlpatterns = [
    path("kontakty/", views.ContactsView.as_view(), name='contacts'),
    path("kontakty/dyakuyemo/", views.ThanksView.as_view(), name='thanks'),
]
