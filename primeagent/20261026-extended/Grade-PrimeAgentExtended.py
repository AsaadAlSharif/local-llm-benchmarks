"""Independent predeclared graders. Never repair agent output or issue feedback."""
import copy
import hashlib
import importlib.util
import json
import random
import sqlite3
import sys
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

directory=Path(sys.argv[1]); plan=json.loads((directory/'plan.json').read_text(encoding='utf-8-sig'))
workspace=Path(plan['workspace']); checks=[]
def check(task,name,fn):
    try:
        assert fn(), name
        checks.append({'task':task,'name':name,'passed':True})
    except Exception as error: checks.append({'task':task,'name':name,'passed':False,'error':str(error)})
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
browser=load(directory/'browser-verification.json')
attempts={a['task']:a for a in browser['attempts']}
for task in plan['tasks']:
    a=attempts.get(task,{})
    check(task,'UI turn completed without browser/observer/turn errors',lambda a=a:a.get('completed') and not a.get('errors') and not a.get('observerError') and not a.get('hasTurnError'))
for task in ['repair','sql']:
    check(task,'Agent actually executed a command',lambda task=task:any('shell' in t['tool'].lower() and t['status']=='completed' for t in attempts.get(task,{}).get('tools',[])))

def money(n): return n.quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
def reference(items,rate='5',discount='0'):
    lines=[money(Decimal(i['unit_price'])*i['quantity']) for i in items]
    subtotal=sum(lines,Decimal(0)); discount=money(Decimal(discount))
    tax=money((subtotal-discount)*Decimal(rate)/100)
    return {'line_totals':[format(i,'.2f') for i in lines],'subtotal':format(subtotal,'.2f'),'discount':format(discount,'.2f'),'tax':format(tax,'.2f'),'total':format(subtotal-discount+tax,'.2f')}
