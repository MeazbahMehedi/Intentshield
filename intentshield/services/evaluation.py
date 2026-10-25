"""Reproducible evaluation, overlap audit and grouped metrics."""
import hashlib
import json
import re
import time
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from intentshield.services.engine import LayeredEngine, version
from intentshield.services.metrics import calculate_metrics
from intentshield.services.normalization import language
from intentshield.services.policy import DEFAULTS
from intentshield.services.semantic import classify

DATA = Path(__file__).resolve().parents[1]/'data'
SPLITS = ('development','holdout','robustness','test')


def load(split):
    if split not in SPLITS:
        raise ValueError('Unknown dataset split.')
    raw = (DATA/(split+'_cases.json')).read_bytes()
    rows = json.loads(raw)
    ids = set()
    for x in rows:
        if not isinstance(x,dict) or not isinstance(x.get('prompt'),str) or not x['prompt'].strip() or len(x['prompt'])>10000 or x.get('expected_label') not in ('attack','safe') or x.get('id') in ids:
            raise ValueError('Invalid dataset schema or duplicate ID.')
        ids.add(x['id'])
    return rows,hashlib.sha256(raw).hexdigest()


def canonical(text):
    from intentshield.detectors.base import normalize_text
    return re.sub(r'\s+',' ',normalize_text(text)).strip()


@lru_cache(maxsize=1)
def dataset_audit():
    datasets = {s:load(s)[0] for s in SPLITS}
    exact = []; near = []; internal = {}
    for split,rows in datasets.items():
        internal[split] = len(rows)-len({canonical(x['prompt']) for x in rows})
    # Main/test is the same corpus as combined, intentionally not counted twice.
    for target in ('development','holdout','robustness'):
        refs = datasets['test'] + (datasets['development'] if target!='development' else [])
        exact_map = {canonical(x['prompt']):x['id'] for x in refs}
        ref_tokens = [(x['id'],set(re.findall(r'\w+',canonical(x['prompt'])))) for x in refs]
        for row in datasets[target]:
            text = canonical(row['prompt'])
            if text in exact_map:
                exact.append({'split':target,'id':row['id'],'matches':exact_map[text]}); continue
            tokens = set(re.findall(r'\w+',text))
            best = (0,None)
            for rid, rt in ref_tokens:
                score = len(tokens&rt)/len(tokens|rt) if tokens|rt else 0
                if score > best[0]: best=(score,rid)
            if best[0]>=0.85:
                near.append({'split':target,'id':row['id'],'matches':best[1],'jaccard':round(best[0],3)})
    return {'internal_duplicates':internal, 'cross_split_exact':exact, 'near_duplicates':near, 'near_method':'Word-set Jaccard >= 0.85; candidates require human review.', 'alias':'combined_cases.json equals test_cases.json; count once.', 'limitations':'Existing holdout is synthetic and previously exposed; filtered results are not proof of unseen real-world performance.'}


def metrics(rows):
    if not rows: return {'total':0}
    result = calculate_metrics([x['expected'] for x in rows],[x['predicted'] for x in rows])
    fp,tn,fn,tp = [result[k] for k in ('false_positive','true_negative','false_negative','true_positive')]
    result['false_positive_rate'] = round(fp/(fp+tn),4) if fp+tn else 0
    result['false_negative_rate'] = round(fn/(fn+tp),4) if fn+tp else 0
    return result


def evaluate(split='holdout',mode='hybrid',clean=True):
    if mode not in ('rules','hybrid','ml'): raise ValueError('Invalid detector mode.')
    rows,digest = load(split)
    audit = dataset_audit()
    contaminated = {x['id'] for x in audit['cross_split_exact']+audit['near_duplicates'] if x['split']==split} if split!='test' else set()
    # ML sees development examples; disallow reporting this as held-out performance.
    engine = LayeredEngine(); details=[]; started=time.perf_counter()
    for row in rows:
        if clean and row['id'] in contaminated: continue
        if mode=='ml':
            start=time.perf_counter(); ml=classify(row['prompt'])
            if not ml['available']:raise ValueError('ML mode requires requirements-ml.txt.')
            latency=round((time.perf_counter()-start)*1000,2)
            positive=ml['score']>=65
        else:
            policy = {**DEFAULTS,'ml_enabled':mode=='hybrid'}
            result = engine.analyze(row['prompt'],policy=policy,mode='rules' if mode=='rules' else 'hybrid')
            ml=result['ml']; latency=result['latency_ms']
            positive = result['injection_score']>=25 or result['harmful_content']['detected'] or result['sensitive_data']['detected'] or (ml.get('available') and ml['score']>=65)
        predicted = 'attack' if positive else 'safe'
        details.append({'id':row['id'],'category':row.get('category','unknown'),'language':language(row['prompt']),'expected':row['expected_label'],'predicted':predicted,'correct':predicted==row['expected_label'],'latency_ms':latency})
    grouped={}
    for field in ('category','language'):
        buckets=defaultdict(list)
        for row in details:buckets[row[field]].append(row)
        grouped[field]={name:metrics(bucket) for name,bucket in buckets.items()}
    elapsed=(time.perf_counter()-started)*1000
    return {'split':split,'mode':mode,'clean':clean,'excluded_count':len(rows)-len(details),'metrics':metrics(details),'groups':grouped,'details':details,'dataset_hash':digest,'engine_version':version(),'elapsed_ms':round(elapsed,2),'mean_latency_ms':round(elapsed/len(details),2) if details else 0,'ml_training':'development only; lexical baseline, not semantic understanding','independent_test':False,'evaluation_role':split,'ml_metadata':ml if details else {},'prediction_thresholds':{'rules_score':25,'ml_score':65},'limitations':audit['limitations']}
