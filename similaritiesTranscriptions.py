import warnings
import json
from pathlib import Path

from get_similarity import get_simil, sim_by_file

results_file = Path("results_comparaison_R52_1_50p.json")

warnings.filterwarnings('ignore')

path_ref = "/home/marine/Documents/HTR/tecquel/REF/R52_1_GT_50p.txt"
hyp_files=["/home/marine/Documents/HTR/tecquel/HYP/Mcfondue/Mcfondue",
           "/home/marine/Documents/HTR/tecquel/HYP/MCFR/Mcfrench",
           "/home/marine/Documents/HTR/tecquel/HYP/RCF/RCF_FT_eScriptorium",
           "/home/marine/Documents/HTR/tecquel/HYP/FT_331p/model_331p",
           "/home/marine/Documents/HTR/tecquel/HYP/FT_MCF_431p/model_431p",
           "/home/marine/Documents/HTR/tecquel/HYP/Postcorrection"
           ]

#le paramètre all_metrics peut être à False pour limiter le nombre de mesures calculées

res = sim_by_file([path_ref] + hyp_files, all_metrics=True)

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

