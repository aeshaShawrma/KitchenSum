import os, time
from fastapi import APIRouter, HTTPException
router=APIRouter()
LAST={'replicas':1,'timestamp':0}
@router.post('/scale/{replicas}')
def scale(replicas:int):
 if replicas<1 or replicas>8:raise HTTPException(400,'Replicas must be between 1 and 8')
 if os.getenv('ENABLE_SCALING','false').lower()!='true':
  return {'mode':'dry-run','recommended_replicas':replicas,'applied':False}
 if time.time()-LAST['timestamp']<30:raise HTTPException(429,'Scaling cooldown active')
 try:
  from kubernetes import client,config
  try:config.load_incluster_config()
  except config.ConfigException:config.load_kube_config()
  ns=os.getenv('K8S_NAMESPACE','default')
  client.AppsV1Api().patch_namespaced_deployment_scale('kitchensum-api',ns,{'spec':{'replicas':replicas}})
  LAST.update(replicas=replicas,timestamp=time.time())
  return {'mode':'kubernetes','replicas':replicas,'applied':True}
 except Exception as exc:raise HTTPException(503,f'Scaling unavailable: {type(exc).__name__}')
