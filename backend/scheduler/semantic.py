"""Conservative, explainable capability mapping for generated task labels.

A generated tool name is not automatically a certification requirement. Map only
routine activities to broad skills; leave specialist work for human confirmation.
"""
from .intelligence import normalize_skill

ALIASES = {
 'api': {'javascript','rest api','api development','backend development','flask','react','node.js','frontend','frontend development'},
 'security': {'authentication','flask','backend development','api security','security testing','cybersecurity'},
 'gunicorn': {'deployment','cloud deployment','web deployment','server deployment','devops'},
 'matplotlib': {'data visualization','eda','exploratory data analysis','python plotting'},
 'seaborn': {'data visualization','eda','exploratory data analysis','python plotting'},
 'integration': {'python','streamlit','backend development','api development','rest api','flask'},
 'requirements analysis': {'documentation','project management','data cleaning','eda','data analysis'},
 'project management': {'documentation','requirements analysis','data analysis'},
 'docker': {'docker','containerization','devops'},
 'sql': {'sql','sqlite','database design','dbms','database management','data modeling'},
 'database design': {'sql','sqlite','database design','dbms','database management','data modeling'},
 'pytest': {'testing','software testing','qa','quality assurance','test automation','unit testing'},
 'linux': {'deployment','cloud deployment','web deployment','devops','linux'},
 'responsive design': {'css','html','frontend','frontend development','ui/ux'},
 'seo': {'seo','search engine optimization','html','web development'},
 'accessibility': {'accessibility','ui/ux','html','frontend','frontend development','software testing'},
 'cross browser testing': {'testing','software testing','qa','responsive design'},
 'ci/cd': {'deployment','github','devops','ci/cd'},
 'rest api': {'flask','rest api','api development','backend development','node.js','express'},
}

IMPLIES = {
 'software testing': {'pytest','unit testing','integration testing','functional testing','testing','qa'},
 'testing': {'pytest','unit testing','integration testing','functional testing','qa'},
 'deployment': {'linux','cloud deployment','web deployment','production deployment','hosting','gunicorn'},
 'dbms': {'database design','database schema','relational database','database','sql'},
 'sql': {'database schema','database design','relational database'},
 'sqlite': {'database schema','database design','sql','relational database'},
 'flask': {'rest api','restful api','api development','backend development','security'},
 'javascript': {'frontend','front end','ui development','api'},
 'html': {'frontend','front end','ui development','seo','accessibility'},
 'css': {'responsive design','frontend','front end','ui development'},
 'github': {'git','version control','ci/cd'},
 'data visualization': {'matplotlib','seaborn'},
 'eda': {'matplotlib','seaborn'},
}

def matches(required, member_skills):
    r = normalize_skill(required)['canonical'].casefold().strip()
    if not r: return True
    for skill in member_skills:
        s = normalize_skill(skill)['canonical'].casefold().strip()
        if r == s or r in IMPLIES.get(s, set()) or s in ALIASES.get(r, set()):
            return True
    return False
