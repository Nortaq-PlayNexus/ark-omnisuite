"""Survivor planning models with explicit limits, no live game access."""
import math
from . import _integer

BROODMOTHER_ARTIFACTS = ('Artifact of the Clever','Artifact of the Hunter','Artifact of the Massive')
BROODMOTHER_APEX = ('Argentavis Talon','Sarcosuchus Skin','Sauropod Vertebra','Titanoboa Venom')

def broodmother_manifest(difficulty, runs=1, inventory=None):
    """The Island Broodmother Arena tribute; not Fjordur or Center.
    https://ark.wiki.gg/wiki/Broodmother_Arena
    """
    if difficulty not in ('gamma','beta','alpha'): raise ValueError('Choose gamma, beta or alpha')
    runs=_integer(runs,'runs',1,1000)
    if inventory is None: inventory={}
    if not isinstance(inventory,dict) or len(inventory)>30: raise ValueError('Inventory must be an object with at most 30 entries')
    stock={}
    for name,value in inventory.items():
        if not isinstance(name,str) or len(name)>100: raise ValueError('Invalid inventory item name')
        stock[name]=_integer(value,'inventory '+name,0,10000000)
    required={name:runs for name in BROODMOTHER_ARTIFACTS}
    amount={'gamma':0,'beta':5,'alpha':10}[difficulty]*runs
    if amount: required.update({name:amount for name in BROODMOTHER_APEX})
    return {'boss':'Broodmother','map':'The Island','difficulty':difficulty,'runs':runs,'required':required,
            'missing':{name:max(0,count-stock.get(name,0)) for name,count in required.items()},
            'source':'https://ark.wiki.gg/wiki/Broodmother_Arena',
            'notes':'Tribute items only. Player level, gear, map variants, server settings and combat readiness are not checked.'}

def _number(value,name,minimum,maximum):
    if isinstance(value,bool): raise ValueError(name+' must be a number')
    try: n=float(value)
    except (ValueError,TypeError,OverflowError): raise ValueError(name+' must be a number')
    if not math.isfinite(n) or not minimum<=n<=maximum: raise ValueError(f'{name} must be {minimum}–{maximum}')
    return n

def incubation_mixer(eggs):
    """Maximise overlap of user-supplied closed intervals, not incubation speed."""
    if not isinstance(eggs,list) or not 1<=len(eggs)<=10: raise ValueError('Enter 1–10 egg ranges')
    valid=[]
    for e in eggs:
        if not isinstance(e,dict): raise ValueError('Egg range must be an object')
        name=e.get('name')
        if not isinstance(name,str) or not name.strip() or len(name)>100: raise ValueError('Each egg needs a name')
        low=_number(e.get('low'),'minimum temperature',-200,200);high=_number(e.get('high'),'maximum temperature',-200,200)
        if low>high: raise ValueError('Minimum temperature cannot exceed maximum')
        valid.append({'name':name.strip(),'low':low,'high':high})
    # The maximum count of closed intervals occurs at an interval endpoint.
    points=sorted({e['low'] for e in valid}|{e['high'] for e in valid})
    scored=[(sum(e['low']<=t<=e['high'] for e in valid),t) for t in points]
    best=max(x[0] for x in scored)
    temp=next(t for count,t in scored if count==best)
    included=[e['name'] for e in valid if e['low']<=temp<=e['high']]
    excluded=[e['name'] for e in valid if not e['low']<=temp<=e['high']]
    return {'temperature_c':temp,'covered':len(included),'total':len(valid),'included':included,'excluded':excluded,
            'notes':'User-entered ranges only. This is a mathematical overlap, not a guarantee of egg safety, hatch speed or incubator behaviour.'}

def waypoint_route(start, waypoints, return_to_start=False):
    """Exact shortest Euclidean grid path through <=8 user pins, Held–Karp DP."""
    if not isinstance(start,dict): raise ValueError('Start must have latitude and longitude')
    if not isinstance(return_to_start,bool): raise ValueError('return_to_start must be boolean')
    sx=_number(start.get('lon'),'start longitude',0,100);sy=_number(start.get('lat'),'start latitude',0,100)
    if not isinstance(waypoints,list) or not 1<=len(waypoints)<=8: raise ValueError('Route requires 1–8 waypoints')
    points=[]
    for p in waypoints:
        if not isinstance(p,dict): raise ValueError('Waypoint must be an object')
        name=p.get('name')
        if not isinstance(name,str) or not name.strip() or len(name)>100: raise ValueError('Waypoint name required')
        lat=_number(p.get('lat'),'latitude',0,100);lon=_number(p.get('lon'),'longitude',0,100)
        points.append({'name':name.strip(),'lat':lat,'lon':lon})
    def dist(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])
    coords=[(p['lon'],p['lat']) for p in points];origin=(sx,sy);n=len(points)
    dp={(1<<i,i):(dist(origin,coords[i]),(i,)) for i in range(n)}
    for mask in range(1,1<<n):
        for last in range(n):
            if (mask,last) not in dp: continue
            length,order=dp[(mask,last)]
            for nxt in range(n):
                if mask & (1<<nxt): continue
                key=(mask|1<<nxt,nxt);candidate=(length+dist(coords[last],coords[nxt]),order+(nxt,))
                if key not in dp or candidate<dp[key]: dp[key]=candidate
    full=(1<<n)-1
    choices=[(length+(dist(coords[last],origin) if return_to_start else 0),order)
             for (mask,last),(length,order) in dp.items() if mask==full]
    total,order=min(choices)
    ordered=[points[i] for i in order]
    stops=[{'name':'Start','lat':sy,'lon':sx}]+ordered
    if return_to_start: stops.append({'name':'Start','lat':sy,'lon':sx})
    legs=[];cumulative=0.0
    for index,(a,b) in enumerate(zip(stops,stops[1:]),1):
        length=dist((a['lon'],a['lat']),(b['lon'],b['lat']));cumulative+=length
        legs.append({'number':index,'from':a,'to':b,'grid_distance':round(length,3),'cumulative_grid_distance':round(cumulative,3)})
    return {'ordered':ordered, 'grid_distance':round(total,3), 'legs':legs, 'return_to_start':return_to_start,
            'notes':'Shortest straight-line coordinate-grid path, not in-game distance or time. Terrain, obstructions, vertical travel and danger are ignored.'}
