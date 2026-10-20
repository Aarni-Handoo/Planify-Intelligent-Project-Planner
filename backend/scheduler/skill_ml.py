"""Skill compatibility: trained model for novel wording, conservative curated ground truth.
Never treat related technologies as interchangeable without explicit coverage.
"""
from pathlib import Path
from functools import lru_cache
import re
import numpy as np
import joblib
from sklearn.metrics.pairwise import cosine_similarity
from .intelligence import normalize_skill

MODEL_PATH=Path(__file__).resolve().parents[1]/'ml'/'models'/'skill_v1'/'skill_matcher.joblib'

@lru_cache(maxsize=1)
def model():
    return joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None

def _clean(value):
    return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9+#/ .-]',' ',str(value).casefold())).strip()

def _expand(skill,implies):
    out={skill};pending=[skill]
    while pending:
        for next_skill in implies.get(pending.pop(),[]):
            if next_skill not in out:out.add(next_skill);pending.append(next_skill)
    return out

def _features(required,member,model_data):
    catalog=model_data['prototypes'];vec=model_data['vectorizer']
    groups=_expand(member,model_data['implies'])
    pos=[p for group in groups if group in catalog for p in catalog[group]]
    neg=[p for group in catalog if group not in groups for p in catalog[group]]
    if not pos or not neg:return None
    req=vec.transform([required]);a=np.sort(cosine_similarity(req,vec.transform(pos))[0])[-3:]
    b=np.sort(cosine_similarity(req,vec.transform(neg))[0])[-3:]
    return np.array([[float(a[-1]),float(a.mean()),float(b[-1]),float(b.mean()),float(a[-1]-b[-1]),float(a[-1]/(b[-1]+0.05))]])

def compatible(required, member_skills):
    """Return match, method, confidence. ML low confidence abstains (no fabricated qualification)."""
    data=model(); required=_clean(required)
    skills={normalize_skill(s)['canonical'] for s in member_skills}
    if not required:return {'match':True,'method':'empty_requirement','confidence':1.0}
    if not data:return {'match':required in skills,'method':'exact_fallback','confidence':1.0 if required in skills else 0.0}
    # Explicitly parse dimensional array requests without assuming every
    # language qualifies for every framework or specialist technique.
    array_match=re.fullmatch(r'([23])d arrays? in (c\+\+|cpp|c|python|javascript|java|typescript)',required)
    if array_match:
        lang={'cpp':'cpp','c++':'cpp'}.get(array_match.group(2),array_match.group(2))
        return {'match':lang in skills,'method':'typed_array_capability','confidence':1.0 if lang in skills else 0.0}
    if required in data['ambiguous']:
        return {'match':required in skills,'method':'ambiguous_requires_confirmation','confidence':0.0}
    for member in skills:
        groups=_expand(member,data['implies'])
        if required in groups or any(required in data['catalog'].get(group,[]) for group in groups):
            return {'match':True,'method':'verified_capability','confidence':1.0}
    # Model is trained on generated labels, so only accept high-confidence novel phrases.
    probabilities=[]
    for member in skills:
        features=_features(required,member,data)
        if features is not None:probabilities.append(float(data['classifier'].predict_proba(features)[0,1]))
    confidence=max(probabilities,default=0.0)
    return {'match':confidence>=0.93,'method':'trained_skill_classifier' if confidence>=0.93 else 'unverified_skill',
            'confidence':round(confidence,3)}
