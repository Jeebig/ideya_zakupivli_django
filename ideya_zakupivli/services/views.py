from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView, ListView
from .models import Service, ConsultationService


class ServiceHubView(TemplateView):
    """Розділова сторінка /zamovnykam/ або /uchasnykam/."""
    template_name = 'services/service_hub.html'
    audience = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['services'] = Service.objects.filter(audience=self.audience)
        ctx['audience'] = self.audience
        ctx['audience_label'] = 'Замовникам' if self.audience == Service.ZAMOVNYKAM else 'Учасникам'
        return ctx


class ServiceDetailView(DetailView):
    """Уніфікований шаблон для всіх 13 сторінок послуг (7 Замовникам + 6 Учасникам)."""
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'

    def get_object(self, queryset=None):
        return get_object_or_404(Service, audience=self.kwargs['audience'], slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        service = self.object
        from content.models import Article, FAQItem
        ctx['related_articles'] = Article.objects.filter(
            article_type=Article.CLARIFICATION, tags__in=service.tags.all(), is_published=True,
        ).distinct()[:4]
        ctx['related_faq'] = FAQItem.objects.filter(tags__in=service.tags.all()).distinct()[:4]
        return ctx


class ConsultationServicesView(ListView):
    model = ConsultationService
    template_name = 'services/consultation_services.html'
    context_object_name = 'consultation_services'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['one_time'] = ConsultationService.objects.filter(service_type=ConsultationService.ONE_TIME)
        ctx['ongoing'] = ConsultationService.objects.filter(service_type=ConsultationService.ONGOING)
        return ctx
