import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from fastapi.testclient import TestClient
from dna.api.app import app

client = TestClient(app)

endpoints = [
    '/',
    '/health',
    '/status',
    '/v1/analyze',
    '/v1/entities',
    '/v1/evidence',
    '/v1/insights'
]

for ep in endpoints:
    resp = client.get(ep)
    print(f'{ep}: {resp.status_code}')
