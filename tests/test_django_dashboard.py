import os
import sys
import django
from django.test import Client

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interfaces.django_dashboard.dashboard.settings')
django.setup()


def test_index_route():
    client = Client()
    resp = client.get('/')
    assert resp.status_code == 200
