from django import forms
from django.core.validators import EmailValidator, URLValidator
from django.core.exceptions import ValidationError
from .models import NewsletterSubscriber


class SubscribeForm(forms.ModelForm):
    """Форма підписки з мінімальною серверною валідацією контакту.

    Дозволяємо email, URL (telegram/viber) або короткий телеграм-нікнейм, що починається з @.
    JavaScript робить клієнтську валідацію, але серверна — обов'язкова для надійності.
    """

    class Meta:
        model = NewsletterSubscriber
        fields = ['contact']
        widgets = {
            'contact': forms.TextInput(attrs={'placeholder': 'Email або Telegram'}),
        }

    def clean_contact(self):
        v = self.cleaned_data.get('contact', '').strip()
        if not v:
            raise ValidationError('Контакт не може бути порожнім')

        # спробуємо розпізнати email
        email_validator = EmailValidator()
        try:
            email_validator(v)
            return v
        except ValidationError:
            pass

        # або URL (посилання на telegram/viber)
        url_validator = URLValidator()
        try:
            url_validator(v)
            return v
        except ValidationError:
            pass

        # або telegram-нікнейм виду @username (короткий, без пробілів)
        if v.startswith('@') and ' ' not in v and len(v) <= 64:
            return v

        # якщо не email, не URL і не @nickname — формат некоректний
        raise ValidationError('Вкажіть email, посилання або Telegram-нік у форматі @nickname')
