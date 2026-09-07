from django.core.management.base import BaseCommand
from django.utils.text import slugify

from content.models import Tag, Article, FAQItem
from services.models import Service, ConsultationService
from core.models import SiteSettings, CaseStudy


TAGS = [
    "Відкриті торги з особливостями",
    "Закупівлі за пунктом 13 Постанови №1178",
    "Спрощені та допорогові закупівлі",
    "Укладення та зміна договорів",
    "Будівництво й аналіз цін",
    "Страхові послуги",
    "Медичне обладнання",
    "Моніторинг ДАСУ",
    "Оскарження до АМКУ",
]

ZAMOVNYKAM_SERVICES = [
    ("Тендерна документація", "Розробка та перевірка тендерної документації без ризикованих формулювань."),
    ("Розгляд пропозицій та 24 години", "Порядок розгляду пропозицій і робота з правилом 24 годин на виправлення."),
    ("Протоколи УО", "Підготовка та перевірка протоколів уповноваженої особи."),
    ("Договори та додаткові угоди", "Укладення договорів і коректне оформлення додаткових угод."),
    ("Моніторинг ДАСУ", "Супровід під час моніторингу закупівлі Держаудитслужбою."),
    ("Будівництво, кошториси й аналіз цін", "Перевірка кошторисної документації та обґрунтування ціни у будівництві."),
    ("Супровід закупівлі", "Повний супровід закупівлі від оголошення до укладення договору."),
]

UCHASNYKAM_SERVICES = [
    ("Перевірка тендерної документації", "Аналіз документації замовника перед подачею пропозиції."),
    ("Підготовка пропозиції", "Формування пакету документів пропозиції відповідно до вимог."),
    ("Вимоги про усунення порушень", "Підготовка та подання вимог про усунення порушень."),
    ("Оскарження в АМКУ", "Підготовка скарги та супровід розгляду в АМКУ."),
    ("Аналіз відхилення", "Оцінка правомірності відхилення пропозиції та подальші дії."),
    ("Супровід виконання договору", "Супровід на етапі виконання укладеного договору."),
]

CONSULTATION_SERVICES = [
    ("Разова консультація", ConsultationService.ONE_TIME, "Письмова відповідь на конкретне питання."),
    ("Перевірка документа", ConsultationService.ONE_TIME, "Аналіз документа з переліком зауважень і ризиків."),
    ("Підготовка документа", ConsultationService.ONE_TIME, "Підготовка документа під конкретну ситуацію."),
    ("Комплексний супровід закупівлі", ConsultationService.ONGOING, "Повний супровід закупівлі від початку до завершення."),
    ("Супровід Замовника", ConsultationService.ONGOING, "Абонентське консультування замовника."),
    ("Супровід Учасника", ConsultationService.ONGOING, "Абонентське консультування учасника."),
]

FAQ_ITEMS = [
    ("Чи можна виправити документ протягом 24 годин", "Відкриті торги з особливостями"),
    ("Коли пропозицію потрібно відхилити", "Відкриті торги з особливостями"),
    ("Як змінити ціну договору", "Укладення та зміна договорів"),
    ("Які документи оприлюднюються разом із договором", "Укладення та зміна договорів"),
    ("Що робити після відміни торгів через відсутність пропозицій", "Спрощені та допорогові закупівлі"),
]

CASES = [
    ("Скарга в АМКУ на етапі розгляду", "Замовник отримав скаргу за день до засідання.",
     "Підготували пояснення з чіткою нормативною опорою.", "Скаргу відхилено, закупівлю збережено."),
    ("Відхилення пропозиції учасника", "Учасника відхилили через формальну помилку в документі.",
     "Проаналізували підстави відхилення та підготували вимогу про усунення порушення.",
     "Рішення про відхилення скасовано."),
    ("Зміна ціни договору під час будівництва", "Зросли ціни на матеріали, потрібно було коректно оформити зміну.",
     "Підготували обґрунтування та додаткову угоду відповідно до вимог законодавства.",
     "Зміну ціни погоджено без зауважень контролюючих органів."),
]


