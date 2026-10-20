"""Train an auditable skill-pair model on curated, generated examples.
Labels are assumed capability relationships, NOT real hiring qualifications.
"""
import csv, json, random
from pathlib import Path
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import GroupShuffleSplit

ROOT=Path(__file__).resolve().parent.parent
# member skill -> example capabilities and their varied surface forms
CATALOG={
 'javascript':['javascript','js','ecmascript','dom','domskill','dom manipulation','document object model','browser events','event listeners','array methods','2d arrays in javascript','3d arrays in javascript','web storage','localstorage','browser storage','finding errors in javascript','javascript debugging','client-side scripting'],
 'typescript':['typescript','ts','javascript','dom','domskill','browser events','array methods','web storage','javascript debugging'],
 'react':['react','reactjs','react components','react hooks','jsx','component state','react user interface','dom manipulation'],
 'html':['html','html5','semantic html','html layout','web page markup'],
 'css':['css','css3','responsive design','flexbox','css grid','responsive styling','media queries','styling web pages'],
 'python':['python','python3','python scripting','python arrays','2d arrays in python','3d arrays in python','python debugging','finding errors in python'],
 'c':['c','c programming','c language','2d arrays in c','3d arrays in c','matrix operations in c','c debugging'],
 'cpp':['c++','cpp','c++ programming','2d arrays in c++','3d arrays in c++','c++ debugging'],
 'java':['java','java programming','java arrays','2d arrays in java','3d arrays in java','java debugging'],
 'sql':['sql','mysql','postgresql','sqlite','database queries','sql data manipulation','data manipulation in dbms','dbms','relational databases','sql joins','crud queries'],
 'database':['database','dbms','database schema','data modeling','relational database design'],
 'debugging':['debugging','finding errors','bug fixing','troubleshooting code','diagnosing software bugs'],
 'testing':['testing','software testing','qa','test cases','functional testing','cross browser testing','bug reporting'],
 'ui/ux':['ui/ux','user experience','user interface design','wireframes','figma','visual design','usability'],
 'git':['git','version control','git branches','github repositories','git commits'],
 'deployment':['deployment','deploying applications','hosting','publish website','netlify deployment','github pages deployment'],
 'docker':['docker','containerization','dockerfiles','docker containers'],
 'kubernetes':['kubernetes','k8s','container orchestration','kubernetes cluster'],
 'machine learning':['machine learning','ml','train prediction model','classification model','regression model','scikit-learn'],
 'deep learning':['deep learning','neural networks','pytorch','tensorflow','train neural network'],
 'computer vision':['computer vision','image classification','object detection','opencv','image recognition'],
 'flask':['flask','python flask','flask rest api','flask backend'],
 'api':['rest api','restful services','api development','http endpoints','backend integration'],
 'node.js':['node.js','nodejs','node backend','express server','javascript backend'],
 'cloud':['cloud','cloud computing','cloud infrastructure','aws cloud'],
 'security':['security','authentication','authorization','access control','secure login'],
}
# Explicit limited prerequisites, not all related technologies are interchangeable.
IMPLIES={'typescript':['javascript'],'react':['javascript'],'flask':['python','api'],
         'node.js':['javascript','api'],'deep learning':['machine learning'],
         'computer vision':['machine learning'],'sql':['database']}
# These are context-dependent; abstain rather than treating them as universally equivalent.
AMBIGUOUS={'data manipulation','arrays','2d array','3d array','storage','backend','frontend','programming','cloud deployment'}

def expand(member):
    out={member}; stack=[member]
    while stack:
        for implied in IMPLIES.get(stack.pop(),[]):
            if implied not in out:out.add(implied);stack.append(implied)
    return out

def train():
    random.seed(42)
    items=[]
    for member in CATALOG:
        positive=set().union(*(set(CATALOG[s]) for s in expand(member)))
        for required in positive:
            items.append((required,member,1))
        negative=[r for other,phrases in CATALOG.items() if other not in expand(member) for r in phrases if r not in positive]
        for required in random.sample(negative,min(len(negative),max(18,len(positive)*3))):
            items.append((required,member,0))
    # Context-sensitive adversarial pairs (do not conflate Docker/Kubernetes, etc.)
    items += [(a,b,0) for a,b in [('kubernetes','docker'),('sql optimization','basic sql'),('figma','css'),('git','react'),('deployment','javascript'),('medical diagnosis','machine learning'),('python','java'),('database administration','sql'),('machine learning','python')]]
    # Hold out requirement PHRASES, preventing exact memorization of test expressions.
    rng=np.random.RandomState(42)
    phrases=sorted({x[0] for x in items}); rng.shuffle(phrases)
    test_phrases=set(phrases[:max(1,len(phrases)//5)])
    train_rows=[x for x in items if x[0] not in test_phrases]
    test_rows=[x for x in items if x[0] in test_phrases]
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.metrics.pairwise import cosine_similarity
    # A model trained on graded similarities to known skill descriptions,
    # not on arbitrary ordered pairs of skill names.
    prototypes={k:[x for x in v if x not in test_phrases] or [k] for k,v in CATALOG.items()}
    vec=TfidfVectorizer(analyzer='char_wb',ngram_range=(2,5),sublinear_tf=True)
    vec.fit([s for v in prototypes.values() for s in v]+[x[0] for x in train_rows])
    from functools import lru_cache
    @lru_cache(None)
    def feat(required,member):
        if member not in CATALOG: return [0.,0.,1.,1.,-1.,0.]
        req=vec.transform([required]); groups=expand(member)
        positives=[x for group in groups for x in prototypes[group]]
        negative=[x for group in CATALOG if group not in groups for x in prototypes[group]]
        sim_pos=cosine_similarity(req,vec.transform(positives))[0]
        sim_neg=cosine_similarity(req,vec.transform(negative))[0]
        a=np.sort(sim_pos)[-3:]; b=np.sort(sim_neg)[-3:]
        return [float(a[-1]),float(a.mean()),float(b[-1]),float(b.mean()),float(a[-1]-b[-1]),float(a[-1]/(b[-1]+0.05))]
    X=np.array([feat(a,b) for a,b,_ in train_rows]);Y=np.array([y for _,_,y in train_rows]);
    clf=HistGradientBoostingClassifier(max_iter=90,max_leaf_nodes=9,l2_regularization=2,random_state=42)
    clf.fit(X,Y)
    Xt=np.array([feat(a,b) for a,b,_ in test_rows]);
    pred=clf.predict(Xt); y=[x[2] for x in test_rows]
    print(classification_report(y,pred,zero_division=0))
    out=ROOT/'ml'/'models'/'skill_v1';out.mkdir(parents=True,exist_ok=True)
    joblib.dump({'vectorizer':vec,'classifier':clf,'catalog':CATALOG,'prototypes':prototypes,'implies':IMPLIES,'ambiguous':sorted(AMBIGUOUS)},out/'skill_matcher.joblib')
    data=ROOT/'data'/'processed';data.mkdir(parents=True,exist_ok=True)
    with (data/'skill_pairs_v1.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['required_skill','member_skill','compatible','split','source'])
        for row in items:w.writerow([*row,'test' if row[0] in test_phrases else 'train','curated_generated'])
    report=classification_report(y,pred,output_dict=True,zero_division=0)
    (out/'evaluation.json').write_text(json.dumps({'split':'held-out requirement phrases','test_count':len(y),'train_count':len(train_rows),'metrics':report,'caveat':'Curated generated examples, not independently labeled real-world qualification data.'},indent=2))
    print('Training pairs:',len(train_rows),'Test pairs:',len(test_rows))
if __name__=='__main__':train()
