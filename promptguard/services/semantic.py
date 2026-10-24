"""Optional statistical text classifier, trained exclusively on development data.

Character TF-IDF + logistic regression is a lexical ML baseline, NOT an LLM or
an embedding-based semantic understanding system. Model probabilities are uncalibrated.
"""
import hashlib
import json
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'data'

@lru_cache(maxsize=1)
def model():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    raw = (DATA / 'development_cases.json').read_bytes()
    rows = json.loads(raw)
    pipeline = make_pipeline(TfidfVectorizer(analyzer='char_wb', ngram_range=(3,5), max_features=15000), LogisticRegression(class_weight='balanced', max_iter=400, random_state=42))
    pipeline.fit([x['prompt'] for x in rows], [x['expected_label'] for x in rows])
    return pipeline, hashlib.sha256(raw).hexdigest()[:16]


def classify(text):
    try:
        pipeline, fingerprint = model()
    except ImportError:
        return {'available':False, 'score':0, 'reason':'Install requirements-ml.txt to enable the lexical ML baseline.'}
    idx = list(pipeline.classes_).index('attack')
    score = round(float(pipeline.predict_proba([text])[0][idx])*100)
    return {'available':True, 'score':score, 'training_split':'development', 'training_hash':fingerprint, 'method':'Character TF-IDF + logistic regression', 'calibrated':False}
