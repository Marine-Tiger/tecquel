import warnings
import json
from pathlib import Path

from get_similarity import get_simil, sim_by_file

results_file = Path("results_RCFv7.json")

warnings.filterwarnings('ignore')

path_ref = "/home/marine/Documents/HTR/tecquel/REF/R124_a"
path_hyp1 = "/home/marine/Documents/HTR/tecquel/HYP/RCF/RCFv7_1763-1773"

#le paramètre all_metrics peut être à False pour limiter le nombre de mesures calculées

res = sim_by_file([path_ref, path_hyp1], all_metrics=True)

print(json.dumps(res, indent =2))

if results_file.exists():
    with results_file.open(mode="r", encoding="utf-8") as f:
        old_res = json.load(f)
else:
    #with results_file.open('w') as f:
    old_res = []

old_res.append(res)

#with results_file.open(mode="w", encoding="utf-8") as f:
with open(results_file, 'w', encoding="utf-8") as f:
    json.dump(old_res, f, indent=4, ensure_ascii=False)

