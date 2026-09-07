from django.db import models


class ConsultationRequest(models.Model):
    name = models.CharField("Ім'я", max_length=150)
    contact = models.CharField('Контакт (email/телефон/telegram)', max_length=200)
    topic = models.CharField('Тема звернення', max_length=255, blank=True)
    tender_link = models.URLField('Посилання на закупівлю (Prozorro)', blank=True)
    message = models.TextField('Опис ситуації')
    consent = models.BooleanField('Згода на обробку персональних даних', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField('Опрацьовано', default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Звернення'
        verbose_name_plural = 'Звернення'

    def __str__(self):
        return f'{self.name} — {self.topic or "без теми"} ({self.created_at:%d.%m.%Y})'
