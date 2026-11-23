"""Local prototype server; never expose this unauthenticated service publicly."""
import argparse, json, os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from core import ingots, mutation_odds, advisor, readiness
from core.crafting import craft, craft_queue, RECIPES
from core.breeding import inheritance_odds
from core.forge import refining_forge
from core.config import ini_snippets
from core.roi import rank_tames
from core.schedule import compare_windows
from core.survivor_tools import broodmother_manifest, incubation_mixer, waypoint_route
ROOT = Path(__file__).parent / 'public'
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs): super().__init__(*args, directory=str(ROOT), **kwargs)
    def do_POST(self):
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size < 1 or size > 16384: raise ValueError('Request body must be 1–16384 bytes')
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict): raise ValueError('Expected JSON object')
            if self.path == '/api/ingots': result=ingots(data.get('count'))
            elif self.path == '/api/mutation': result=mutation_odds(data.get('offspring'),data.get('mother',0),data.get('father',0))
            elif self.path == '/api/windows': result=compare_windows(data.get('windows'))
            elif self.path == '/api/tribute': result=broodmother_manifest(data.get('difficulty'),data.get('runs',1),data.get('inventory'))
            elif self.path == '/api/incubation': result=incubation_mixer(data.get('eggs'))
            elif self.path == '/api/route': result=waypoint_route(data.get('start'),data.get('waypoints'),data.get('return_to_start',False))
            elif self.path == '/api/inheritance': result=inheritance_odds(data.get('differing_stats'),data.get('events'))
            elif self.path == '/api/forge': result=refining_forge(data.get('ingots'),data.get('fuel'))
            elif self.path == '/api/queue': result=craft_queue(data.get('lines'),data.get('inventory'),data.get('expand_ingots',False))
            elif self.path == '/api/roi': result=rank_tames(data.get('candidates'))
            elif self.path == '/api/craft': result=craft(data.get('recipe'),data.get('quantity'),data.get('inventory'),data.get('expand_ingots',False))
            elif self.path == '/api/config': result=ini_snippets(data)
            elif self.path == '/api/readiness': result=readiness(data.get('checks'))
            elif self.path == '/api/advisor': result=advisor(data.get('minutes'),data.get('metal_shortage'),data.get('raid_soon'))
            else: self.send_error(404); return
            self.respond(200, result)
        except (ValueError, TypeError, json.JSONDecodeError) as exc: self.respond(400, {'error': str(exc)})
    def respond(self, status, data):
        body=json.dumps(data).encode(); self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(body))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(body)
if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--host',default='127.0.0.1'); parser.add_argument('--port',type=int,default=8000); args=parser.parse_args()
    print(f'Obelisk Console on http://{args.host}:{args.port}', flush=True)
    ThreadingHTTPServer((args.host,args.port),Handler).serve_forever()
