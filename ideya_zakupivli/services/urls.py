from django.urls import path, re_path
from . import views
from .models import Service

app_name = 'services'

urlpatterns = [
    path("zamovnykam/", views.ServiceHubView.as_view(audience=Service.ZAMOVNYKAM), name='zamovnykam'),
    path("uchasnykam/", views.ServiceHubView.as_view(audience=Service.UCHASNYKAM), name='uchasnykam'),
    path("poslugy/", views.ConsultationServicesView.as_view(), name='poslugy'),
    # audience обмежено конкретними значеннями, щоб цей паттерн не перехоплював
    # інші дворівневі шляхи на кшталт /kontakty/dyakuyemo/
    re_path(r'^(?P<audience>zamovnykam|uchasnykam)/(?P<slug>[-\w]+)/$',
            views.ServiceDetailView.as_view(), name='service_detail'),
]
