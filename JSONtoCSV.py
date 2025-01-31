import json
import csv
import pandas as pd

with open('./RESULTS/results.json', encoding='utf-8') as inputfile:
    df = pd.read_json(inputfile)

df.to_csv('./RESULTS/results.csv', encoding='utf-8', index=False)
