from locust import HttpUser,task,between
class KitchenUser(HttpUser):
 wait_time=between(.1,1)
 @task
 def order(self):self.client.post('/order',json={'items':2})
