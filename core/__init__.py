"""Small verified and user-input-driven OMNISUITE core."""
import math

def _integer(value, name, minimum=0, maximum=1000000):
    if isinstance(value, bool): raise ValueError(f'{name} must be an integer')
    try: n = int(value)
    except (TypeError, ValueError, OverflowError): raise ValueError(f'{name} must be an integer')
    if str(n) != str(value).strip() and not (isinstance(value, float) and value == n):
        raise ValueError(f'{name} must be an integer')
    if not minimum <= n <= maximum: raise ValueError(f'{name} must be {minimum}–{maximum}')
    return n

def ingots(count):
    """Two Metal produce one Metal Ingot; fuel and processing time excluded.
    https://ark.fandom.com/wiki/Metal_Ingot"""
    count = _integer(count, 'ingots', 1)
    return {'ingots': count, 'metal': 2 * count, 'fuel_included': False}

def mutation_odds(offspring, mother=0, father=0):
    """3 independent 2.5% rolls per breeding event, ONLY when both counters below 20.
    Independent events assumed; twins/triplets from a single event do not count as independent.
    https://ark.wiki.gg/wiki/Mutations"""
    n = _integer(offspring, 'offspring', 1, 100000)
    mother = _integer(mother, 'mother counter', 0)
    father = _integer(father, 'father counter', 0)
    if mother >= 20 or father >= 20:
        raise ValueError('This model supports only parents with total mutation counters below 20.')
    p = -math.expm1(n * 3 * math.log1p(-0.025))
    return {'offspring': n, 'probability_percent': round(100*p, 3), 'assumption': 'both parent counters below 20; three independent 2.5% checks per breeding event; independent events assumed'}

def readiness(checks):
    if not isinstance(checks, list) or len(checks) != 5 or not all(isinstance(x,bool) for x in checks):
        raise ValueError('five boolean checks are required')
    return {'score': 20 * sum(checks), 'checked': sum(checks), 'total': 5, 'method': 'equal-weight self-reported checklist; not an in-game defense measurement'}

def advisor(minutes, metal_shortage, raid_soon):
    minutes = _integer(minutes, 'minutes', 1, 1440)
    if not isinstance(metal_shortage, bool) or not isinstance(raid_soon, bool): raise ValueError('flags must be boolean')
    tasks=[]
    if raid_soon: tasks.append('Inspect turret coverage, ammunition and generator fuel before the raid window.')
    if metal_shortage: tasks.append('Plan a metal run; reserve time to refine ore and return safely.')
    if minutes < 60: tasks.append('Prioritise one short objective and leave time to return to base.')
    else: tasks.append('Review tame, breeding and boss preparations for your next session.')
    return {'minutes': minutes, 'tasks': tasks, 'note': 'Heuristic suggestions based only on the information you supplied.'}
