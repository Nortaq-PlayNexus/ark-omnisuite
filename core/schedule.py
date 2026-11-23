"""Compare manually supplied time windows; no scheduling or notifications."""
from datetime import datetime, timezone


def _instant(value, label):
    if not isinstance(value,str) or len(value)>40: raise ValueError(label+' must be an ISO 8601 timestamp with timezone')
    try:
        dt=datetime.fromisoformat(value.replace('Z','+00:00'))
        if dt.tzinfo is None or dt.utcoffset() is None: raise ValueError()
        dt=dt.astimezone(timezone.utc)
    except (ValueError,OverflowError): raise ValueError(label+' must be a valid ISO 8601 timestamp with timezone')
    if not 1970<=dt.year<=2100: raise ValueError(label+' must be within 1970–2100 UTC')
    return dt


def compare_windows(windows):
    if not isinstance(windows,list) or not 1<=len(windows)<=20: raise ValueError('Enter 1–20 event windows')
    events=[]
    for row in windows:
        if not isinstance(row,dict): raise ValueError('Each window must be an object')
        name=row.get('name')
        if not isinstance(name,str) or not name.strip() or len(name)>100: raise ValueError('Each window needs a name up to 100 characters')
        start=_instant(row.get('start'),'start');end=_instant(row.get('end'),'end')
        if start>=end: raise ValueError('End must be later than start')
        events.append((name.strip(),start,end))
    def iso(t): return t.isoformat().replace('+00:00','Z')
    ordered=sorted(enumerate(events),key=lambda x:(x[1][1],x[0]))
    results=[{'index':i,'name':n,'start':iso(s),'end':iso(e),'discord_start':f'<t:{int(s.timestamp())}:F>','discord_end':f'<t:{int(e.timestamp())}:F>'} for i,(n,s,e) in ordered]
    conflicts=[]
    for i,(a,sa,ea) in enumerate(events):
        for j in range(i+1,len(events)):
            b,sb,eb=events[j];start=max(sa,sb);end=min(ea,eb)
            if start<end: conflicts.append({'first_index':i,'second_index':j,'first':a,'second':b,'start':iso(start),'end':iso(end),'overlap_seconds':(end-start).total_seconds()})
    return {'windows':results,'conflicts':conflicts,'notes':'User-entered windows only; end is exclusive. No notifications, recurrence, named-timezone lookup, Discord posting or game schedule data.'}
