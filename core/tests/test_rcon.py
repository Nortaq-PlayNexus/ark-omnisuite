import socket, struct, threading, unittest
from unittest.mock import patch
from core.rcon import execute, _packet, _receive_packet, RconAuthError, RconProtocolError, RconError

class FakeConnection:
    def __init__(self, scenario='success'):
        self.client,self.server=socket.socketpair();self.scenario=scenario;self.errors=[]
        self.thread=threading.Thread(target=self.run,daemon=True);self.thread.start()
    def run(self):
        try:
            auth=_receive_packet(self.server)
            if auth != (41,3,'secret'): raise AssertionError(auth)
            if self.scenario=='reject': self.server.sendall(_packet(-1,2,''));return
            self.server.sendall(_packet(41,0,''))
            response=_packet(41,2,'')
            # Deliberately fragmented wire writes
            for part in [response[:2],response[2:6],response[6:]]: self.server.sendall(part)
            cmd=_receive_packet(self.server)
            if cmd != (42,2,'listplayers'): raise AssertionError(cmd)
            if self.scenario=='wrongid': self.server.sendall(_packet(999,0,'not a player list'));return
            self.server.sendall(_packet(42,0,'No Players Connected'))
        except Exception as e: self.errors.append(e)
        finally: self.server.close()
    def close(self): self.thread.join(2)

class RconTests(unittest.TestCase):
    def test_success_fragmented_and_auth_preamble(self):
        fake=FakeConnection()
        with patch('core.rcon.socket.create_connection',return_value=fake.client):
            result=execute('server',27020,'secret','listplayers')
        fake.close();self.assertFalse(fake.errors);self.assertEqual(result['response'],'No Players Connected');self.assertIsNone(result['complete'])
    def test_auth_failure(self):
        fake=FakeConnection('reject')
        with patch('core.rcon.socket.create_connection',return_value=fake.client):
            with self.assertRaises(RconAuthError): execute('server',27020,'secret','listplayers')
        fake.close()
    def test_request_mismatch(self):
        fake=FakeConnection('wrongid')
        with patch('core.rcon.socket.create_connection',return_value=fake.client):
            with self.assertRaises(RconProtocolError): execute('server',27020,'secret','listplayers')
        fake.close()
    def test_invalid_packet_length(self):
        a,b=socket.socketpair()
        try:
            b.sendall(struct.pack('<i',9))
            with self.assertRaises(RconProtocolError): _receive_packet(a)
        finally: a.close();b.close()
    def test_invalid_terminator(self):
        a,b=socket.socketpair()
        try:
            b.sendall(struct.pack('<iii',10,1,0)+b'xx')
            with self.assertRaises(RconProtocolError): _receive_packet(a)
        finally: a.close();b.close()
    def test_input_validation(self):
        for cmd in ['','x\x00y','x\ny']:
            with self.assertRaises(ValueError): execute('server',27020,'secret',cmd)
        with self.assertRaises(ValueError): execute('server',0,'secret','listplayers')
    def test_timeout(self):
        with patch('core.rcon.socket.create_connection',side_effect=socket.timeout):
            with self.assertRaises(RconError): execute('server',27020,'secret','listplayers')
