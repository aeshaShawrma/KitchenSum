import argparse,random,time,concurrent.futures,requests
p=argparse.ArgumentParser();p.add_argument('--url',default='http://localhost:8000');p.add_argument('--rate',type=int,default=10,help='Requests per second');p.add_argument('--seconds',type=int,default=30);args=p.parse_args()
def send(_):
 try:return requests.post(args.url+'/order',json={'items':random.randint(1,5)},timeout=5).status_code
 except requests.RequestException:return 0
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as pool:
 results=[]
 for second in range(args.seconds):
  start=time.monotonic();results.extend(pool.map(send,range(args.rate)))
  time.sleep(max(0,1-(time.monotonic()-start)))
print('Sent:',len(results),'Successful:',results.count(200),'Failed:',len(results)-results.count(200))
