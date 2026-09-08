from django.contrib import admin
from .models import ConsultationRequest, ConsultationAttachment


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'topic', 'contact', 'created_at', 'is_processed')
    list_filter = ('is_processed', 'created_at')
    search_fields = ('name', 'contact', 'topic', 'message')
    readonly_fields = ('created_at',)
