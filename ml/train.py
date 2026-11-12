import csv,random,math,joblib
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
random.seed(42)
rows=[]
for day_index in range(70):
 day=day_index%7
 for hour in range(24):
  meal=750 if 12<=hour<=14 or 19<=hour<=22 else 120
  weekend=1.25 if day>=5 else 1
  target=max(10,round(meal*weekend+random.gauss(0,70)))
  previous=max(10,round(target*random.uniform(.7,1.1)))
  current=max(10,round(target*random.uniform(.8,1.2)))
  rows.append(([hour,day,previous,current],target))
cut=int(len(rows)*.8);train,test=rows[:cut],rows[cut:]
model=RandomForestRegressor(n_estimators=80,max_depth=10,random_state=42)
model.fit([r[0] for r in train],[r[1] for r in train])
print('Synthetic holdout MAE:',round(mean_absolute_error([r[1] for r in test],model.predict([r[0] for r in test])),2))
joblib.dump(model,Path(__file__).resolve().parent.parent/'backend'/'model.joblib')
print('Model saved to backend/model.joblib')
