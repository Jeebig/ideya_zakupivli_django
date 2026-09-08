from django.contrib import admin
from .models import Tag, Article, FAQItem, OfficialExplanation


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'article_type', 'audience', 'is_published', 'is_featured', 'published_at')
    list_filter = ('article_type', 'audience', 'is_published', 'is_featured', 'tags')
    date_hierarchy = 'published_at'
    list_per_page = 25
    search_fields = ('title', 'summary', 'body', 'short_answer')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    fieldsets = (
        (None, {'fields': ('article_type', 'title', 'slug', 'audience', 'tags', 'summary')}),
        ("Структура роз'яснення (4 кроки)", {
            'fields': ('short_answer', 'legal_basis', 'legal_basis_reference', 'source_url', 'current_as_of', 'exceptions_risks', 'action_algorithm', 'wording', 'template_url', 'author', 'related_articles'),
            'classes': ('collapse',),
        }),
        ('Текст новини', {'fields': ('body', 'changes_document', 'effective_from', 'what_to_do'), 'classes': ('collapse',)}),
        ('Публікація', {'fields': ('is_published', 'is_featured', 'published_at', 'updated_at')}),
    )
    readonly_fields = ('updated_at',)


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ('question', 'audience', 'is_popular', 'order')
    list_filter = ('audience', 'is_popular', 'tags')
    search_fields = ('question', 'answer')
    filter_horizontal = ('tags',)
    ordering = ('order',)


@admin.register(OfficialExplanation)
class OfficialExplanationAdmin(admin.ModelAdmin):
    list_display = ('document_date', 'document_number', 'title', 'document_type', 'status', 'checked_at')
    list_filter = ('document_type', 'status', 'tags')
    search_fields = ('title', 'document_number', 'summary', 'keywords')
    filter_horizontal = ('tags',)
