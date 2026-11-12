import os, math, joblib
from datetime import datetime
from fastapi import APIRouter
router=APIRouter()
MODEL=os.getenv('MODEL_PATH','/app/model.joblib')
@router.get('/prediction')
def prediction(hour:int|None=None,day:int|None=None,previous:int=200,current:int=200):
 now=datetime.now();hour=now.hour if hour is None else hour;day=now.weekday() if day is None else day
 hour=max(0,min(23,hour));day=max(0,min(6,day));previous=max(0,previous);current=max(0,current)
 if os.path.exists(MODEL):
  model=joblib.load(MODEL)
  expected=max(0,round(float(model.predict([[hour,day,previous,current]])[0])))
  source='random-forest'
 else:
  expected=round(max(0,current*0.7+previous*0.3));source='baseline'
 capacity=max(1,int(os.getenv('CAPACITY_PER_REPLICA','400')))
 replicas=max(1,min(8,math.ceil(expected/capacity)))
 return {'predicted_requests_per_minute':expected,'recommended_replicas':replicas,'model':source,'capacity_per_replica':capacity}