try:
    spec=importlib.util.spec_from_file_location('agent_settlement',workspace/'repair/settlement.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);settle=module.settle_invoice
    vectors=[([], '5','0'),([{'quantity':1,'unit_price':'1.005'}],'5','0'),([{'quantity':3,'unit_price':'0.335'}],'5','0'),([{'quantity':1,'unit_price':'10'}],'5','2'),([{'quantity':1,'unit_price':'0.01'}],'50','0'),([{'quantity':1,'unit_price':'100000000000.99'}],'7.5','0'),([{'quantity':2,'unit_price':'3.335'},{'quantity':3,'unit_price':'4.445'}],'17.5','1.005'),([{'quantity':1,'unit_price':'5'}],'100','5')]
    rng=random.Random(6392026)
    for i in range(24):
        items=[{'quantity':rng.randint(1,7),'unit_price':str(Decimal(rng.randint(0,50000))/1000)} for _ in range(rng.randint(1,5))]
        vectors.append((items,str(rng.choice([0,5,7.5,50,100])),'0'))
    for n,(items,rate,disc) in enumerate(vectors):
        original=copy.deepcopy(items)
        check('repair',f'Decimal oracle and nonmutation case {n+1}',lambda items=items,rate=rate,disc=disc,original=original:settle(items,rate,disc)==reference(items,rate,disc) and items==original)
    invalid=[(None,'5','0'),({},'5','0'),([{}],'5','0'),([{'quantity':True,'unit_price':'1'}],'5','0'),([{'quantity':0,'unit_price':'1'}],'5','0'),([{'quantity':-1,'unit_price':'1'}],'5','0'),([{'quantity':1.5,'unit_price':'1'}],'5','0'),([{'quantity':1,'unit_price':1.0}],'5','0'),([{'quantity':1,'unit_price':'-1'}],'5','0'),([{'quantity':1,'unit_price':'NaN'}],'5','0'),([{'quantity':1,'unit_price':'Infinity'}],'5','0'),([{'quantity':1,'unit_price':'abc'}],'5','0'),([], '-1','0'),([], '101','0'),([], 'NaN','0'),([], 5,'0'),([], '5','-1'),([], '5','NaN'),([], '5','Infinity'),([], '5','1')]
    def rejects(args):
        try: settle(*args)
        except ValueError:return True
        return False
    for n,args in enumerate(invalid):check('repair',f'Invalid contract case {n+1}',lambda args=args:rejects(args))
except Exception as error:check('repair','Load generated module',lambda:(_ for _ in ()).throw(error))

fixture=load(directory/'sql-fixture.json')
schema=(directory/'inputs/sql/schema.sql').read_text()
def oracle(data):
    result=[]
    for cid,name in data['customers']:
        total=paid=credit=outstanding=0
        for iid,customer,amount,status in data['invoices']:
            if customer!=cid or status!='issued':continue
            p=sum(row[2] for row in data['payments'] if row[1]==iid and row[3]=='posted')
            c=sum(row[2] for row in data['credits'] if row[1]==iid and row[3]=='approved')
            total+=amount;paid+=p;credit+=c;outstanding+=max(amount-p-c,0)
        result.append(dict(customer_id=cid,name=name,invoice_total_cents=total,paid_cents=paid,credit_cents=credit,outstanding_cents=outstanding))
    return sorted(result,key=lambda r:(-r['outstanding_cents'],r['customer_id']))
try:
    sql=(workspace/'sql/report.sql').read_text(encoding='utf-8-sig')
    variants=[fixture]
    for mode in range(6):
        data=copy.deepcopy(fixture)
        if mode==0:data['payments']+=[[90,10,1000,'posted']]
        if mode==1:data['credits']+=[[90,10,500,'approved']]
        if mode==2:data['invoices']+=[[90,3,7000,'issued']]
        if mode==3:data['invoices']=[];data['credits']=[];data['payments']=[]
        if mode==4:data['customers']=[];data['invoices']=[];data['credits']=[];data['payments']=[]
        if mode==5:data['payments']+=[[90,10,999999,'pending']];data['credits']+=[[90,11,999999,'pending']]
        variants.append(data)
    def correct_sql(data):
        with sqlite3.connect(':memory:') as db:
            db.executescript(schema)
            for table,rows in data.items():
                if rows:db.executemany('INSERT INTO '+table+' VALUES ('+','.join('?' for _ in rows[0])+')',rows)
            db.commit();db.row_factory=sqlite3.Row
            allowed={sqlite3.SQLITE_SELECT,sqlite3.SQLITE_READ,sqlite3.SQLITE_FUNCTION,sqlite3.SQLITE_RECURSIVE}
            db.set_authorizer(lambda action,*args:sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY)
            ticks=[0]
            def interrupt():ticks[0]+=1;return ticks[0]>1000
            db.set_progress_handler(interrupt,1000)
            rows=[dict(row) for row in db.execute(sql)]
            return rows==oracle(data) and all(type(v) is int for row in rows for k,v in row.items() if k!='name')
    for n,data in enumerate(variants):check('sql',f'Read-only SQL oracle dataset {n+1}',lambda data=data:correct_sql(data))
    check('sql','Agent saved actual correct source-query rows',lambda:load(workspace/'sql/result.json')==oracle(fixture))
    check('sql','Source database byte identity preserved',lambda:(workspace/'sql/accounts.db').read_bytes()==(directory/'inputs/sql/accounts.db').read_bytes())
except Exception as error:check('sql','Load and execute generated SQL',lambda:(_ for _ in ()).throw(error))

expected={'project':'واحة المعرفة','supplier':'شركة النور','currency':'AED','currentDate':'2026-02-28','previousDate':'2026-01-31','currentSource':'02-approved.docx','previousSource':'01-approved.docx','excludedSources':['03-draft.docx'],'currentTotal':2500,'previousTotal':2000,'delta':500,'percentIncrease':25}
try:
    actual=load(workspace/'evidence/result.json')
    check('evidence','Exact result schema',lambda:set(actual)==set(expected))
    for key,value in expected.items():check('evidence','Evidence field '+key,lambda key=key,value=value:actual.get(key)==value and (not isinstance(value,(int,float)) or type(actual.get(key)) in [int,float]))
    tools=attempts.get('evidence',{}).get('tools',[])
    check('evidence','Three connected document reads completed',lambda:sum(t['tool']=='mcp__local-workbench__read_document' and t['status']=='completed' for t in tools)>=3)
    check('evidence','Exact-math MCP invocation completed',lambda:any(t['tool']=='mcp__local-workbench__math_compute' and t['status']=='completed' for t in tools))
    check('evidence','All three source filenames cited in final answer',lambda:all(n in attempts['evidence'].get('answer','') for n in ['01-approved.docx','02-approved.docx','03-draft.docx']))
    check('evidence','Original document fixtures unchanged',lambda:all(p.read_bytes()==(workspace/'evidence'/p.name).read_bytes() for p in (directory/'inputs/evidence').glob('*.docx')))
except Exception as error:check('evidence','Load evidence result',lambda:(_ for _ in ()).throw(error))

result={'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'checks':len(checks),'passed':sum(c['passed'] for c in checks),'failed':[c for c in checks if not c['passed']],'details':checks}
(directory/'independent-functional-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in result.items() if k!='details'},ensure_ascii=True))
sys.exit(bool(result['failed']))
