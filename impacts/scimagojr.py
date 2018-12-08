import pandas as pd
import os

df = pd.read_csv(os.path.join('impacts', 'data', 'scimagojr_2017.csv'), delimiter=';')

df.head()
df.query("'Psychological Science' in Title ")
