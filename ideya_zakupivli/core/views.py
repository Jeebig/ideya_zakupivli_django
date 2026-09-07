from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from content.models import Article, FAQItem
from .models import CaseStudy
from .forms import SubscribeForm
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        featured = Article.objects.filter(
            article_type=Article.CLARIFICATION, is_published=True, is_featured=True,
            published_at__lte=timezone.now(),
        )
        ctx['latest_clarifications'] = (
            featured[:4] if featured.exists()
            else Article.objects.filter(
                article_type=Article.CLARIFICATION,
                is_published=True,
                published_at__lte=timezone.now(),
            )[:4]
        )
        ctx['latest_news'] = Article.objects.filter(
            article_type=Article.NEWS, is_published=True,
            published_at__lte=timezone.now(),
        )[:3]
        ctx['popular_faq'] = FAQItem.objects.filter(is_popular=True)[:5]
        return ctx


class AboutView(TemplateView):
    template_name = 'core/about.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cases'] = CaseStudy.objects.all()
        return ctx


@require_POST
def subscribe(request):
    form = SubscribeForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Дякуємо! Ви підписані на оновлення.')
    else:
        messages.error(request, 'Перевірте, будь ласка, введені дані.')
    # Безпечний редірект: дозволяємо лише внутрішні шляхи або fallback на home
    referer = request.META.get('HTTP_REFERER')
    if referer and url_has_allowed_host_and_scheme(
        referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(referer)
    return redirect(reverse_lazy('core:home'))
