from fastapi.testclient import TestClient
from backend.main import app
client=TestClient(app)
def test_health():assert client.get('/health').status_code==200
def test_order():assert client.post('/order',json={'items':2}).json()['accepted']
def test_bad_order():assert client.post('/order',json={'items':0}).status_code==422
def test_prediction():assert client.get('/prediction?current=500&previous=300').json()['recommended_replicas']>=1
def test_safe_scaling():assert client.post('/scale/3').json()['applied'] is False
