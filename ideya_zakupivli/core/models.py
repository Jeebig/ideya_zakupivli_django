from django.db import models


class CaseStudy(models.Model):
    """Знеособлений кейс для сторінки 'Про мене'."""
    title = models.CharField('Заголовок кейсу', max_length=255)
    situation = models.TextField('Ситуація')
    action = models.TextField('Дія')
    result = models.TextField('Результат')
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Кейс'
        verbose_name_plural = 'Кейси (Про мене)'

    def __str__(self):
        return self.title


class SiteSettings(models.Model):
    """Синглтон з контактними даними та загальними текстами сайту (редагується в адмінці)."""
    phone = models.CharField('Телефон', max_length=50, blank=True)
    email = models.EmailField('Email', blank=True)
    telegram = models.URLField('Посилання на Telegram', blank=True)
    viber = models.URLField('Посилання на Viber', blank=True)
    response_sla = models.CharField(
        'Орієнтовний термін відповіді', max_length=255,
        default='Орієнтовний термін відповіді — 2 робочі дні',
    )
    consultation_format_note = models.TextField(
        'Пояснення формату консультацій',
        default=(
            'Консультації надаються письмово. Типові питання вже мають відповіді в розділах '
            "«Роз'яснення» та «Питання та відповіді». Індивідуальна консультація по вашій "
            'ситуації — платна, вартість уточнюється після опису ситуації.'
        ),
    )
    about_intro = models.TextField('Вступний текст "Про мене"', blank=True)
    experience_years = models.CharField('Досвід (наприклад "7+ років")', max_length=100, blank=True)
    expert_name = models.CharField('Ім’я та прізвище експерта', max_length=255, blank=True)
    expert_specialization = models.CharField('Спеціалізація', max_length=255, blank=True)
    expert_education = models.TextField('Освіта та сертифікати', blank=True)
    expert_experience = models.TextField('Фактичний досвід', blank=True)
    confidentiality_note = models.TextField('Принцип конфіденційності', blank=True)
    legal_provider_details = models.TextField('Реквізити надавача платних послуг', blank=True)
    expert_photo = models.ImageField('Фото експерта', upload_to='expert/', blank=True, null=True)

    class Meta:
        verbose_name = 'Налаштування сайту'
        verbose_name_plural = 'Налаштування сайту'

    def __str__(self):
        return 'Налаштування сайту'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class NewsletterSubscriber(models.Model):
    contact = models.CharField('Email або Telegram', max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Підписник розсилки'
        verbose_name_plural = 'Підписники розсилки'

    def __str__(self):
        return self.contact
