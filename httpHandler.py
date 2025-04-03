import http.server
from cameraLogic import output
from hardwareLogic import led_off, led_on

class HttpRequestHandler(http.server.BaseHTTPRequestHandler):
    def return_file(self): 
        print("path: ", self.path)
        if '..' in self.path:
            # directory traversal is not allowed
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b'403 .. is not allowed')
            return
        try:
            with open('/opt/public/'+self.path, 'rb') as f:
                data = f.read()
            self.send_response(200)
            if self.path.endswith('js'): 
                self.send_header('Content-Type', 'text/javascript')
                self.send_header('Content-Length', len(data))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 not found')
        except PermissionError:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b'403 no permission')
        except Exception:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'500 error')
    def return_401(self): 
        self.send_response(401)
        self.send_header(
            'WWW-Authenticate', 'Basic realm="Demo Realm"')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'Invalid credentials\r\n')
        
    def return_stream(self): 
        self.send_response(200)
        self.send_header('Age', 0)
        self.send_header('Cache-Control', 'no-cache, private')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
        self.end_headers()
        try:
            while True:
                with output.condition:
                    output.condition.wait()
                    frame = output.frame
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(frame))
                self.end_headers()
                self.wfile.write(frame)
                self.wfile.write(b'\r\n')
        except Exception as e:
            print("Stream stopped:", e)
            
    def return_temp(self):
        with open('/sys/class/thermal/thermal_zone0/temp', 'rb') as f: 
            temp = f.read()
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(temp) 
        self.wfile.write(b'\r\n')
    def check_authorization(self):
        key = self.server.get_auth_key()
        if key == "": 
            return True
        if self.headers.get('Authorization') == None:
            self.send_response(401)
            self.send_header(
                'WWW-Authenticate', 'Basic realm="Demo Realm"')
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            self.wfile.write(b'No auth header received\r\n')

        elif self.headers.get('Authorization') == 'Basic ' + str(key):
            return True

    def do_GET(self):
        if self.check_authorization():
            if self.path == '/':
                self.send_response(301)
                self.send_header('Location', '/index.html')
                self.end_headers()
            elif self.path == '/ledon':
                led_on()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'ok\r\n')
            elif self.path == '/ledoff':
                led_off()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'ok\r\n')
            elif self.path == '/temp':
                self.return_temp()
            elif self.path == '/stream.mjpg':
                self.return_stream()
            else:
                self.return_file()
        else:
            self.return_401()
