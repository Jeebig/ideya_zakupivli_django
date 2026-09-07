from django.test import TestCase
from django.urls import reverse

from .forms import ConsultationRequestForm


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