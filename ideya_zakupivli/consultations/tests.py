from django.test import TestCase, override_settings
from django.test.client import MULTIPART_CONTENT
from django.utils.datastructures import MultiValueDict
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from .forms import ConsultationRequestForm
from .models import ConsultationRequest


class ConsultationRequestTests(TestCase):
    def test_short_message_is_rejected(self):
        form = ConsultationRequestForm(data={
            'name': 'Олена',
            'contact': 'olena@example.com',
            'message': '?',
            'consent': True,
        })

        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

    def test_subscribe_endpoint_only_accepts_post(self):
        response = self.client.get(reverse('core:subscribe'))

        self.assertEqual(response.status_code, 405)

    def test_form_rejects_honeypot(self):
        form = ConsultationRequestForm(data={
            'name': 'Олена',
            'contact': 'olena@example.com',
            'message': 'Достатньо довгий опис ситуації для перевірки.',
            'consent': True,
            'website': 'https://spam.example',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('website', form.errors)

    def test_form_rejects_unsupported_attachment(self):
        form = ConsultationRequestForm(
            data={
                'name': 'Олена',
                'contact': 'olena@example.com',
                'message': 'Достатньо довгий опис ситуації для перевірки.',
                'consent': True,
            },
            files={'attachments': [SimpleUploadedFile('script.exe', b'bad')]},
        )

        self.assertFalse(form.is_valid())
        self.assertIn('attachments', form.errors)

    @override_settings(ADMIN_NOTIFICATION_EMAIL='')
    def test_valid_submission_creates_request_number_and_attachment(self):
        response = self.client.post(
            reverse('consultations:contacts'),
            data={
                'name': 'Олена',
                'audience': 'zamovnyk',
                'contact': 'olena@example.com',
                'response_method': 'email',
                'message': 'Достатньо довгий опис ситуації для перевірки.',
                'consent': True,
            },
            content_type=MULTIPART_CONTENT,
        )

        request_obj = ConsultationRequest.objects.get()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(request_obj.request_number.startswith('IDEYA-'))
        self.assertEqual(request_obj.attachments.count(), 0)

    def test_form_accepts_supported_attachment(self):
        form = ConsultationRequestForm(
            data={
                'name': 'Олена',
                'audience': 'zamovnyk',
                'contact': 'olena@example.com',
                'response_method': 'email',
                'message': 'Достатньо довгий опис ситуації для перевірки.',
                'consent': True,
            },
            files=MultiValueDict({
                'attachments': [SimpleUploadedFile('brief.pdf', b'%PDF-test')],
            }),
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(len(form.cleaned_data['attachments']), 1)