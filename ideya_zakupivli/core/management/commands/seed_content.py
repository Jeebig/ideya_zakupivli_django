from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from datetime import date

from content.models import Tag, Article, FAQItem, OfficialExplanation
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

PRACTICAL_ARTICLES = [
    ('Як замовнику перевірити вимоги до учасника', 'zamovnykam', 'Відкриті торги з особливостями', 'Чекліст перевірки вимог без зайвого обмеження конкуренції.'),
    ('Що робити після моніторингу ДАСУ', 'zamovnykam', 'Моніторинг ДАСУ', 'Алгоритм підготовки пояснень і документів на запит контролюючого органу.'),
    ('Як підготувати вимогу замовнику', 'uchasnykam', 'Оскарження до АМКУ', 'Практична структура вимоги про усунення порушення.'),
    ('Коли подавати скаргу до АМКУ', 'uchasnykam', 'Оскарження до АМКУ', 'Що перевірити до оплати та подання скарги.'),
    ('Зміна договору через коливання ціни', 'zamovnykam', 'Укладення та зміна договорів', 'Документи й межі зміни істотних умов договору.'),
    ('Аналіз ціни у будівельній закупівлі', 'zamovnykam', 'Будівництво й аналіз цін', 'Як оформити обґрунтування очікуваної вартості.'),
    ('Пункт 13 Постанови №1178: практичний алгоритм', 'zamovnykam', 'Закупівлі за пунктом 13 Постанови №1178', 'Коли можливе укладення договору без відкритих торгів.'),
    ('Формальна помилка у пропозиції учасника', 'uchasnykam', 'Відкриті торги з особливостями', 'Як оцінити помилку та підготувати пояснення.'),
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
        Service.objects.all().update(
            client_provides='Опис ситуації, наявні документи та посилання на закупівлю.',
            result_format='Письмовий висновок, алгоритм дій і готове формулювання.',
            duration='2–5 робочих днів',
            price='Вартість після оцінки завдання',
            urgent_available=True,
            not_included='Представництво без окремого погодження та гарантування рішення контролюючого органу.',
            cta_label='Описати ситуацію',
        )
        self.stdout.write(self.style.SUCCESS('Послуги Замовникам/Учасникам створено.'))

        for i, (title, stype, desc) in enumerate(CONSULTATION_SERVICES):
            ConsultationService.objects.get_or_create(
                slug=slugify(title, allow_unicode=True),
                defaults=dict(title=title, service_type=stype, description=desc, order=i),
            )
        ConsultationService.objects.all().update(
            problem='Потрібна конкретна відповідь або перевірка документів у стислі строки.',
            client_provides='Опис ситуації та документи, які потрібно проаналізувати.',
            result_format='Письмова відповідь або пакет підготовлених документів.',
            duration='Від 1 робочого дня',
            price='Від 1500 грн після оцінки обсягу',
            urgent_available=True,
            not_included='Оплата державних зборів і представництво, якщо це не погоджено окремо.',
            cta_label='Описати ситуацію',
        )
        self.stdout.write(self.style.SUCCESS('Послуги та консультації створено.'))

        art1, created = Article.objects.get_or_create(
            slug='24-hod-vypravlennya-dokumentu',
            defaults=dict(
                article_type=Article.CLARIFICATION,
                title='Чи можна виправити документ протягом 24 годин',
                audience='uchasnykam',
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
        Article.objects.filter(pk=art1.pk).update(
            is_published=True,
            published_at=timezone.now(),
            legal_basis_reference='пункт 43 Особливостей, затверджених постановою КМУ № 1178',
            source_url='https://zakon.rada.gov.ua/laws/show/1178-2022-%D0%BF#Text',
            current_as_of=date.today(),
            exceptions_risks='Правило не застосовується до всіх невідповідностей. Перевірте перелік винятків і строк, зазначений у повідомленні замовника.',
            author='ІдеЯ у закупівлях',
        )

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
        Article.objects.filter(pk=art2.pk).update(
            is_published=True,
            published_at=timezone.now(),
            legal_basis_reference='пункт 19 Особливостей, затверджених постановою КМУ № 1178',
            source_url='https://zakon.rada.gov.ua/laws/show/1178-2022-%D0%BF#Text',
            current_as_of=date.today(),
            exceptions_risks='Не кожне коливання ціни є підставою для зміни договору. Потрібні документальне обґрунтування та дотримання встановлених меж.',
            author='ІдеЯ у закупівлях',
        )

        art1.related_articles.add(art2)

        practical_articles = []
        for index, (title, audience, tag_name, summary) in enumerate(PRACTICAL_ARTICLES, start=1):
            article, _ = Article.objects.update_or_create(
                slug=slugify(title, allow_unicode=True),
                defaults=dict(
                    article_type=Article.CLARIFICATION,
                    title=title,
                    audience=audience,
                    summary=summary,
                    short_answer=f'У ситуації «{title.lower()}» дійте за перевіреним алгоритмом і фіксуйте кожен крок у документах закупівлі.',
                    legal_basis='Застосовуйте чинні норми Закону України «Про публічні закупівлі» та Особливостей, затверджених постановою КМУ № 1178.',
                    legal_basis_reference='Відповідний пункт Закону або постанови № 1178 перевіряється за чинною редакцією.',
                    source_url='https://zakon.rada.gov.ua/laws/show/922-19#Text',
                    current_as_of=date.today(),
                    exceptions_risks='Остаточний висновок залежить від документів, строків і конкретних умов закупівлі.',
                    action_algorithm='1. Зафіксувати фактичні обставини.\n2. Перевірити строк і нормативну підставу.\n3. Підготувати документ із посиланнями.\n4. Оприлюднити або подати його у встановлений строк.',
                    wording='«На виконання вимог законодавства та з урахуванням обставин закупівлі повідомляємо: ...»',
                    author='ІдеЯ у закупівлях',
                    template_url='https://zakon.rada.gov.ua/laws/show/922-19#Text',
                    is_published=True,
                    is_featured=True,
                    published_at=timezone.now(),
                ),
            )
            article.tags.set([tags[tag_name]])
            practical_articles.append(article)
        art1.related_articles.add(*practical_articles[:3])
        self.stdout.write(self.style.SUCCESS(f'Повноцінних практичних матеріалів: {len(practical_articles) + 2}'))

        official, _ = OfficialExplanation.objects.update_or_create(
            document_number='№ 3304-04/12345-06',
            defaults=dict(
                document_type=OfficialExplanation.RESOLUTION,
                status=OfficialExplanation.CURRENT,
                document_date=date(2025, 2, 14),
                title='Щодо застосування Особливостей здійснення публічних закупівель',
                summary='Демонстраційний запис офіційного роз’яснення: перевірте порядок застосування норм постанови № 1178 та актуальність позиції за першоджерелом.',
                source_page_url='https://www.me.gov.ua/InfoRez/DocumentsList?lang=uk-UA',
                source_file_url='https://www.me.gov.ua/InfoRez/DocumentsList?lang=uk-UA',
                current_text_url='https://zakon.rada.gov.ua/laws/show/1178-2022-%D0%BF#Text',
                keywords='публічні закупівлі, постанова 1178, відкриті торги, замовник',
                checked_at=date.today(),
                is_current=True,
                practical_comment=art1,
            ),
        )
        official.tags.set([tags['Відкриті торги з особливостями'], tags['Моніторинг ДАСУ']])
        self.stdout.write(self.style.SUCCESS('Офіційні роз’яснення Мінекономіки створено/оновлено.'))

        news1, _ = Article.objects.get_or_create(
            slug='zminy-postanova-1178',
            defaults=dict(
                article_type=Article.NEWS,
                title='Оновлено порядок закупівель за пунктом 13 Постанови №1178',
                audience='zamovnykam',
                summary='Короткий огляд змін і що це означає на практиці.',
                body='Внесено зміни до порядку здійснення закупівель. Детальний алгоритм дій — у відповідному роз\'ясненні.',
            ),
        )
        news1.tags.add(tags["Закупівлі за пунктом 13 Постанови №1178"])
        Article.objects.filter(pk=news1.pk).update(
            is_published=True,
            published_at=timezone.now(),
            changes_document='Постанова Кабінету Міністрів України № 1178 та наступні зміни до неї.',
            effective_from=date.today(),
            what_to_do='Перевірити чинну редакцію постанови, оновити внутрішній чекліст і зафіксувати підставу обраного способу закупівлі.',
        )

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
                    audience='uchasnykam' if question == 'Чи можна виправити документ протягом 24 годин' else 'zamovnykam', is_popular=True, order=i,
                    related_article=art_by_faq.get(question),
                ),
            )
            faq = FAQItem.objects.get(question=question)
            faq.audience = (
                'uchasnykam'
                if question in {
                    'Чи можна виправити документ протягом 24 годин',
                    'Коли пропозицію потрібно відхилити',
                }
                else 'zamovnykam'
            )
            faq.save(update_fields=['audience'])
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
            settings_obj.expert_name = 'Команда ІдеЯ'
            settings_obj.expert_specialization = 'Публічні закупівлі для замовників та учасників'
            settings_obj.expert_education = 'Профільна юридична освіта та постійне навчання у сфері закупівель.'
            settings_obj.expert_experience = 'Практика підготовки тендерної документації, відповідей ДАСУ, вимог і скарг до АМКУ.'
            settings_obj.confidentiality_note = 'Документи та обставини звернення використовуються лише для підготовки погодженого результату.'
            settings_obj.legal_provider_details = 'Реквізити надавача платних послуг заповнюються власником сайту перед запуском оплати.'
            settings_obj.save()
        else:
            changed = False
            profile_defaults = {
                'expert_name': 'Команда ІдеЯ',
                'expert_specialization': 'Публічні закупівлі для замовників та учасників',
                'expert_education': 'Профільна юридична освіта та постійне навчання у сфері закупівель.',
                'expert_experience': 'Практика підготовки тендерної документації, відповідей ДАСУ, вимог і скарг до АМКУ.',
                'confidentiality_note': 'Документи та обставини звернення використовуються лише для підготовки погодженого результату.',
                'legal_provider_details': 'Реквізити надавача платних послуг заповнюються власником сайту перед запуском оплати.',
            }
            for field, value in profile_defaults.items():
                if not getattr(settings_obj, field) or (
                    field == 'expert_name' and getattr(settings_obj, field) == 'Ім’я та прізвище експерта'
                ):
                    setattr(settings_obj, field, value)
                    changed = True
            if changed:
                settings_obj.save()
        self.stdout.write(self.style.SUCCESS('Налаштування сайту оновлено.'))

        self.stdout.write(self.style.SUCCESS('Готово! Демо-контент завантажено.'))
