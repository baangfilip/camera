from picamera2 import Picamera2, MappedArray
from picamera2.encoders import Quality, MJPEGEncoder
from picamera2.outputs import FileOutput
from threading import Condition
from datetime import datetime
import io
import cv2

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
            
def apply_timestamp(request):
    timestamp = datetime.utcnow().strftime('%F %T.%f')[:-3]
    with MappedArray(request, "main") as m:
        cv2.putText(m.array, timestamp, origin, font, scale, colourBlack, thicknessBlack)
        cv2.putText(m.array, timestamp, origin, font, scale, colourWhite, thicknessWhite)

colourWhite = (255, 255, 255)
colourBlack = (0, 0, 0)
origin = (0, 30)
font = cv2.FONT_HERSHEY_SIMPLEX
scale = 1
thicknessWhite = 2
thicknessBlack = 6

picam2 = Picamera2()

picam2.pre_callback = apply_timestamp
picam2.configure(picam2.create_video_configuration(main={"size": (1920, 1080)}))
output = StreamingOutput()
picam2.start_recording(MJPEGEncoder(), FileOutput(output), quality=Quality.VERY_HIGH)
