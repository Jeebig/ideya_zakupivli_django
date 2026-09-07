from .models import SiteSettings
from services.models import Service


def site_globals(request):
    """Дані, потрібні на кожній сторінці: контакти сайту і сервіси для mega-menu в header."""
    return {
        'site_settings': SiteSettings.load(),
        'nav_customer_services': Service.objects.filter(audience=Service.ZAMOVNYKAM)[:7],
        'nav_participant_services': Service.objects.filter(audience=Service.UCHASNYKAM)[:6],
    }
