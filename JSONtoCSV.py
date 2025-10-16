import json
import csv
import pandas as pd

with open('results_comparaison_3models.json', encoding='utf-8') as inputfile:
    df = pd.read_json(inputfile)

df.to_csv('results_comparaison_R52-R124.csv', encoding='utf-8', index=False)
