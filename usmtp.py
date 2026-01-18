#usmtp.py

import usocket as socket
import time

class SMTP:
    def __init__(self, host, port=587, ssl=False):
        self.host = host
        self.port = port
        self.sock = socket.socket()
        addr = socket.getaddrinfo(host, port)[0][-1]
        self.sock.connect(addr)
        self._drain() # Clear the initial connection greeting
        if ssl:
            import ussl
            self.sock = ussl.wrap_socket(self.sock)

    def _send(self, str):
        self.sock.send(str.encode() + b'\r\n')

    def _recv(self):
        return self.sock.readline()

    def _drain(self):
        """Continues reading lines as long as the 4th character is a '-'"""
        while True:
            line = self._recv()
            print("Server:", line) # Watch the conversation in Thonny
            if line[3:4] != b'-':
                break

    def starttls(self):
        self._send('EHLO smtp.gmail.com')
        self._drain()
        
        self._send('STARTTLS')
        resp = self._recv()
        print("STARTTLS Response:", resp)
        
        if not resp.startswith(b'220'):
            # If we still get a 250, try to drain one more time and check next line
            self._drain()
            resp = self._recv()
            
        try:
            import ssl as ussl
        except ImportError:
            import ussl
            
        self.sock = ussl.wrap_socket(self.sock, server_hostname=self.host)

    def login(self, user, password):
        self._send('EHLO smtp.gmail.com')
        self._drain()
        
        import ubinascii
        self._send('AUTH LOGIN')
        self._recv()
        self._send(ubinascii.b2a_base64(user.encode()).decode().strip())
        self._recv()
        self._send(ubinascii.b2a_base64(password.encode()).decode().strip())
        resp = self._recv()
        if not resp.startswith(b'235'):
            raise Exception('Login failed: ' + resp.decode())

    def send_mail(self, from_addr, to_addr, msg):
        self._send('MAIL FROM:<' + from_addr + '>')
        self._recv()
        self._send('RCPT TO:<' + to_addr + '>')
        self._recv()
        self._send('DATA')
        self._recv()
        self._send(msg)
        self._send('.')
        self._recv()

    def quit(self):
        self._send('QUIT')
        self.sock.close()
