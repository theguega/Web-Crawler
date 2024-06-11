import pandas as pd
df = pd.read_csv('../graph/datas.csv')
statistiques = df.describe()
print(statistiques)