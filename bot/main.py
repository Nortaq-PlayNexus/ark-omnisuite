"""OMNI Discord slash commands backed by validated shared planning models."""
import argparse
import asyncio
import os
from pathlib import Path
from core import ingots, mutation_odds, advisor, readiness
from core.breeding import inheritance_odds
from core.config import ini_snippets
from core.crafting import craft, craft_queue, RECIPES
from core.forge import refining_forge
from core.roi import rank_tames
from core.schedule import compare_windows
from core.survivor_tools import broodmother_manifest, incubation_mixer, waypoint_route, BROODMOTHER_ARTIFACTS, BROODMOTHER_APEX
from bot import parsing
from bot.store import PlanStore


def dry_run():
    assert ingots(15)['metal']==30
    assert mutation_odds(1)['probability_percent']==7.314
    assert craft('smithy',1)['requirements']['Metal Ingot']==5
    assert refining_forge(150,'wood')['fuel_units']==100
    assert broodmother_manifest('beta')['required']['Argentavis Talon']==5
    assert inheritance_odds(2,1)['per_event_percent']==30.25
    assert craft_queue(parsing.queue('smithy|1;spyglass|1'))['requirements']['Wood']==35
    assert incubation_mixer(parsing.eggs('A|10|20;B|20|30'))['covered']==2
    assert waypoint_route({'lat':0,'lon':0},parsing.pins('A|3|4'))['grid_distance']==5
    assert compare_windows(parsing.windows('A|2027-01-01T00:00Z|2027-01-01T01:00Z'))['conflicts']==[]
    print('Dry run OK: shared core and command parsers validated. Run tests/test_bot.py with discord.py installed for mocked command checks.')
    print('Offline dry run does not verify Discord registration, delivery or credentials.')


