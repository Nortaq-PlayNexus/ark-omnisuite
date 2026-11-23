"""ASE parental-stat inheritance: https://ark.wiki.gg/wiki/Breeding ."""
import math
from . import _integer

def inheritance_odds(differing_stats, attempts):
    """Initial stronger stat for each differing target, before mutation.

    Assumes independent 55% choices per differing stat and independent breeding
    events. Multiple offspring from one breeding event must not be counted as
    independent. Equal parental stats require no successful inheritance roll.
    """
    n=_integer(differing_stats,'differing stats',0,7)
    attempts=_integer(attempts,'independent breeding events',1,100000)
    p=0.55 ** n
    total=1.0 if p == 1 else -math.expm1(attempts*math.log1p(-p))
    return {'differing_stats':n,'events':attempts,'per_event_percent':round(p*100,4),
            'at_least_one_percent':round(total*100,4),'expected_events':round(1/p,2),
            'source':'https://ark.wiki.gg/wiki/Breeding',
            'assumption':'Independent initial inheritance; excludes mutations, sex and imprint. Twins/triplets from one event are not independent attempts.'}
