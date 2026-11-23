"""Small, attributed ASE recipe catalog; explicit station variants and batch rounding."""
from math import ceil
from . import _integer

# No substitutions, fuel, station construction costs, spoilage or modded recipes.
RECIPES = {
 'metal_ingot': {'name':'Metal Ingot', 'station':'Refining Forge', 'yield':1, 'ingredients':{'Metal':2}, 'url':'https://ark.fandom.com/wiki/Metal_Ingot'},
 'smithy': {'name':'Smithy', 'station':'Inventory', 'yield':1, 'ingredients':{'Metal Ingot':5,'Stone':50,'Wood':30,'Hide':20}, 'url':'https://www.dododex.com/item/1726/smithy'},
 'spyglass': {'name':'Spyglass', 'station':'Inventory', 'yield':1, 'ingredients':{'Wood':5,'Hide':10,'Fiber':10,'Crystal':2}, 'url':'https://ark.wiki.gg/wiki/Spyglass'},
 'narcotic_mortar': {'name':'Narcotic', 'station':'Mortar and Pestle', 'yield':1, 'ingredients':{'Narcoberry':5,'Spoiled Meat':1}, 'url':'https://ark.wiki.gg/wiki/Mortar_and_Pestle'},
 'narcotic_chemistry': {'name':'Narcotic', 'station':'Chemistry Bench', 'yield':6, 'ingredients':{'Narcoberry':20,'Spoiled Meat':4}, 'url':'https://ark.wiki.gg/wiki/Chemistry_Bench'},
}

def craft(recipe_id, quantity, inventory=None, expand_ingots=False):
    if not isinstance(recipe_id, str) or recipe_id not in RECIPES: raise ValueError('Unknown recipe')
    quantity=_integer(quantity,'quantity',1,100000)
    if not isinstance(expand_ingots,bool): raise ValueError('expand_ingots must be boolean')
    if inventory is None: inventory={}
    if not isinstance(inventory,dict) or len(inventory)>30: raise ValueError('inventory must be an object with at most 30 entries')
    stock={}
    for name, count in inventory.items():
        if not isinstance(name,str) or len(name)>100: raise ValueError('invalid inventory item name')
        stock[name]=_integer(count,'inventory '+name,0,100000000)
    r=RECIPES[recipe_id]; batches=ceil(quantity/r['yield']); immediate={k:v*batches for k,v in r['ingredients'].items()}
    gross=dict(immediate)
    if expand_ingots and 'Metal Ingot' in gross:
        # Existing ingots should be consumed before expanding the remaining required ingots.
        needed=gross.pop('Metal Ingot'); used=min(needed,stock.get('Metal Ingot',0)); stock['Metal Ingot']=stock.get('Metal Ingot',0)-used
        if needed-used: gross['Metal']=gross.get('Metal',0)+2*(needed-used)
    missing={name:max(0,qty-stock.get(name,0)) for name,qty in gross.items()}
    return {'recipe':recipe_id,'name':r['name'],'station':r['station'],'requested':quantity,'batches':batches,'produced':batches*r['yield'],'surplus':batches*r['yield']-quantity,'immediate_ingredients':immediate,'requirements':gross,'shortfall':missing,'source':r['url'],'notes':'Base recipes only; no fuel, alternatives, stations, spoilage, mods or custom rates.'}

def craft_queue(lines, inventory=None, expand_ingots=False):
    """Aggregate matching recipe variants before batching; subtract inventory once.

    Ingot output from a queued recipe is not transferred to other queue lines.
    """
    if not isinstance(lines,list) or not 1<=len(lines)<=20: raise ValueError('Queue must contain 1–20 lines')
    if not isinstance(expand_ingots,bool): raise ValueError('expand_ingots must be boolean')
    if inventory is None: inventory={}
    if not isinstance(inventory,dict) or len(inventory)>30: raise ValueError('inventory must be an object with at most 30 entries')
    stock={}
    for name,count in inventory.items():
        if not isinstance(name,str) or len(name)>100: raise ValueError('invalid inventory item name')
        stock[name]=_integer(count,'inventory '+name,0,100000000)
    grouped={}
    for line in lines:
        if not isinstance(line,dict): raise ValueError('Queue line must be an object')
        rid=line.get('recipe')
        if not isinstance(rid,str) or rid not in RECIPES: raise ValueError('Unknown recipe')
        quantity=_integer(line.get('quantity'),'quantity',1,100000)
        grouped[rid]=grouped.get(rid,0)+quantity
        if grouped[rid]>100000: raise ValueError('Combined quantity per recipe exceeds 100000')
    requirements={}; plans=[]
    for rid,qty in grouped.items():
        plan=craft(rid,qty)
        plans.append({k:plan[k] for k in ('recipe','name','station','requested','batches','produced','surplus','source')})
        for name,amount in plan['requirements'].items(): requirements[name]=requirements.get(name,0)+amount
    used_ingots=0
    if expand_ingots and 'Metal Ingot' in requirements:
        needed=requirements.pop('Metal Ingot')
        used_ingots=min(needed,stock.get('Metal Ingot',0))
        remaining=needed-used_ingots
        if remaining: requirements['Metal']=requirements.get('Metal',0)+2*remaining
    shortfall={name:max(0,amount-stock.get(name,0)) for name,amount in requirements.items()}
    return {'lines':plans,'requirements':requirements,'shortfall':shortfall,'owned_ingots_used':used_ingots,
            'notes':'Base recipes only; no fuel, substitutions, station costs, mods or custom rates. Queued outputs are not shared as inputs to other queue lines.'}
