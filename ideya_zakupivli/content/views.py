from django.views.generic import ListView, DetailView
from .models import Article, Tag, FAQItem, OfficialExplanation
from django.db.models import Q
from django.utils import timezone


class ArticleListView(ListView):
    """Каталог Роз'яснень з фільтрами за темою, аудиторією та пошуком."""
    model = Article
    template_name = 'content/article_list.html'
    context_object_name = 'articles'
    paginate_by = 9

    def get_queryset(self):
        qs = Article.objects.filter(
            article_type=Article.CLARIFICATION, is_published=True,
            published_at__lte=timezone.now(),
        )
        tag_slug = self.request.GET.get('tag')
        audience = self.request.GET.get('audience')
        query = self.request.GET.get('q')
        if tag_slug:
            qs = qs.filter(tags__slug=tag_slug)
        if audience in ('zamovnykam', 'uchasnykam'):
            qs = qs.filter(audience=audience)
        if query:
            q = query.strip()
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(summary__icontains=q) |
                Q(short_answer__icontains=q) |
                Q(legal_basis__icontains=q) |
                Q(action_algorithm__icontains=q) |
                Q(wording__icontains=q) |
                Q(body__icontains=q)
            )
        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tags'] = Tag.objects.all()
        ctx['current_tag'] = self.request.GET.get('tag', '')
        ctx['current_audience'] = self.request.GET.get('audience', '')
        ctx['query'] = self.request.GET.get('q', '')
        return ctx


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'content/article_detail.html'
    context_object_name = 'article'
    slug_field = 'slug'

    def get_queryset(self):
        return Article.objects.filter(
            article_type=Article.CLARIFICATION, is_published=True,
            published_at__lte=timezone.now(),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        article = self.object
        ctx['related_faq'] = FAQItem.objects.filter(tags__in=article.tags.all()).distinct()[:5]
        ctx['related_articles'] = Article.objects.filter(
            article_type=Article.CLARIFICATION, tags__in=article.tags.all(),
            is_published=True, published_at__lte=timezone.now(),
        ).exclude(pk=article.pk).distinct()[:4]
        return ctx


class NewsListView(ListView):
    """Стрічка новин — короткі оперативні пости, окремо від Роз'яснень."""
    model = Article
    template_name = 'content/news_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        qs = Article.objects.filter(
            article_type=Article.NEWS, is_published=True,
            published_at__lte=timezone.now(),
        )
        tag_slug = self.request.GET.get('tag')
        query = self.request.GET.get('q')
        if tag_slug:
            qs = qs.filter(tags__slug=tag_slug)
        if query:
            q = query.strip()
            qs = qs.filter(Q(title__icontains=q) | Q(summary__icontains=q) | Q(body__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tags'] = Tag.objects.all()
        ctx['current_tag'] = self.request.GET.get('tag', '')
        return ctx


class NewsDetailView(DetailView):
    model = Article
    template_name = 'content/news_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        return Article.objects.filter(
            article_type=Article.NEWS, is_published=True,
            published_at__lte=timezone.now(),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        article = self.object
        ctx['related_clarifications'] = Article.objects.filter(
            article_type=Article.CLARIFICATION, tags__in=article.tags.all(),
            is_published=True, published_at__lte=timezone.now(),
        ).distinct()[:4]
        return ctx


class FAQListView(ListView):
    model = FAQItem
    template_name = 'content/faq_list.html'
    context_object_name = 'faq_items'

    def get_queryset(self):
        qs = FAQItem.objects.all()
        # support quick filter for popular items (used from home teaser)
        if self.request.GET.get('popular') in ('1', 'true', 'True'):
            qs = qs.filter(is_popular=True)
        tag_slug = self.request.GET.get('tag')
        audience = self.request.GET.get('audience')
        if tag_slug:
            qs = qs.filter(tags__slug=tag_slug)
        if audience in ('zamovnykam', 'uchasnykam'):
            qs = qs.filter(audience=audience)
        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tags'] = Tag.objects.filter(faq_items__isnull=False).distinct()
        ctx['current_tag'] = self.request.GET.get('tag', '')
        ctx['current_audience'] = self.request.GET.get('audience', '')
        return ctx


class OfficialExplanationListView(ListView):
    model = OfficialExplanation
    template_name = 'content/official_list.html'
    context_object_name = 'official_documents'
    paginate_by = 12

    def get_queryset(self):
        qs = OfficialExplanation.objects.all().prefetch_related('tags', 'practical_comment')
        query = self.request.GET.get('q', '').strip()
        tag = self.request.GET.get('tag')
        document_type = self.request.GET.get('document_type')
        status = self.request.GET.get('status')
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        current = self.request.GET.get('current')
        if query:
            qs = qs.filter(
                Q(title__icontains=query) |
                Q(document_number__icontains=query) |
                Q(summary__icontains=query) |
                Q(keywords__icontains=query)
            )
        if tag:
            qs = qs.filter(tags__slug=tag)
        if document_type in dict(OfficialExplanation.DOCUMENT_TYPE_CHOICES):
            qs = qs.filter(document_type=document_type)
        if status in dict(OfficialExplanation.STATUS_CHOICES):
            qs = qs.filter(status=status)
        if year and year.isdigit():
            qs = qs.filter(document_date__year=int(year))
        if month and month.isdigit():
            qs = qs.filter(document_date__month=int(month))
        if current == '1':
            qs = qs.filter(is_current=True)
        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tags'] = Tag.objects.filter(official_explanations__isnull=False).distinct()
        ctx['document_types'] = OfficialExplanation.DOCUMENT_TYPE_CHOICES
        ctx['statuses'] = OfficialExplanation.STATUS_CHOICES
        ctx['filters'] = self.request.GET
        return ctx
