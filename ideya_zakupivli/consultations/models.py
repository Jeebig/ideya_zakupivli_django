from django.db import models


class ConsultationRequest(models.Model):
    AUDIENCE_CHOICES = [('zamovnyk', 'Я — замовник'), ('uchasnyk', 'Я — учасник')]
    name = models.CharField("Ім'я", max_length=150)
    audience = models.CharField('Аудиторія', max_length=20, choices=AUDIENCE_CHOICES, default='zamovnyk')
    contact = models.CharField('Контакт (email/телефон/telegram)', max_length=200)
    help_type = models.CharField('Вид допомоги', max_length=200, blank=True)
    deadline = models.DateField('Крайній строк', null=True, blank=True)
    topic = models.CharField('Тема звернення', max_length=255, blank=True)
    tender_link = models.URLField('Посилання на закупівлю (Prozorro)', blank=True)
    message = models.TextField('Опис ситуації')
    consent = models.BooleanField('Згода на обробку персональних даних', default=False)
    urgent = models.BooleanField('Терміново', default=False)
    request_number = models.CharField('Номер звернення', max_length=30, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField('Опрацьовано', default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Звернення'
        verbose_name_plural = 'Звернення'

    def __str__(self):
        return f'{self.name} — {self.topic or "без теми"} ({self.created_at:%d.%m.%Y})'

    def save(self, *args, **kwargs):
        if not self.request_number:
            from uuid import uuid4
            self.request_number = f'IDEYA-{uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)


class ConsultationAttachment(models.Model):
    request = models.ForeignKey(ConsultationRequest, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField('Файл', upload_to='consultations/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
