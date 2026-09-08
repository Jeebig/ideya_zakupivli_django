from django.contrib import admin
from .models import ConsultationRequest, ConsultationAttachment


class ConsultationAttachmentInline(admin.TabularInline):
    model = ConsultationAttachment
    extra = 0
    readonly_fields = ('uploaded_at', 'file')


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ('request_number', 'name', 'audience', 'response_method', 'topic', 'contact', 'created_at', 'is_processed')
    list_filter = ('is_processed', 'created_at')
    search_fields = ('name', 'contact', 'topic', 'message')
    readonly_fields = ('created_at',)
    inlines = (ConsultationAttachmentInline,)


@admin.register(ConsultationAttachment)
class ConsultationAttachmentAdmin(admin.ModelAdmin):
    list_display = ('request', 'file', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
