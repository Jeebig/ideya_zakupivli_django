from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from .forms import ConsultationRequestForm


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
        form.save()
        return super().form_valid(form)


class ThanksView(TemplateView):
    template_name = 'consultations/thanks.html'
