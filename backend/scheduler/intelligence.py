"""Planify: conservative skill normalization and rule-based project starter plans."""
import re
from difflib import get_close_matches

ALIASES = {
 'python':['py','python3','pyhton','pythn','pghnon'],
 'react':['reactjs','react.js','react js'],
 'javascript':['js','java script','ecmascript'],
 'dom manipulation':['dom','document object model','dom scripting'],
 'web storage':['storage','local storage','localstorage','browser storage'],
 'debugging':['debug','bug fixing','bugfixing'],
 'typescript':['ts','type script'],
 'html':['html5'], 'css':['css3','stylesheets'],
 'web development':['web dev','web programming','web prgm','web prog','webprogramming'],
 'node.js':['node','nodejs','node js'],
 'sql':['mysql','postgresql','postgres','sqlite'],
 'machine learning':['ml','machinelearning'],
 'artificial intelligence':['ai'],
 'data science':['data analytics','data analysis'],
 'api':['rest api','restful api','apis'],
 'database':['db','databases'],
 'testing':['qa','quality assurance','software testing'],
 'docker':['containers','containerization'],
 'cloud':['cloud computing'],
 'devops':['ci/cd','cicd'],
 'java':['java programming'],
 'flutter':['flutter framework'],
 'ui/ux':['ui ux','ui','ux','interface design'],
 'inventory management':['inventory','stock management'],
 'food safety':['hygiene','food hygiene'],
}
LOOKUP={alias:canonical for canonical,variants in ALIASES.items() for alias in [canonical,*variants]}
# Similarity only for sufficiently clear matches; otherwise ask the user to confirm.
def normalize_skill(raw):
    value=re.sub(r'\s+',' ',str(raw).strip().casefold()).strip()
    if not value: return {'input':str(raw),'canonical':'','confidence':'empty','suggestions':[]}
    if value in LOOKUP:
        return {'input':str(raw),'canonical':LOOKUP[value],'confidence':'exact_or_alias','suggestions':[]}
    matches=get_close_matches(value,list(LOOKUP),n=4,cutoff=0.78)
    canonical=[]
    for match in matches:
        candidate=LOOKUP[match]
        if candidate not in canonical: canonical.append(candidate)
    if canonical and len(value)>=4:
        from difflib import SequenceMatcher
        score=SequenceMatcher(None,value,matches[0]).ratio()
        if score>=0.88 and len(value)>=5:
            return {'input':str(raw),'canonical':canonical[0],'confidence':'fuzzy','suggestions':canonical}
    return {'input':str(raw),'canonical':value,'confidence':'unrecognized','suggestions':canonical}

def normalize_skills(skills):
    if isinstance(skills,str): skills=skills.split(',')
    if not isinstance(skills,list) or not all(isinstance(s,str) for s in skills):
        raise ValueError('skills must be a list of strings or comma-separated text')
    results=[normalize_skill(s) for s in skills if s.strip()]
    return {'normalized_skills':sorted(set(x['canonical'] for x in results if x['canonical'])),
            'matches':results,'needs_review':[x for x in results if x['confidence']=='unrecognized']}

TEMPLATES=[
 ('Plan requirements and user roles',['ui/ux'],4,[]),
 ('Design user interface',['react','css'],8,[0]),
 ('Create database schema',['sql','database'],6,[0]),
 ('Implement backend API',['python','api'],10,[2]),
 ('Connect frontend and backend',['react','api'],8,[1,3]),
 ('Test application',['testing'],6,[4]),
 ('Prepare deployment',['docker','cloud'],5,[5]),
]
DOMAIN={
 'mess': [('Design weekly meal menu',['ui/ux'],5),('Manage ingredients and inventory',['sql','inventory management'],8),('Handle student meal orders',['react','api'],8),('Track kitchen preparation and food safety',['food safety'],6)],
 'food': [('Design weekly meal menu',['ui/ux'],5),('Manage ingredients and inventory',['sql','inventory management'],8),('Handle student meal orders',['react','api'],8),('Track kitchen preparation and food safety',['food safety'],6)],
 'school': [('Manage student records',['sql','database'],7)],
 'shop': [('Manage product catalog',['sql','database'],7),('Build shopping cart',['react','api'],8)],
 'hospital': [('Manage patient records',['sql','database'],8)],
}
def project_plan(name,description=''):
    text=(str(name)+' '+str(description)).casefold()
    domain='general'
    for keyword in ('mess','food','shop','hospital','school'):
        if keyword in text: domain=keyword;break
    templates=list(TEMPLATES)
    if domain in DOMAIN:
        for title,skills,hours in DOMAIN[domain]:
            templates.append((title,skills,hours,[0]))
    tasks=[]
    for i,(title,skills,hours,deps) in enumerate(templates):
        tasks.append({'id':f'T{i+1}','title':title,'description':title,
                      'required_skills':skills,'estimated_hours':hours,
                      'priority':'high' if i in (0,2,3) else 'medium',
                      'dependencies':[f'T{d+1}' for d in deps]})
    return {'success':True,'project_name':name,'detected_domain':domain,
            'method':'rule_based_starter_template_v1','tasks':tasks,
            'note':'Starter suggestions, not validated ML predictions. Edit tasks, skills, hours and dependencies before scheduling.'}
