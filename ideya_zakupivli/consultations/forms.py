from django import forms
from .models import ConsultationRequest


class ConsultationRequestForm(forms.ModelForm):
    class Meta:
        model = ConsultationRequest
        fields = ['name', 'contact', 'topic', 'tender_link', 'message', 'consent']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': "Ваше ім'я"}),
            'contact': forms.TextInput(attrs={'placeholder': 'Email, телефон або Telegram'}),
            'topic': forms.TextInput(attrs={'placeholder': 'Наприклад: перевірка тендерної документації'}),
            'tender_link': forms.URLInput(attrs={'placeholder': 'https://prozorro.gov.ua/tender/...'}),
            'message': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Опишіть вашу ситуацію якомога детальніше'}),
        }
        labels = {
            'tender_link': 'Посилання на закупівлю (Prozorro), якщо є',
        }

    def clean_consent(self):
        consent = self.cleaned_data.get('consent')
        if not consent:
            raise forms.ValidationError('Потрібна згода на обробку персональних даних.')
        return consent
