import os, time, random, threading
from datetime import datetime, timezone
from collections import deque
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from pymongo import MongoClient

app=FastAPI(title="KitchenSum API")
app.add_middleware(CORSMiddleware,allow_origins=os.getenv('CORS_ORIGINS','http://localhost:5173').split(','),allow_methods=['*'],allow_headers=['*'])
client=None
try:
 if os.getenv('MONGO_URI'):
  client=MongoClient(os.getenv('MONGO_URI'),serverSelectionTimeoutMS=1500)
  client.admin.command('ping')
except Exception:
 client=None
memory=deque(maxlen=20000)
lock=threading.Lock()
requests=Counter('kitchensum_orders_total','Orders accepted')
latency=Histogram('kitchensum_order_processing_seconds','Order processing time')
class Order(BaseModel):
 items:int=Field(default=1,ge=1,le=30)
 zone:str='default'
@app.get('/health')
def health():return {'status':'ok','database':'mongodb' if client else 'in-memory'}
@app.post('/order')
def order(o:Order):
 start=time.perf_counter()
 # Adjustable simulated work makes response time measurable under load.
 time.sleep(float(os.getenv('PROCESSING_DELAY','0.02')))
 doc={'timestamp':datetime.now(timezone.utc).isoformat(),'items':o.items,'zone':o.zone}
 if client:
  try:client.kitchensum.orders.insert_one(dict(doc))
  except Exception:pass
 with lock:memory.append(doc)
 requests.inc();latency.observe(time.perf_counter()-start)
 return {'accepted':True,'order':doc}
@app.get('/stats')
def stats():
 with lock:
  orders=list(memory)
 now=datetime.now(timezone.utc).timestamp()
 minute=sum(1 for x in orders if datetime.fromisoformat(x['timestamp']).timestamp()>=now-60)
 return {'orders_last_minute':minute,'orders_in_local_buffer':len(orders),'timestamp':datetime.now(timezone.utc).isoformat()}
@app.get('/history')
def history():
 with lock:return list(memory)[-100:]
@app.get('/metrics')
def metrics():return Response(generate_latest(),media_type=CONTENT_TYPE_LATEST)
