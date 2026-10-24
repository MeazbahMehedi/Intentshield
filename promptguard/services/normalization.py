"""Bounded decoding variants. Encoding alone never produces a threat score."""
import base64
import html
import re
from urllib.parse import unquote
from promptguard.detectors.base import normalize_text


def variants(text):
    candidates = [('original', text)]
    seen = {text}
    for depth in range(2):
        for source, value in list(candidates)[-12:]:
            decoded = [('html/url', unquote(html.unescape(value)))]
            decoded.append(('unicode escapes', re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m[1],16)), value)))
            for match in list(re.finditer(r'(?<![\w])(?:[A-Za-z0-9+/]{20,}={0,2})(?![\w])', value))[:6]:
                try:
                    result = base64.b64decode(match[0], validate=True).decode('utf-8')
                    decoded.append(('base64', value[:match.start()] + result + value[match.end():]))
                except (ValueError, UnicodeDecodeError):
                    pass
            for match in list(re.finditer(r'\b(?:[0-9a-fA-F]{2}){12,}\b', value))[:6]:
                try:
                    decoded.append(('hex', value[:match.start()] + bytes.fromhex(match[0]).decode('utf-8') + value[match.end():]))
                except (ValueError, UnicodeDecodeError):
                    pass
            for method, result in decoded:
                if len(result) <= 10000 and result not in seen and len(candidates) < 16:
                    candidates.append((method, result)); seen.add(result)
    normal = normalize_text(html.unescape(text))
    # Limited known-word deobfuscation, rather than globally rewriting numbers.
    replacements = {'1gnore':'ignore','ign0re':'ignore','previ0us':'previous','instructi0ns':'instructions','syst3m':'system','pr0mpt':'prompt','r3veal':'reveal'}
    for old,new in replacements.items():
        normal = re.sub(r'\b'+old+r'\b', new, normal)
    normal = re.sub(r'\b(?:[a-z]\s+){3,}[a-z]\b', lambda m:m[0].replace(' ',''), normal)
    if normal not in seen:
        candidates.append(('normalized', normal))
    return candidates


def language(text):
    chinese = bool(re.search(r'[\u4e00-\u9fff]', text))
    latin = bool(re.search(r'[a-zA-Z]', text))
    return 'zh-en' if chinese and latin else 'zh' if chinese else 'en/other'