def create_client(db_path, guild_id=None):
    import discord
    from discord import app_commands
    if guild_id is not None and (isinstance(guild_id,bool) or not isinstance(guild_id,int) or guild_id<=0): raise ValueError('DISCORD_GUILD_ID must be a positive integer')
    store=PlanStore(db_path)
    class Client(discord.Client):
        async def setup_hook(self):
            if guild_id:
                guild=discord.Object(id=guild_id)
                tree.copy_global_to(guild=guild)
                await tree.sync(guild=guild)
                print('OMNI synced to configured test guild',flush=True)
            else:
                await tree.sync()
                print('OMNI globally synced',flush=True)
    client=Client(intents=discord.Intents.default(),allowed_mentions=discord.AllowedMentions.none())
    tree=app_commands.CommandTree(client)
    client.omni_tree=tree
    safe=lambda value:discord.utils.escape_mentions(discord.utils.escape_markdown(str(value)))
    colors={'amber':0xF5A623,'cyan':0x37D6F0,'purple':0xA86BFF}
    def embed(title,text,color='cyan'):
        if len(text)>4096: raise ValueError('Result too large; reduce the number or length of inputs')
        return discord.Embed(title=title,description=text,color=colors[color])
    async def calculate(interaction,title,fn,format_result,public=False,color='cyan'):
        try:
            result=fn();message=embed(title,format_result(result),color)
            await interaction.response.send_message(embed=message,ephemeral=not public,allowed_mentions=discord.AllowedMentions.none())
        except ValueError as exc:
            await interaction.response.send_message(embed=embed('OMNI // INPUT ERROR',safe(exc),'amber'),ephemeral=True,allowed_mentions=discord.AllowedMentions.none())
    @tree.error
    async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        print('OMNI interaction error:',type(error).__name__,flush=True)
        kwargs={'content':'OMNI could not complete this request. Check the input or contact the bot operator.','ephemeral':True,'allowed_mentions':discord.AllowedMentions.none()}
        if interaction.response.is_done(): await interaction.followup.send(**kwargs)
        else: await interaction.response.send_message(**kwargs)

    def checked_inventory(value, allowed):
        stock=parsing.inventory(value)
        unknown=[name for name in stock if name not in allowed]
        if unknown: raise ValueError('Unknown item name(s): '+', '.join(unknown)+'. Item names are case-sensitive.')
        return stock
    @tree.command(name='omni',description='OMNI command guide and limitations')
    async def omni(interaction: discord.Interaction):
        text=('**CORE** · /ingots /forge /mutation /inheritance /craft /tribute\n'
              '**PLANNING** · /queue /incubate /route /windows /rates /readiness /advisor /tamecompare\n'
              '**PRIVATE NOTES** · /plans add, list, edit, done, remove\n\n'
              'Structured examples: `smithy|2;spyglass|1` (queue); `Egg A|10|20;Egg B|20|30` (°C); '
              '`Base|50|50;Metal|30|70` (lat/lon); `Raid|2027-01-01T10:00Z|2027-01-01T12:00Z` (UTC). '
              'For stock use `Wood|20;Stone|5`. Calculations are private unless public is selected; notes are always private. '
              'No live ARK server, taming dataset, alerts, web sync or RCON. See README for limits.')
        await interaction.response.send_message(embed=embed('OMNI // SURVIVOR TERMINAL',text,'amber'),ephemeral=True,allowed_mentions=discord.AllowedMentions.none())

    @tree.command(name='ingots',description='Metal needed for ingots; fuel excluded')
    async def ingot_command(interaction: discord.Interaction,count:int,public:bool=False):
        await calculate(interaction,'REFINING // METAL',lambda:ingots(count),lambda r:f"{r['metal']} Metal for {r['ingots']} ingots. Fuel excluded.\nhttps://ark.fandom.com/wiki/Metal_Ingot",public,'amber')
    @tree.command(name='mutation',description='Mutation odds for independent breeding events')
    async def mutation_command(interaction: discord.Interaction,breeding_events:int,mother:int=0,father:int=0,public:bool=False):
        await calculate(interaction,'BREEDING // MUTATION',lambda:mutation_odds(breeding_events,mother,father),lambda r:f"{r['probability_percent']}% · {r['assumption']}. Twins/triplets are not independent events.\nhttps://ark.wiki.gg/wiki/Mutations",public,'purple')
    @tree.command(name='inheritance',description='ASE chance to inherit higher parental stats')
    async def inheritance_command(interaction: discord.Interaction,differing_stats:int,breeding_events:int,public:bool=False):
        await calculate(interaction,'BREEDING // INHERITANCE',lambda:inheritance_odds(differing_stats,breeding_events),lambda r:f"{r['per_event_percent']}% per event; {r['at_least_one_percent']}% across {r['events']} independent events. Expected {r['expected_events']} events per success, not a guarantee.\n{r['assumption']}\n{r['source']}",public,'purple')
    @tree.command(name='forge',description='ASE refining forge metal and fuel baseline')
    @app_commands.choices(fuel=[app_commands.Choice(name=x,value=y) for x,y in [('Wood','wood'),('Thatch','thatch'),('Sparkpowder','sparkpowder'),('AnglerGel','anglergel')]])
    async def forge_command(interaction: discord.Interaction,ingot_count:int,fuel:str,public:bool=False):
        await calculate(interaction,'REFINING // FORGE',lambda:refining_forge(ingot_count,fuel),lambda r:f"{r['metal']} Metal → {r['ingots']} ingots in {r['time_seconds']} seconds. Fuel: {r['fuel_units']} {r['fuel']}.\n{r['assumptions']}\n{r['source']}",public,'amber')
    @tree.command(name='craft',description='Materials for one supported ASE recipe')
    @app_commands.choices(recipe=[app_commands.Choice(name=x,value=y) for x,y in [('Smithy','smithy'),('Spyglass','spyglass'),('Metal Ingot','metal_ingot'),('Narcotic · Mortar','narcotic_mortar'),('Narcotic · Chemistry Bench','narcotic_chemistry')]])
    async def craft_command(interaction: discord.Interaction,recipe:str,quantity:int,expand_ingots:bool=False,public:bool=False):
        await calculate(interaction,'CRAFTING // MATERIALS',lambda:craft(recipe,quantity,expand_ingots=expand_ingots),lambda r:f"{r['name']} ×{r['produced']} ({r['batches']} batches; {r['surplus']} surplus)\nStation: {r['station']}\n"+'\n'.join(f"{v} × {k}" for k,v in r['requirements'].items())+f"\n{r['notes']}\n{r['source']}",public)
    @tree.command(name='tribute',description='The Island Broodmother tribute requirements')
    @app_commands.choices(difficulty=[app_commands.Choice(name=x,value=x.lower()) for x in ('Gamma','Beta','Alpha')])
    async def tribute_command(interaction: discord.Interaction,difficulty:str,runs:int=1,stock:str='',public:bool=False):
        def fmt(r): return f"{r['difficulty'].title()} · {r['runs']} run(s)\n"+'\n'.join(f"{k}: {v} required → {r['missing'][k]} missing" for k,v in r['required'].items())+f"\n{r['notes']}\n{r['source']}"
        await calculate(interaction,'THE ISLAND // TRIBUTE',lambda:broodmother_manifest(difficulty,runs,checked_inventory(stock,set(BROODMOTHER_ARTIFACTS+BROODMOTHER_APEX))),fmt,public)
    @tree.command(name='queue',description='Combine up to 5 supported recipe lines and shared stock')
    @app_commands.describe(items='recipe_id|quantity;recipe_id|quantity',stock='Optional: item name|quantity;item name|quantity')
    async def queue_command(interaction: discord.Interaction,items:str,stock:str='',expand_ingots:bool=False,public:bool=False):
        def fmt(r):
            lines='\n'.join(f"{x['name']} ({x['station']}): {x['requested']} requested, {x['produced']} produced · {x['source']}" for x in r['lines'])
            mats='\n'.join(f"{name}: {amount} required → {r['shortfall'][name]} missing" for name,amount in r['requirements'].items())
            return f"{lines}\n\n{mats}\nOwned ingots used: {r['owned_ingots_used']}.\n{r['notes']}"
        await calculate(interaction,'CRAFTING // QUEUE',lambda:craft_queue(parsing.queue(items),checked_inventory(stock,{name for recipe in RECIPES.values() for name in recipe['ingredients']}),expand_ingots),fmt,public)
    @tree.command(name='incubate',description='Find overlap among manually supplied temperature ranges')
    @app_commands.describe(ranges='name|min_C|max_C;name|min_C|max_C')
    async def incubate_command(interaction: discord.Interaction,ranges:str,public:bool=False):
        await calculate(interaction,'BREEDING // RANGE MIXER',lambda:incubation_mixer(parsing.eggs(ranges)),lambda r:f"{r['temperature_c']} °C covers {r['covered']}/{r['total']} ranges.\nIncluded: "+', '.join(map(safe,r['included']))+'\nOutside: '+(', '.join(map(safe,r['excluded'])) or 'none')+f"\n{r['notes']}",public,'purple')
    @tree.command(name='route',description='Shortest straight-grid route through up to 8 manual pins')
    @app_commands.describe(pins='name|latitude|longitude;name|latitude|longitude')
    async def route_command(interaction: discord.Interaction,start_lat:float,start_lon:float,pins:str,return_to_start:bool=False,public:bool=False):
        def fmt(r):
            lines='\n'.join(f"{i}. {safe(p['name'])} ({p['lat']}, {p['lon']}) · leg {r['legs'][i-1]['grid_distance']}" for i,p in enumerate(r['ordered'],1))
            back=f"\nReturn leg: {r['legs'][-1]['grid_distance']}" if r['return_to_start'] else ''
            return f"{r['grid_distance']} grid units\n{lines}{back}\n{r['notes']}"
        await calculate(interaction,'ATLAS // ROUTE SKETCH',lambda:waypoint_route({'lat':start_lat,'lon':start_lon},parsing.pins(pins),return_to_start),fmt,public)
    @tree.command(name='windows',description='Compare up to 4 manual time windows and make Discord timestamps')
    @app_commands.describe(events='name|ISO start with Z/offset|ISO end with Z/offset;...')
    async def windows_command(interaction: discord.Interaction,events:str,public:bool=False):
        def fmt(r):
            pairs='\n'.join(f"{safe(c['first'])} #{c['first_index']+1} ↔ {safe(c['second'])} #{c['second_index']+1} · {c['overlap_seconds']} sec" for c in r['conflicts']) or 'None'
            times='\n'.join(f"{safe(w['name'])} #{w['index']+1}: {w['discord_start']} → {w['discord_end']}" for w in r['windows'])
            return f"**Overlaps**\n{pairs}\n\n**Time windows**\n{times}\n{r['notes']} Tags use whole seconds."
        await calculate(interaction,'OPERATIONS // WINDOWS',lambda:compare_windows(parsing.windows(events)),fmt,public)
    @tree.command(name='rates',description='Preview six ASE server rate INI settings; no changes made')
    async def rates_command(interaction: discord.Interaction,taming:float=1.0,xp:float=1.0,harvest:float=1.0,hatch:float=1.0,mature:float=1.0,mating:float=1.0,public:bool=False):
        def fmt(r): return f"**GameUserSettings.ini**\n```ini\n{r['gameusersettings']}```\n**Game.ini**\n```ini\n{r['game']}```\n{r['notes']}\n{r['source']}"
        await calculate(interaction,'SERVER // RATES PREVIEW',lambda:ini_snippets(dict(taming=taming,xp=xp,harvest=harvest,hatch=hatch,mature=mature,mating=mating)),fmt,public)
    @tree.command(name='readiness',description='Score five self-reported preparation checks')
    async def readiness_command(interaction: discord.Interaction,turrets:bool,ammo:bool,fuel:bool,walls:bool,tribe_plan:bool,public:bool=False):
        await calculate(interaction,'TRIBE // READINESS',lambda:readiness([turrets,ammo,fuel,walls,tribe_plan]),lambda r:f"{r['score']}/100 · {r['checked']}/{r['total']} checked. {r['method']}.",public)
    @tree.command(name='advisor',description='Create a simple session priority list')
    async def advisor_command(interaction: discord.Interaction,minutes:int,metal_shortage:bool=False,raid_soon:bool=False,public:bool=False):
        await calculate(interaction,'OPERATIONS // ADVISOR',lambda:advisor(minutes,metal_shortage,raid_soon),lambda r:'\n'.join(f"• {task}" for task in r['tasks'])+f"\n{r['note']}",public,'amber')
    @tree.command(name='tamecompare',description='Rank candidates using your utility and time estimates')
    @app_commands.describe(candidates='name|utility score|estimated hours;name|score|hours')
    async def tamecompare_command(interaction: discord.Interaction,candidates:str,public:bool=False):
        await calculate(interaction,'TAMES // USER-DEFINED ROI',lambda:rank_tames(parsing.tames(candidates)),lambda r:'\n'.join(f"{i}. {safe(x['name'])}: {x['utility_per_hour']} utility/hour" for i,x in enumerate(r['ranking'],1))+f"\n{r['method']}",public,'purple')

    plans=app_commands.Group(name='plans',description='Private notes scoped to you and this server or DM')
    async def plan_action(interaction,action):
        await interaction.response.defer(ephemeral=True,thinking=True)
        try:
            text=await asyncio.to_thread(action)
            message=embed('OMNI // PRIVATE PLANS',text,'purple')
        except ValueError as exc: message=embed('OMNI // INPUT ERROR',safe(exc),'amber')
        except Exception as exc:
            print('OMNI storage error:',type(exc).__name__,flush=True)
            message=embed('OMNI // STORAGE ERROR','Unable to access local storage. Contact the bot operator.','amber')
        await interaction.followup.send(embed=message,ephemeral=True,allowed_mentions=discord.AllowedMentions.none())
    def scope(interaction): return (interaction.guild_id or 0,interaction.user.id)
    @plans.command(name='add',description='Add a private note, up to 15 per server or DM')
    async def plan_add(interaction: discord.Interaction,text:str):
        def action(): return f"Added #{store.add(*scope(interaction),text)}. Use /plans list to view."
        await plan_action(interaction,action)
    @plans.command(name='list',description='List your private notes in this server or DM')
    async def plan_list(interaction: discord.Interaction,page:int=1):
        def action():
            records=store.list(*scope(interaction));pages=max(1,(len(records)+4)//5)
            if page<1 or page>pages: raise ValueError(f'Page must be 1–{pages}')
            current=records[(page-1)*5:page*5]
            listing='\n'.join(f"#{r['id']} · {'DONE' if r['done'] else 'OPEN'} · {safe(r['text'])}" for r in current) if current else 'No notes yet. Use /plans add.'
            return f"Page {page}/{pages} · {len(records)} notes\n{listing}\n\nStored on the bot host; not shared with the web app."
        await plan_action(interaction,action)
    @plans.command(name='edit',description='Edit one of your private notes')
    async def plan_edit(interaction: discord.Interaction,note_id:int,text:str):
        def action(): return f"Updated #{note_id}." if store.edit(*scope(interaction),note_id,text) else 'Note not found in your private list.'
        await plan_action(interaction,action)
    @plans.command(name='done',description='Mark your private note complete or reopen it')
    async def plan_done(interaction: discord.Interaction,note_id:int,complete:bool=True):
        def action(): return f"#{note_id} marked {'complete' if complete else 'open'}." if store.set_done(*scope(interaction),note_id,complete) else 'Note not found in your private list.'
        await plan_action(interaction,action)
    @plans.command(name='remove',description='Permanently remove one of your private notes')
    async def plan_remove(interaction: discord.Interaction,note_id:int):
        def action(): return f"Removed #{note_id}." if store.delete(*scope(interaction),note_id) else 'Note not found in your private list.'
        await plan_action(interaction,action)
    tree.add_command(plans)
    return client


def main():
    p=argparse.ArgumentParser();p.add_argument('--dry-run',action='store_true');args=p.parse_args()
    if args.dry_run: dry_run();return
    try: import discord
    except ImportError: raise SystemExit('Install discord.py: pip install -r bot/requirements.txt')
    token=os.environ.get('DISCORD_TOKEN')
    if not token: raise SystemExit('DISCORD_TOKEN is required')
    guild=os.environ.get('DISCORD_GUILD_ID')
    if guild:
        try: guild=int(guild)
        except ValueError: raise SystemExit('DISCORD_GUILD_ID must be a positive integer')
    db=os.environ.get('OMNI_DB_PATH',str(Path(__file__).resolve().parent.parent/'data'/'omni.sqlite3'))
    try: client=create_client(db,guild)
    except ValueError as e: raise SystemExit(str(e))
    client.run(token)
if __name__=='__main__': main()
