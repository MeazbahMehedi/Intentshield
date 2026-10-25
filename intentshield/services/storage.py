"""Store redacted evidence by default; raw retention is an explicit local policy."""
import json
import time
from uuid import uuid4
from intentshield.database.db import db, owner, settings, history
from intentshield.services.engine import redact


def save_scan(prompt,result,demo=False):
    scan_id=uuid4().hex
    public=json.loads(json.dumps(result))
    # All evidence has already been redacted; do not store normalized full prompt copies.
    entry={'id':scan_id,'time':time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime()),'preview':('[demo] ' if demo else '')+('[Sensitive content omitted]' if result['sensitive_data']['detected'] else redact(prompt)[:72].replace('\n',' ')),'level':result['level'],'score':result['score'],'findings':len(result['findings']),'rule_names':[x['name'] for x in result['findings']],'categories':result['categories'],'harmful':result['harmful_content']['detected'],'harmful_categories':result['harmful_content']['categories'],'action':result['decision']['action'],'language':result['language'],'latency_ms':result['latency_ms'],'report':public}
    if settings().get('retain_prompts',False): entry['prompt']=prompt
    db().execute('INSERT INTO scans VALUES (?,?,?,?)',(scan_id,owner(),time.time(),json.dumps(entry,ensure_ascii=False)))
    db().execute('DELETE FROM scans WHERE owner=? AND id NOT IN (SELECT id FROM scans WHERE owner=? ORDER BY stamp DESC LIMIT 2000)',(owner(),owner()))
    db().commit()
    result['scan_id']=scan_id
    return entry


def get_scan(scan_id):
    row=db().execute('SELECT data FROM scans WHERE id=? AND owner=?',(scan_id,owner())).fetchone()
    return json.loads(row['data']) if row else None
