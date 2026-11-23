"""Transparent utility-per-hour comparison using survivor-supplied inputs only."""
import math

def rank_tames(candidates):
    if not isinstance(candidates,list) or not 1 <= len(candidates) <= 20:
        raise ValueError('Provide 1–20 candidates')
    result=[]
    for item in candidates:
        if not isinstance(item,dict): raise ValueError('Each candidate must be an object')
        name=item.get('name')
        if not isinstance(name,str) or not name.strip() or len(name.strip())>100: raise ValueError('Each candidate needs a name up to 100 characters')
        try:
            if isinstance(item.get('utility'),bool) or isinstance(item.get('hours'),bool): raise ValueError()
            utility=float(item.get('utility'));hours=float(item.get('hours'))
        except (ValueError,TypeError,OverflowError): raise ValueError('Utility and effort must be numbers')
        if not math.isfinite(utility) or not 0<=utility<=1000000: raise ValueError('Utility must be 0–1000000')
        if not math.isfinite(hours) or not 0.01<=hours<=100000: raise ValueError('Effort must be 0.01–100000 hours')
        result.append({'name':name.strip(),'utility':utility,'hours':hours,'utility_per_hour':round(utility/hours,2), '_raw':utility/hours})
    result.sort(key=lambda x:x['_raw'],reverse=True)
    for item in result: del item['_raw']
    return {'ranking':result,'method':'User-defined utility ÷ user-estimated effort in hours; not a game-data estimate.'}
