from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


AUDIENCE_CHOICES = [
    ('zamovnykam', 'Замовникам'),
    ('uchasnykam', 'Учасникам'),
    ('both', 'Усім'),
]


class Tag(models.Model):
    """Єдина система тегів — використовується і в Роз'ясненнях, і в Новинах, і в FAQ."""
    name = models.CharField('Назва теми', max_length=150, unique=True)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Тема (тег)'
        verbose_name_plural = 'Теми (теги)'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Article(models.Model):
    CLARIFICATION = 'clarification'
    NEWS = 'news'
    TYPE_CHOICES = [
        (CLARIFICATION, "Роз'яснення"),
        (NEWS, 'Новина'),
    ]

    article_type = models.CharField('Тип матеріалу', max_length=20, choices=TYPE_CHOICES, default=CLARIFICATION)
    title = models.CharField('Заголовок', max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    audience = models.CharField('Для кого', max_length=20, choices=AUDIENCE_CHOICES, default='both')
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True, verbose_name='Теми')

    summary = models.TextField('Короткий опис (для списків)', blank=True)

    # Структура "Роз'яснення": 4 кроки
    short_answer = models.TextField('Коротка відповідь', blank=True)
    legal_basis = models.TextField('Нормативна опора', blank=True)
    action_algorithm = models.TextField('Алгоритм дій', blank=True)
    wording = models.TextField('Робоче формулювання', blank=True)

    # Для новин достатньо простого тексту
    body = models.TextField('Текст новини / додатковий текст', blank=True)

    is_published = models.BooleanField('Опубліковано', default=False)
    is_featured = models.BooleanField('Показувати в дайджесті на Головній', default=False)
    published_at = models.DateTimeField('Дата публікації', null=True, blank=True)
    updated_at = models.DateTimeField('Дата оновлення', auto_now=True)

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'Матеріал (роз\u2019яснення / новина)'
        verbose_name_plural = "Роз'яснення та новини"

    def __str__(self):
        return f'[{self.get_article_type_display()}] {self.title}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.article_type == self.NEWS:
            return reverse('content:news_detail', args=[self.slug])
        return reverse('content:article_detail', args=[self.slug])


class FAQItem(models.Model):
    question = models.CharField('Питання', max_length=300)
    answer = models.TextField('Відповідь')
    audience = models.CharField('Для кого', max_length=20, choices=AUDIENCE_CHOICES, default='both')
    tags = models.ManyToManyField(Tag, related_name='faq_items', blank=True, verbose_name='Теми')
    related_article = models.ForeignKey(
        Article, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='faq_from_article', verbose_name="Пов'язане роз'яснення",
        limit_choices_to={'article_type': Article.CLARIFICATION},
    )
    is_popular = models.BooleanField('Популярне питання (показувати на Головній)', default=False)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['order', '-id']
        verbose_name = 'Питання та відповідь'
        verbose_name_plural = 'Питання та відповіді'

    def __str__(self):
        return self.question

    def clean(self):
        super().clean()
        if self.related_article and self.related_article.article_type != Article.CLARIFICATION:
            raise ValidationError({
                'related_article': 'Можна прив’язувати лише роз’яснення.',
            })
