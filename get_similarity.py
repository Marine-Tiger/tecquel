import sys
import glob
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import pairwise_distances
import os
from pathlib import PurePath
import json
import pywer

def open_file(path):
  with open(path, encoding="utf-8") as f:
    content = f.read()
  return content

def process_by_source(path_sources):
  print(f"path_sources : {path_sources}")
  for source in glob.glob(f"{path_sources}/*"):
    print(source)
    path_ref = f"{source}/REF/TXT/"
    path_hyp = f"{source}/HYP/*"
    print(source)
    print(f"  Processing {path_ref} as reference path")
    print(f"  Processing {path_hyp} as hypothesis path")
    res = process_data(path_hyp, path_ref, by_source = True)
    #print(json.dumps(res, indent =2))
    
def get_simil(corpus, names = []):
  if len(names)<len(corpus)-1:
    names = [x for x in range(len(corpus)-1)]
  vectorizer = CountVectorizer(analyzer ="word", ngram_range=(1,2))
  X = vectorizer.fit_transform(corpus)
  array = X.toarray()
  simil = cosine_similarity(array)[0][1:]
  dic = {"cosine": {names[i]:simil[i] for i in range(len(names))}}
  for metric in ["dice", "jaccard", "braycurtis"]:
    simil = pairwise_distances(array, metric=metric)[0][1:]
    dic[metric] =  {names[i]:1-simil[i] for i in range(len(names))}
  for hypo, name in zip(corpus[1:], names):
    for metric, res in [["WER", pywer.wer([hypo], [corpus[0]])],
                        ["CER", pywer.cer(hypo, corpus[0])],
]:
      dic.setdefault(metric, {})
      dic[metric][name] = res
      print(metric, res)
  return dic 
#output 1: simil, output 2: similar syst.(closer together than to the ref)

def get_data(path_hyp, path_ref):
  all_hyp = glob.glob(f"{path_hyp}/*/*")
  all_ref = glob.glob(f"{path_ref}/*")
#  all_ref = [x for x in all_ref if "0005" 
  data = {PurePath(path).parts[-1]:{"ref": path, "hyp":[]} for path in all_ref}
  for path in all_hyp:
    filename = os.path.basename(path)
    if filename in data:
      data[filename]["hyp"].append(path)
  return data

def get_results(data, by_source = False):
  pos_hyp_name = -2#adapting directory structure
  if by_source==True:
      pos_hyp_name = -3
  results = {}
  for filename, dic in data.items():
    hyp_path = sorted([path for path in dic["hyp"]])
    hyp_names = [PurePath(path).parts[pos_hyp_name] for path in hyp_path]
    corpus = [open_file(dic["ref"])]
    corpus += [open_file(path) for path in hyp_path]
    dic_simil = get_simil(corpus, names=hyp_names)
    for metric, d in dic_simil.items():
      results.setdefault(metric, {})
      for name, res in d.items():
        results[metric].setdefault(name, [])
        results[metric][name].append(res)
  return results

def viz(results):
  
  import statistics as st
  dic_agreg = {}
  out = {}
  for metric, dic_syst in results.items():
    dic_agreg.setdefault(metric, {"mean":[]})
    for syst, l_res in dic_syst.items():
      dic_agreg[metric]["mean"].append([st.mean(l_res), syst])
    rev = True
    if metric in ["WER", "CER"]:
      rev = False
    out[metric+"_mean"] = sorted(dic_agreg[metric]["mean"], reverse=rev)
  return out

def process_data(path_hyp, path_ref, by_source= False):
  data = get_data(path_hyp, path_ref)
  results = get_results(data, by_source) 
  results_for_viz = viz(results) 
  os.makedirs("./RESULTS/", exist_ok = True)
  filename_out = "--".join(PurePath(path_ref).parts)
  filename_out = re.sub("C:..","",filename_out)
  path_out = f"./RESULTS/{filename_out}.json"
  with open(path_out, "w") as w:
    w.write(json.dumps(results_for_viz, indent=2))
  print(f"Output written : {path_out}")
  return results_for_viz

if __name__=="__main__":
  path_hyp = "dummy_data/cleaned/"
  path_ref = "dummy_data/reference/"
  if len(sys.argv)==3:
    path_hyp = sys.argv[1]
    path_ref = sys.argv[2]
  res = process_data(path_hyp, path_ref)

