from django import forms
from .models import ConsultationRequest


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def clean(self, data, initial=None):
        if not data:
            return []
        clean_file = super().clean
        if isinstance(data, (list, tuple)):
            return [clean_file(item, initial) for item in data]
        return [clean_file(data, initial)]


class ConsultationRequestForm(forms.ModelForm):
    name = forms.CharField(label="Ім’я", min_length=2, max_length=150)
    attachments = MultipleFileField(
        label='Файли (DOCX, PDF, XLSX, ZIP)', required=False,
        widget=MultipleFileInput(attrs={'multiple': True}),
    )
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = ConsultationRequest
        fields = ['name', 'audience', 'help_type', 'deadline', 'contact', 'response_method', 'topic', 'tender_link', 'message', 'urgent', 'consent']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': "Ваше ім'я"}),
            'contact': forms.TextInput(attrs={'placeholder': 'Email, телефон або Telegram'}),
            'topic': forms.TextInput(attrs={'placeholder': 'Наприклад: перевірка тендерної документації'}),
            'tender_link': forms.URLInput(attrs={'placeholder': 'https://prozorro.gov.ua/tender/...'}),
            'message': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Опишіть вашу ситуацію якомога детальніше'}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'tender_link': 'Посилання на закупівлю (Prozorro), якщо є',
        }

    def clean_attachments(self):
        files = self.cleaned_data.get('attachments', [])
        if len(files) > 10:
            raise forms.ValidationError('Можна додати не більше 10 файлів.')
        allowed = {'.docx', '.pdf', '.xlsx', '.zip'}
        for uploaded in files:
            if not any(uploaded.name.lower().endswith(ext) for ext in allowed):
                raise forms.ValidationError('Дозволені файли DOCX, PDF, XLSX або ZIP.')
            if uploaded.size > 10 * 1024 * 1024:
                raise forms.ValidationError('Розмір одного файлу не може перевищувати 10 МБ.')
        return files

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Не вдалося надіслати звернення. Спробуйте ще раз.')
        return ''

    def clean_consent(self):
        consent = self.cleaned_data.get('consent')
        if not consent:
            raise forms.ValidationError('Потрібна згода на обробку персональних даних.')
        return consent

    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if len(message) < 10:
            raise forms.ValidationError('Опишіть ситуацію щонайменше у 10 символах.')
        return message
