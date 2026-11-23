"""Minimal Source RCON transport for trusted ASE servers, not an HTTP endpoint.

Specification: https://developer.valvesoftware.com/wiki/Source_RCON_Protocol
RCON is plaintext and has administrative authority. Use only over a protected network.
Only the first response packet is returned: multi-packet replies are NOT supported.
"""
import socket
import struct

MAX_PACKET = 4 * 1024 * 1024
AUTH_ID, COMMAND_ID = 41, 42

class RconError(Exception): pass
class RconAuthError(RconError): pass
class RconProtocolError(RconError): pass


def _packet(request_id, kind, body):
    if not isinstance(body, str) or '\x00' in body: raise ValueError('RCON body must be text without NUL bytes')
    content=body.encode('utf-8')
    if len(content) > 4096: raise ValueError('RCON input is too long')
    payload=struct.pack('<ii',request_id,kind)+content+b'\x00\x00'
    return struct.pack('<i',len(payload))+payload


def _receive_exact(sock,n):
    parts=[]
    while n:
        block=sock.recv(n)
        if not block: raise RconProtocolError('Connection closed during a packet')
        parts.append(block);n-=len(block)
    return b''.join(parts)


def _receive_packet(sock):
    size=struct.unpack('<i',_receive_exact(sock,4))[0]
    if not 10 <= size <= MAX_PACKET: raise RconProtocolError('Invalid RCON packet size')
    data=_receive_exact(sock,size)
    if data[-2:] != b'\x00\x00' or b'\x00' in data[8:-2]: raise RconProtocolError('Malformed RCON packet')
    request_id,kind=struct.unpack('<ii',data[:8])
    try: body=data[8:-2].decode('utf-8')
    except UnicodeDecodeError as e: raise RconProtocolError('Invalid response encoding') from e
    return request_id,kind,body


def execute(host,port,password,command,timeout=5):
    """Connect, authenticate, run exactly one command and return the first packet.

    Response completeness is not known for a Source server that fragments output.
    A fresh connection is opened for each command; timeout covers each socket operation.
    Never expose this function to unauthenticated web callers.
    """
    if not isinstance(host,str) or not host.strip(): raise ValueError('host required')
    if isinstance(port,bool) or not isinstance(port,int) or not 1<=port<=65535: raise ValueError('port must be 1–65535')
    if not isinstance(password,str) or not password: raise ValueError('password required')
    if not isinstance(command,str) or not command.strip() or '\n' in command or '\r' in command: raise ValueError('one non-empty command required')
    if isinstance(timeout,bool) or not isinstance(timeout,(int,float)) or not 0 < timeout <= 60: raise ValueError('timeout must be >0 and <=60')
    auth_packet=_packet(AUTH_ID,3,password); command_packet=_packet(COMMAND_ID,2,command)
    try:
        with socket.create_connection((host,port),timeout=timeout) as sock:
            sock.settimeout(timeout);sock.sendall(auth_packet)
            # Source servers may send an empty response-value before AUTH_RESPONSE.
            for _ in range(5):
                rid,kind,body=_receive_packet(sock)
                if kind == 0 and body == '': continue
                if kind == 2 and rid == -1: raise RconAuthError('RCON authentication rejected')
                if kind == 2 and rid == AUTH_ID: break
                raise RconProtocolError('Unexpected authentication response')
            else: raise RconProtocolError('Authentication response not received')
            sock.sendall(command_packet)
            rid,kind,body=_receive_packet(sock)
            if rid == -1: raise RconAuthError('RCON command rejected')
            if rid != COMMAND_ID or kind != 0: raise RconProtocolError('Unexpected command response')
            return {'response':body,'complete':None,'notice':'Only the first response packet is read; output may be incomplete.'}
    except (socket.timeout,TimeoutError) as exc: raise RconError('RCON connection or response timed out') from exc
    except OSError as exc: raise RconError(f'RCON network error: {exc.__class__.__name__}') from exc
