from django.views.generic import FormView, TemplateView
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from .forms import ConsultationRequestForm
from .models import ConsultationAttachment


class ContactsView(FormView):
    template_name = 'core/contacts.html'
    form_class = ConsultationRequestForm
    success_url = reverse_lazy('consultations:thanks')

    def get_initial(self):
        initial = super().get_initial()
        topic = self.request.GET.get('topic')
        if topic:
            initial['topic'] = topic
        return initial

    def form_valid(self, form):
        with transaction.atomic():
            request_obj = form.save()
            for uploaded in form.cleaned_data.get('attachments', []):
                ConsultationAttachment.objects.create(request=request_obj, file=uploaded)
        if settings.ADMIN_NOTIFICATION_EMAIL:
            attachments = request_obj.attachments.count()
            send_mail(
                f'Нове звернення {request_obj.request_number}',
                f'Ім’я: {request_obj.name}\nКонтакт: {request_obj.contact}\nСпосіб відповіді: {request_obj.get_response_method_display()}\nТерміново: {"так" if request_obj.urgent else "ні"}\nВкладень: {attachments}\nОпис: {request_obj.message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_NOTIFICATION_EMAIL],
                fail_silently=True,
            )
        return redirect(f'{reverse("consultations:thanks")}?number={request_obj.request_number}')


class ThanksView(TemplateView):
    template_name = 'consultations/thanks.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['request_number'] = self.request.GET.get('number', '')
        return ctx
