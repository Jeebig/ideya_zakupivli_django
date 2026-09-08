from django.shortcuts import redirect
from django.http import HttpResponse
from django.shortcuts import render
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


class LegalPageView(TemplateView):
    page_templates = {
        'privacy': 'core/privacy.html',
        'terms': 'core/terms.html',
        'services_terms': 'core/services_terms.html',
        'documents': 'core/documents.html',
        'disclaimer': 'core/disclaimer.html',
    }

    def get_template_names(self):
        return [self.page_templates[self.kwargs['page']]]


def robots_txt(request):
    return HttpResponse(
        'User-agent: *\nDisallow: /admin/\nDisallow: /media/\nSitemap: /sitemap.xml\n',
        content_type='text/plain',
    )


def sitemap_xml(request):
    from django.urls import reverse
    urls = [
        reverse('core:home'), reverse('core:about'), reverse('services:poslugy'),
        reverse('content:article_list'), reverse('content:faq_list'),
        reverse('content:official_list'), reverse('consultations:contacts'),
        reverse('core:privacy'), reverse('core:terms'), reverse('core:services_terms'),
        reverse('core:documents'), reverse('core:disclaimer'),
    ]
    body = ''.join(f'<url><loc>{request.build_absolute_uri(url)}</loc></url>' for url in urls)
    return HttpResponse(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>',
        content_type='application/xml',
    )


def page_not_found(request, exception):
    return render(request, '404.html', status=404)


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
