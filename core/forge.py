"""Baseline ASE refining forge planner; no parallel furnaces or server-rate changes."""
from . import _integer

FUEL_SECONDS={'thatch':7.5,'wood':30,'sparkpowder':60,'anglergel':240}

def refining_forge(ingots, fuel):
    count=_integer(ingots,'ingots',1,1000000)
    if not isinstance(fuel,str) or fuel not in FUEL_SECONDS: raise ValueError('Unknown fuel')
    # Half-seconds keep thatch calculations exact without float ceiling issues.
    burn_half_seconds=int(FUEL_SECONDS[fuel]*2)
    duration=count*20;half_seconds=duration*2
    fuel_units=(half_seconds+burn_half_seconds-1)//burn_half_seconds
    return {'ingots':count,'metal':count*2,'time_seconds':duration,'fuel':fuel,
            'fuel_units':fuel_units,'burn_seconds_per_unit':FUEL_SECONDS[fuel],
            'source':'https://ark.fandom.com/wiki/Refining_Forge',
            'assumptions':'One standard refining forge; continuous baseline metal smelting, one fuel type, 20 seconds per ingot; excludes fuel waste beyond rounding, gasoline, mods and custom rates.'}
