from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Article


class ArticlePublicationTests(TestCase):
    def test_future_article_is_hidden_from_public_list(self):
        Article.objects.create(
            title='Future clarification',
            article_type=Article.CLARIFICATION,
            is_published=True,
            published_at=timezone.now() + timedelta(days=1),
        )

        response = self.client.get(reverse('content:article_list'))

        self.assertNotContains(response, 'Future clarification')

    def test_published_article_is_visible(self):
        Article.objects.create(
            title='Published clarification',
            article_type=Article.CLARIFICATION,
            is_published=True,
            published_at=timezone.now() - timedelta(minutes=1),
        )

        response = self.client.get(reverse('content:article_list'))

        self.assertContains(response, 'Published clarification')

    def test_article_pagination_renders_django_value(self):
        for index in range(10):
            Article.objects.create(
                title=f'Published clarification {index}',
                article_type=Article.CLARIFICATION,
                is_published=True,
                published_at=timezone.now() - timedelta(minutes=1),
            )

        response = self.client.get(reverse('content:article_list'))

        self.assertContains(response, 'Сторінка 1 з 2')
        self.assertNotContains(response, '{{ page_obj.paginator.num_pages')

    def test_official_explanations_page_is_available(self):
        response = self.client.get(reverse('content:official_list'))

        self.assertEqual(response.status_code, 200)