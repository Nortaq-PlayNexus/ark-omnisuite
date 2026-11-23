"""Generate a safe subset of ASE config snippets, never alter user files."""
import math

def _rate(value,label):
    if isinstance(value,bool): raise ValueError(label+' must be a number')
    try: n=float(value)
    except (TypeError,ValueError,OverflowError): raise ValueError(label+' must be a number')
    if not math.isfinite(n) or not 0.01 <= n <= 1000: raise ValueError(label+' must be between 0.01 and 1000')
    return format(n,'.10g')

def ini_snippets(settings):
    if not isinstance(settings,dict): raise ValueError('settings must be an object')
    keys={'taming':'TamingSpeedMultiplier','xp':'XPMultiplier','harvest':'HarvestAmountMultiplier','hatch':'EggHatchSpeedMultiplier','mature':'BabyMatureSpeedMultiplier','mating':'MatingIntervalMultiplier'}
    rates={k:_rate(settings.get(k),k) for k in keys}
    gameuser='[ServerSettings]\n'+'\n'.join(f'{keys[k]}={rates[k]}' for k in ('taming','xp','harvest'))+'\n'
    game='[/script/shootergame.shootergamemode]\n'+'\n'.join(f'{keys[k]}={rates[k]}' for k in ('hatch','mature','mating'))+'\n'
    return {'gameusersettings':gameuser,'game':game,'notes':'Preview only; merge into the existing sections after backing up and stopping your server. Mating interval is a duration multiplier: lower means shorter waits.','source':'https://playyourway.com.au/help/ark-server-ini-settings-explained'}
