"""Evidence-oriented layered analysis around the original detector interface."""
import hashlib
import re
import time
from functools import lru_cache
from promptguard.detectors import CombinedDetector
from promptguard.detectors.pattern_detector import PatternDetector
from promptguard.services.normalization import variants, language
from promptguard.services.policy import DEFAULTS, decide
from promptguard.services.semantic import classify

SECRET_PATTERNS = [
 ('Email address', r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'),
 ('Private key', r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
 ('Assigned credential', r'(?i)\b(?:api[_ -]?key|password|access[_ -]?token|secret)\s*[:=]\s*["\']?[^\s"\',;]{8,}'),
 ('API token pattern', r'\b(?:sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,})\b'),
]


def redact(text):
    for _,pattern in SECRET_PATTERNS:
        text = re.sub(pattern, '[REDACTED]', text)
    return text


def sensitive(text):
    findings = []
    for name, pattern in SECRET_PATTERNS:
        for m in list(re.finditer(pattern,text))[:10]:
            findings.append({'name':name, 'start':m.start(), 'end':m.end(), 'evidence':'[REDACTED]'})
    return {'detected':bool(findings), 'findings':findings}


@lru_cache(maxsize=1)
def version():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    digest = hashlib.sha256()
    for folder in ('detectors','services'):
        for path in sorted((root/folder).glob('*.py')):
            digest.update(path.name.encode()); digest.update(path.read_bytes())
    digest.update((root/'data/rules.json').read_bytes())
    return 'pg-3-' + digest.hexdigest()[:12]


class LayeredEngine:
    def __init__(self):
        self.base = CombinedDetector()
        self.patterns = PatternDetector()

    def analyze(self, prompt, source='user', source_name='', policy=None, mode='hybrid'):
        started = time.perf_counter()
        policy = {**DEFAULTS, **(policy or {})}
        copies = [('original',prompt)] if mode=='rules' else variants(prompt)
        aggregate = {}
        harmful = None
        legacy_score = 0
        for method, text in copies:
            result = self.base.analyze(text)
            legacy_score = max(legacy_score,result['score'])
            if harmful is None or result['harmful_content']['detected']:
                harmful = result['harmful_content']
            for finding in result['findings']:
                if finding['name'] not in aggregate:
                    evidence = ''
                    for rule in self.patterns.rules:
                        if rule['name'] == finding['name']:
                            from promptguard.detectors.base import normalize_text
                            match = rule['compiled'].search(normalize_text(text))
                            evidence = redact(match[0][:220]) if match else ''
                            break
                    aggregate[finding['name']] = {**finding,'evidence':evidence, 'variant':method, 'layer':'safety' if finding['category'] in ('Dangerous request','Violent threat language','Harmful content') else 'injection'}
        # Actual embedded instructions in untrusted data must not be masked as educational quotes.
        if source != 'user':
            for method, text in copies:
                for finding in self.patterns.detect(text):
                    aggregate.setdefault(finding['name'], {**finding,'evidence':'Matched in untrusted source.', 'variant':method, 'layer':'safety' if finding['category'] in ('Dangerous request','Violent threat language','Harmful content') else 'injection'})
        findings = list(aggregate.values())
        safety_categories = sorted({x['category'] for x in findings if x['layer']=='safety'})
        if safety_categories:
            harmful = {**harmful, 'detected':True, 'categories':sorted(set(harmful['categories'] + safety_categories))}
        injection = min(100,sum(x['weight'] for x in findings if x['layer']=='injection'))
        result = self.base.analyze(prompt)
        result.update(score=max(legacy_score, injection), injection_score=injection, findings=findings, categories=sorted({x['category'] for x in findings}), harmful_content=harmful)
        result['level'] = 'High' if result['score']>=60 else 'Medium' if result['score']>=25 else 'Low'
        result['css'] = result['level'].lower()
        result['summary'] = 'Matched security signals require review.' if result['score']>=25 else 'No strong configured pattern matched; this does not establish safety.'
        result['summary_zh'] = '检测到需要审查的安全信号。' if result['score']>=25 else '未检测到明显的已配置模式，但这不能证明内容安全。'
        result['source'] = {'type':source,'name':redact(source_name[:120]),'trusted':source=='user', 'instruction_boundary':'External content is data, never an authority.'}
        result['normalization'] = {'variants_checked':len(copies),'methods':list(dict.fromkeys(x[0] for x in copies)),'original_sha256':hashlib.sha256(prompt.encode()).hexdigest()}
        secret_findings=[]
        for method,text in copies:
            for finding in sensitive(text)['findings']:
                candidate={**finding,'variant':method}
                if candidate not in secret_findings:secret_findings.append(candidate)
        result['sensitive_data'] = {'detected':bool(secret_findings),'findings':secret_findings}
        result['language'] = language(prompt)
        result['ml'] = classify(prompt) if policy['ml_enabled'] else {'available':False,'score':0,'reason':'Disabled by policy.'}
        result['detectors'] = [
            {'name':'Injection / jailbreak / tool misuse','score':injection,'findings':sum(x['layer']=='injection' for x in findings)},
            {'name':'Harmful intent','score':85 if harmful['detected'] else 0,'findings':len(harmful['categories'])},
            {'name':'Sensitive data','score':80 if result['sensitive_data']['detected'] else 0,'findings':len(result['sensitive_data']['findings'])},
            {'name':'Indirect source context','score':injection if source!='user' else 0,'findings':int(source!='user' and injection>0)},
        ]
        result['decision'] = decide(result,policy)
        result['engine_version'] = version()
        result['latency_ms'] = round((time.perf_counter()-started)*1000,2)
        result['remediation'] = 'Reject embedded instructions; remove secrets; verify the source and request.' if result['decision']['action']!='ALLOW' else 'Apply least-privilege tool permissions and continue monitoring.'
        return result