class Command(BaseCommand):
    help = 'Наповнює сайт демонстраційним контентом за структурою ТЗ.'

    def handle(self, *args, **options):
        tags = {}
        for name in TAGS:
            tag, _ = Tag.objects.get_or_create(name=name)
            tags[name] = tag
        self.stdout.write(self.style.SUCCESS(f'Тегів створено/знайдено: {len(tags)}'))

        for i, (title, desc) in enumerate(ZAMOVNYKAM_SERVICES):
            Service.objects.get_or_create(
                audience=Service.ZAMOVNYKAM, slug=slugify(title, allow_unicode=True),
                defaults=dict(
                    title=title, short_description=desc, order=i,
                    whats_included="Аналіз ситуації\nПідготовка документа/відповіді\nПеревірка на відповідність законодавству",
                    risks="Формальні помилки в документах\nПорушення строків\nНечіткі формулювання, що дають підставу для скарги",
                ),
            )
        for i, (title, desc) in enumerate(UCHASNYKAM_SERVICES):
            Service.objects.get_or_create(
                audience=Service.UCHASNYKAM, slug=slugify(title, allow_unicode=True),
                defaults=dict(
                    title=title, short_description=desc, order=i,
                    whats_included="Аналіз документації\nПеревірка відповідності вимогам\nРекомендації щодо усунення ризиків",
                    risks="Пропущений строк оскарження\nНеповний пакет документів\nНевідповідність кваліфікаційним вимогам",
                ),
            )
        self.stdout.write(self.style.SUCCESS('Послуги Замовникам/Учасникам створено.'))

        for i, (title, stype, desc) in enumerate(CONSULTATION_SERVICES):
            ConsultationService.objects.get_or_create(
                slug=slugify(title, allow_unicode=True),
                defaults=dict(title=title, service_type=stype, description=desc, order=i),
            )
        self.stdout.write(self.style.SUCCESS('Послуги та консультації створено.'))

        art1, created = Article.objects.get_or_create(
            slug='24-hod-vypravlennya-dokumentu',
            defaults=dict(
                article_type=Article.CLARIFICATION,
                title='Чи можна виправити документ протягом 24 годин',
                audience='both',
                summary='Коли і як застосовується правило 24 годин на виправлення документів у пропозиції.',
                short_answer='Так, у визначених законодавством випадках учасник може виправити невідповідність протягом 24 годин.',
                legal_basis='Відповідне положення Закону України "Про публічні закупівлі" щодо усунення невідповідностей.',
                action_algorithm='1. Отримати повідомлення від замовника.\n2. Підготувати виправлений документ.\n3. Завантажити його в systему протягом 24 годин.',
                wording='"На виконання повідомлення від [дата] надаємо виправлений документ: ..."',
                is_featured=True,
            ),
        )
        if created:
            art1.tags.add(tags["Відкриті торги з особливостями"])

        art2, created = Article.objects.get_or_create(
            slug='zmina-tsiny-dohovoru',
            defaults=dict(
                article_type=Article.CLARIFICATION,
                title='Як змінити ціну договору',
                audience='zamovnykam',
                summary="Підстави та порядок зміни ціни договору про закупівлю.",
                short_answer='Ціну договору можна змінити лише за наявності законних підстав і з дотриманням встановленого порядку.',
                legal_basis='Норми щодо істотних умов договору про закупівлю та підстав їх зміни.',
                action_algorithm='1. Перевірити наявність підстави для зміни ціни.\n2. Підготувати обґрунтування.\n3. Укласти додаткову угоду та оприлюднити її.',
                wording='"Сторони погодили зміну ціни договору у зв\'язку з ..."',
                is_featured=True,
            ),
        )
        if created:
            art2.tags.add(tags["Укладення та зміна договорів"], tags["Будівництво й аналіз цін"])

        news1, _ = Article.objects.get_or_create(
            slug='zminy-postanova-1178',
            defaults=dict(
                article_type=Article.NEWS,
                title='Оновлено порядок закупівель за пунктом 13 Постанови №1178',
                audience='both',
                summary='Короткий огляд змін і що це означає на практиці.',
                body='Внесено зміни до порядку здійснення закупівель. Детальний алгоритм дій — у відповідному роз\'ясненні.',
            ),
        )
        news1.tags.add(tags["Закупівлі за пунктом 13 Постанови №1178"])

        self.stdout.write(self.style.SUCCESS("Роз'яснення та новини створено."))

        art_by_faq = {
            "Чи можна виправити документ протягом 24 годин": art1,
            "Як змінити ціну договору": art2,
        }
        for i, (question, tag_name) in enumerate(FAQ_ITEMS):
            FAQItem.objects.get_or_create(
                question=question,
                defaults=dict(
                    answer='Коротка практична відповідь на це питання. Детальніше — у відповідному роз\'ясненні.',
                    audience='both', is_popular=True, order=i,
                    related_article=art_by_faq.get(question),
                ),
            )
            faq = FAQItem.objects.get(question=question)
            faq.tags.add(tags[tag_name])
        self.stdout.write(self.style.SUCCESS('FAQ створено.'))

        for i, (title, situation, action, result) in enumerate(CASES):
            CaseStudy.objects.get_or_create(
                title=title, defaults=dict(situation=situation, action=action, result=result, order=i),
            )
        self.stdout.write(self.style.SUCCESS('Кейси створено.'))

        settings_obj = SiteSettings.load()
        if not settings_obj.email:
            settings_obj.email = 'info@ideya-zakupivli.ua'
            settings_obj.phone = '+380 (00) 000-00-00'
            settings_obj.telegram = 'https://t.me/ideya_zakupivli'
            settings_obj.experience_years = '7+ років'
            settings_obj.save()
        self.stdout.write(self.style.SUCCESS('Налаштування сайту оновлено.'))

        self.stdout.write(self.style.SUCCESS('Готово! Демо-контент завантажено.'))
