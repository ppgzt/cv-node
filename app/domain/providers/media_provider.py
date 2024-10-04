import threading
import time
import cv2
from datetime import datetime

from app.data.sensors.camera.cameras import MaixSenseA075V 
from app.domain.failures.exceptions import MediaSensorInitializationException

class MediaProvider:

    def __init__(self):
        self.sensor = MaixSenseA075V()

        # img acquisition
        def handling():
            while True:
                if self.event.is_set():
                    try:                    
                        now_in_milli = datetime.now().timestamp() * 1000
                        
                        thing_id = self.thing["id"]
                        print(f'capturing: thing-id - {thing_id}')
                        
                        frames = self.sensor.take_snapshot()
                        for img in frames:
                            # TEMP: Acredito que a imagem deva ser persistida sem ColorMap
                            _data = cv2.applyColorMap(img.data, cv2.COLORMAP_VIRIDIS)
                            cv2.imwrite(f'output/{thing_id}_{now_in_milli}_{img.type}.jpg', _data)
                    
                    except MediaSensorInitializationException as err:
                        print(err.msg)
                    
                    except Exception as err:
                        print(f'Unexpected {err=}, {type(err)=}')
                    
                    time.sleep(1)
                else:
                    print(f'waiting')
                    self.event.wait()
        
        self.event = threading.Event()
        self.thing = None
        
        t_capt = threading.Thread(target = handling)        
        t_capt.start()

        print('orchestration on')

    def start(self, thing):
        print('step: start')
        self.thing = thing
        self.event.set()
        
    def stop(self):
        print('step: stop')

        self.obj = None
        self.event.clear()