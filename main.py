import http.server
import socketserver
from threading import Condition
import ssl
from picamera2 import Picamera2, MappedArray
from picamera2.encoders import JpegEncoder, Quality, MJPEGEncoder
from picamera2.outputs import FileOutput
import io
import socket
import cv2
from datetime import datetime

PORT = 8443

PAGE = """\
<html>
<head>
<title>Baby camera</title>
</head>
<body>
<h1>Baby camera</h1>
<img src="stream.mjpg" width="1920" height="1080" />
</body>
</html>
"""

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

class VideoStreamHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':

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
        else:
            self.send_error(404)
            self.end_headers()

def apply_timestamp(request):
    timestamp = datetime.utcnow().strftime('%F %T.%f')[:-3]
    with MappedArray(request, "main") as m:
        cv2.putText(m.array, timestamp, origin, font, scale, colourBlack, thicknessBlack)
        cv2.putText(m.array, timestamp, origin, font, scale, colourWhite, thicknessWhite)

Handler = VideoStreamHandler

picam2 = Picamera2()


colourWhite = (255, 255, 255)
colourBlack = (0, 0, 0)
origin = (0, 30)
font = cv2.FONT_HERSHEY_SIMPLEX
scale = 1
thicknessWhite = 2
thicknessBlack = 6

picam2.pre_callback = apply_timestamp
picam2.configure(picam2.create_video_configuration(main={"size": (1920, 1080)}))
output = StreamingOutput()
picam2.start_recording(MJPEGEncoder(), FileOutput(output), quality=Quality.VERY_HIGH)
local_ip = "0.0.0.0"

class StreamingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

try:
    with StreamingServer((local_ip, PORT), Handler) as httpd:
        print("Serving at IP", local_ip, "and port", PORT)

        httpd.socket = ssl.wrap_socket (httpd.socket, 
            keyfile="/opt/key.pem", 
            certfile='/opt/cert.pem', server_side=True)

        httpd.serve_forever()
finally:
    picam2.stop_recording()

