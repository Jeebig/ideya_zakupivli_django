from django.views.generic import ListView, DetailView
from .models import Article, Tag, FAQItem
from django.db.models import Q


class ArticleListView(ListView):
    """Каталог Роз'яснень з фільтрами за темою, аудиторією та пошуком."""
    model = Article
    template_name = 'content/article_list.html'
    context_object_name = 'articles'
    paginate_by = 9

    def get_queryset(self):
        qs = Article.objects.filter(article_type=Article.CLARIFICATION, is_published=True)
        tag_slug = self.request.GET.get('tag')
        audience = self.request.GET.get('audience')
        query = self.request.GET.get('q')
        if tag_slug:
            qs = qs.filter(tags__slug=tag_slug)
        if audience in ('zamovnykam', 'uchasnykam'):
            qs = qs.filter(audience__in=[audience, 'both'])
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
        return Article.objects.filter(article_type=Article.CLARIFICATION, is_published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        article = self.object
        ctx['related_faq'] = FAQItem.objects.filter(tags__in=article.tags.all()).distinct()[:5]
        ctx['related_articles'] = Article.objects.filter(
            article_type=Article.CLARIFICATION, tags__in=article.tags.all(), is_published=True,
        ).exclude(pk=article.pk).distinct()[:4]
        return ctx


class NewsListView(ListView):
    """Стрічка новин — короткі оперативні пости, окремо від Роз'яснень."""
    model = Article
    template_name = 'content/news_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        qs = Article.objects.filter(article_type=Article.NEWS, is_published=True)
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
        return Article.objects.filter(article_type=Article.NEWS, is_published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        article = self.object
        ctx['related_clarifications'] = Article.objects.filter(
            article_type=Article.CLARIFICATION, tags__in=article.tags.all(), is_published=True,
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
            qs = qs.filter(audience__in=[audience, 'both'])
        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tags'] = Tag.objects.filter(faq_items__isnull=False).distinct()
        ctx['current_tag'] = self.request.GET.get('tag', '')
        ctx['current_audience'] = self.request.GET.get('audience', '')
        return ctx
