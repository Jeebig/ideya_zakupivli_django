from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from content.models import Tag


class Service(models.Model):
    """Один пункт зі списку 'Замовникам' або 'Учасникам' (тендерна документація, протоколи УО і т.д.)."""
    ZAMOVNYKAM = 'zamovnykam'
    UCHASNYKAM = 'uchasnykam'
    AUDIENCE_CHOICES = [
        (ZAMOVNYKAM, 'Замовникам'),
        (UCHASNYKAM, 'Учасникам'),
    ]

    audience = models.CharField('Розділ', max_length=20, choices=AUDIENCE_CHOICES)
    title = models.CharField('Назва послуги', max_length=255)
    slug = models.SlugField(max_length=280, blank=True)
    short_description = models.CharField('Короткий опис (для картки)', max_length=400, blank=True)
    whats_included = models.TextField('Що входить у послугу', blank=True, help_text='Кожен пункт з нового рядка')
    risks = models.TextField('Типові помилки / ризики', blank=True, help_text='Кожен пункт з нового рядка')
    client_provides = models.TextField('Що надає клієнт', blank=True)
    result_format = models.CharField('Формат результату', max_length=255, blank=True)
    duration = models.CharField('Строк виконання', max_length=120, blank=True)
    price = models.CharField('Вартість / від', max_length=120, blank=True)
    urgent_available = models.BooleanField('Можливе термінове виконання', default=False)
    not_included = models.TextField('Що не входить у послугу', blank=True)
    cta_label = models.CharField('Текст кнопки', max_length=120, blank=True)
    tags = models.ManyToManyField(Tag, related_name='services', blank=True, verbose_name='Теми')
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['audience', 'order']
        unique_together = ('audience', 'slug')
        verbose_name = 'Послуга (Замовникам/Учасникам)'
        verbose_name_plural = 'Послуги (Замовникам/Учасникам)'

    def __str__(self):
        return f'{self.get_audience_display()}: {self.title}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('services:service_detail', args=[self.audience, self.slug])

    def included_list(self):
        return [line.strip() for line in self.whats_included.splitlines() if line.strip()]

    def risks_list(self):
        return [line.strip() for line in self.risks.splitlines() if line.strip()]


class ConsultationService(models.Model):
    """Пункт сторінки 'Послуги та консультації' (разова консультація, перевірка документа тощо)."""
    ONE_TIME = 'one_time'
    ONGOING = 'ongoing'
    TYPE_CHOICES = [
        (ONE_TIME, 'Разова допомога'),
        (ONGOING, 'Постійний супровід'),
    ]

    title = models.CharField('Назва', max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    service_type = models.CharField('Тип', max_length=20, choices=TYPE_CHOICES, default=ONE_TIME)
    description = models.TextField('Опис', blank=True)
    format_note = models.CharField(
        'Примітка про формат/ціну', max_length=255,
        default='Відповідь надається письмово. Вартість — за запитом.',
    )
    problem = models.TextField('Яку проблему вирішуємо', blank=True)
    client_provides = models.TextField('Що надає клієнт', blank=True)
    result_format = models.CharField('Формат результату', max_length=255, blank=True)
    duration = models.CharField('Строк', max_length=120, blank=True)
    price = models.CharField('Вартість / від', max_length=120, blank=True)
    urgent_available = models.BooleanField('Можливе термінове виконання', default=False)
    not_included = models.TextField('Що не входить', blank=True)
    cta_label = models.CharField('Текст кнопки', max_length=120, blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['service_type', 'order']
        verbose_name = 'Послуга (консультації)'
        verbose_name_plural = "Послуги та консультації"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)
