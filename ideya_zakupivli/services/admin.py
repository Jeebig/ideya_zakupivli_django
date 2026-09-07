from django.contrib import admin
from .models import Service, ConsultationService


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'audience', 'order')
    list_filter = ('audience', 'tags')
    search_fields = ('title', 'short_description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    ordering = ('audience', 'order')


@admin.register(ConsultationService)
class ConsultationServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'service_type', 'order')
    list_filter = ('service_type',)
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('service_type', 'order')
