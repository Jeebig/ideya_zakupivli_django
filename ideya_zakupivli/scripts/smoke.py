import os
import sys
import json
from pathlib import Path

# Если скрипт запускают как `python scripts/smoke.py`, добавим корень проекта в sys.path
proj_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(proj_root))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.test import Client

c = Client()
urls = [
    '/',
    '/zamovnykam/',
    '/uchasnykam/',
    '/poslugy/',
    '/rozyasnennya/',
    '/novyny/',
    '/faq/',
    '/kontakty/',
]
results = {}
for u in urls:
    r = c.get(u)
    results[u] = {
        'status': r.status_code,
        'length': len(r.content),
    }

print(json.dumps(results, ensure_ascii=False, indent=2))
