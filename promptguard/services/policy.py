"""Central policy used by scanning, document inspection and the gateway."""
DEFAULTS = {'warn':25, 'review':45, 'block':70, 'block_harmful':True, 'block_sensitive':True, 'ml_enabled':False, 'retain_prompts':False, 'retention_days':30, 'tools':[]}


def validate_policy(data):
    if not isinstance(data,dict) or set(data)-set(DEFAULTS):
        raise ValueError('Unknown policy fields.')
    result = {**DEFAULTS, **data}
    for key in ('warn','review','block','retention_days'):
        if type(result[key]) is not int:
            raise ValueError(key+' must be an integer.')
    if not 0 < result['warn'] < result['review'] < result['block'] <= 100:
        raise ValueError('Thresholds must satisfy 0 < warn < review < block <= 100.')
    if not 1 <= result['retention_days'] <= 365:
        raise ValueError('Retention must be 1–365 days.')
    for key in ('block_harmful','block_sensitive','ml_enabled','retain_prompts'):
        if type(result[key]) is not bool:
            raise ValueError(key+' must be a boolean.')
    if not isinstance(result['tools'],list) or any(x not in ('calculator',) for x in result['tools']):
        raise ValueError('Only the sandboxed calculator tool is supported.')
    return result


def decide(result, policy):
    reasons = []
    score = result['injection_score']
    if result['harmful_content']['detected'] and policy['block_harmful']:
        reasons.append('Independent harmful-content detector matched.')
    if result['sensitive_data']['detected'] and policy['block_sensitive']:
        reasons.append('Potential sensitive data detected.')
    action = 'BLOCK' if reasons or score >= policy['block'] else 'REVIEW' if score >= policy['review'] else 'WARN' if score >= policy['warn'] else 'ALLOW'
    if not reasons:
        reasons.append(f'Injection score {score}; thresholds warn/review/block: {policy["warn"]}/{policy["review"]}/{policy["block"]}.')
    if policy['ml_enabled'] and result['ml'].get('available') and result['ml']['score'] >= 65 and action in ('ALLOW','WARN'):
        action = 'REVIEW'; reasons.append('Lexical ML baseline indicates uncertainty; review required.')
    return {'action':action,'reasons':reasons,'forward_allowed':action in ('ALLOW','WARN'), 'review_required':action=='REVIEW'}
