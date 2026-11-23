"""Interactive local-only RCON CLI; not connected to the web or Discord app."""
import argparse, getpass, os, sys
from .rcon import execute, RconError

def main():
    p=argparse.ArgumentParser(description='Send one command to a trusted ASE RCON server. RCON is unencrypted; use a protected network.')
    p.add_argument('--host',required=True);p.add_argument('--port',type=int,default=27020)
    p.add_argument('--command',default='listplayers',help='Admin command; defaults to listplayers. Commands can change the server.')
    p.add_argument('--timeout',type=float,default=5)
    args=p.parse_args()
    password=os.environ.get('ARK_RCON_PASSWORD') or getpass.getpass('RCON password: ')
    try:
        result=execute(args.host,args.port,password,args.command,args.timeout)
        print(result['response']);print('WARNING: '+result['notice'],file=sys.stderr)
    except (RconError,ValueError) as e: print('RCON: '+str(e),file=sys.stderr);return 1
    return 0
if __name__=='__main__': raise SystemExit(main())
