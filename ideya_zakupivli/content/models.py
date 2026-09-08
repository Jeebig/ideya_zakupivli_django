from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone


AUDIENCE_CHOICES = [
    ('zamovnykam', 'Замовникам'),
    ('uchasnykam', 'Учасникам'),
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
    audience = models.CharField('Для кого', max_length=20, choices=AUDIENCE_CHOICES, default='zamovnykam')
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True, verbose_name='Теми')

    summary = models.TextField('Короткий опис (для списків)', blank=True)

    # Структура "Роз'яснення": 4 кроки
    short_answer = models.TextField('Коротка відповідь', blank=True)
    legal_basis = models.TextField('Нормативна опора', blank=True)
    legal_basis_reference = models.CharField('Пункт і номер нормативного акта', max_length=500, blank=True)
    source_url = models.URLField('Посилання на першоджерело', blank=True)
    current_as_of = models.DateField('Актуально станом на', null=True, blank=True)
    exceptions_risks = models.TextField('Винятки та ризики', blank=True)
    action_algorithm = models.TextField('Алгоритм дій', blank=True)
    wording = models.TextField('Робоче формулювання', blank=True)
    author = models.CharField('Автор / експерт', max_length=255, blank=True)
    template_url = models.URLField('Посилання на файл або шаблон', blank=True)
    changes_document = models.CharField('Документ, яким внесено зміни', max_length=500, blank=True)
    effective_from = models.DateField('Дата набрання чинності', null=True, blank=True)
    what_to_do = models.TextField('Що потрібно зробити замовнику або учаснику', blank=True)
    related_articles = models.ManyToManyField(
        'self', blank=True, symmetrical=False, related_name='related_to', verbose_name='Пов’язані матеріали'
    )

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
    audience = models.CharField('Для кого', max_length=20, choices=AUDIENCE_CHOICES, default='zamovnykam')
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


class OfficialExplanation(models.Model):
    """Посилання на офіційні документи Мінекономіки без копіювання файлів."""
    LAW = 'law'
    RESOLUTION = 'resolution'
    ORDER = 'order'
    PROCEDURE = 'procedure'
    GUIDELINE = 'guideline'
    DOCUMENT_TYPE_CHOICES = [
        (LAW, 'Закон'),
        (RESOLUTION, 'Постанова'),
        (ORDER, 'Наказ'),
        (PROCEDURE, 'Порядок'),
        (GUIDELINE, 'Настанова'),
    ]
    CURRENT = 'current'
    INVALID = 'invalid'
    UPCOMING = 'upcoming'
    STATUS_CHOICES = [
        (CURRENT, 'Чинний'),
        (INVALID, 'Втратив чинність'),
        (UPCOMING, 'Набирає чинності'),
    ]
    document_type = models.CharField('Вид документа', max_length=20, choices=DOCUMENT_TYPE_CHOICES, default=RESOLUTION)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=CURRENT)
    document_date = models.DateField('Дата документа')
    document_number = models.CharField('Номер документа', max_length=120)
    title = models.CharField('Офіційна назва', max_length=500)
    summary = models.TextField('Короткий опис')
    keywords = models.TextField('Ключові слова', blank=True, help_text='Слова через кому')
    tags = models.ManyToManyField(Tag, blank=True, related_name='official_explanations', verbose_name='Теми')
    source_page_url = models.URLField('Посилання на картку документа')
    source_file_url = models.URLField('Офіційне посилання')
    current_text_url = models.URLField('Посилання на чинний текст з #Text', blank=True)
    previous_text_url = models.URLField('Посилання на попередню редакцію', blank=True)
    previous_revision_label = models.CharField('Підпис попередньої редакції', max_length=255, blank=True)
    checked_at = models.DateField('Перевірено', default=timezone.localdate)
    is_current = models.BooleanField('Актуальне', default=True)
    practical_comment = models.ForeignKey(
        Article, blank=True, null=True, on_delete=models.SET_NULL,
        limit_choices_to={'article_type': Article.CLARIFICATION},
        related_name='official_sources', verbose_name='Практичний коментар ІдеЯ',
    )

    class Meta:
        ordering = ['-document_date', '-id']
        verbose_name = 'Офіційне роз’яснення Мінекономіки'
        verbose_name_plural = 'Офіційні роз’яснення Мінекономіки'

    def __str__(self):
        return f'{self.document_number} — {self.title}'
