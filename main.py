import http.server
import socketserver
import ssl
import base64
from httpHandler import HttpRequestHandler
import argparse
from time import sleep
from hardwareLogic import led_on, led_off

local_ip = "0.0.0.0"

class StreamingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    key = ''
    allow_reuse_address = True
    daemon_threads = True
    def get_auth_key(self):
        return self.key
    
    def set_auth(self, username, password):
        self.key = base64.b64encode(
            bytes('%s:%s' % (username, password), 'utf-8')).decode('ascii')

try:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="define what port the server is running on, default 8443", default=8443, type=int)
    parser.add_argument("--cert", help="define server cert for TLS")
    parser.add_argument("--key", help="define what port the server is running on, default 8443")
    parser.add_argument("-u", "--username", help="define username for basic authentication")
    parser.add_argument("-p", "--password", help="define password for basic authentication")
    args = parser.parse_args()
    if bool(args.key) ^ bool(args.cert):
        parser.error('cert and key must be given together')
        
    if bool(args.password) ^ bool(args.username):
        parser.error('username and password must be given together')
        
    with StreamingServer((local_ip, args.port), HttpRequestHandler) as httpd:
        print("Serving at IP", local_ip, "and port", args.port)
        if args.cert and args.key:
            httpd.socket = ssl.wrap_socket (httpd.socket, 
                keyfile=args.key,  #/Users/filipbang/Documents/camera/key.pem
                certfile=args.cert, server_side=True) #/Users/filipbang/Documents/camera/cert.pem
        else:
            print('TLS not used')
        
        # flash light to confirm server about the be started
        for i in range(3):
            led_on()
            sleep(1)
            led_off()
        if(args.username and args.password):
            httpd.set_auth(args.username, args.password)
        else: 
            print('No basic authentication set')
        httpd.serve_forever()    
        
finally:
    # picam2.stop_recording()
    print("finally")