import threading
import time
import cv2
from datetime import datetime

from app.data.sensors.camera.cameras import *
from app.domain.failures.exceptions import MediaSensorInitializationException

class MediaProvider:

    def __init__(self):
        self.sensors = [
            lambda: PiCamera(), lambda: MaixSenseA075V()
        ]

        # img acquisition
        def handling(thread_name: str, factory):
            sensor = None
            
            while True:
                if self.event.is_set():
                    try:               
                        if sensor is None:
                            sensor = factory()
     
                        now_in_milli = datetime.now().timestamp() * 1000
                        
                        thing_id = self.thing["id"]
                        print(f'{thread_name} is capturing: thing-id - {thing_id}')
                        
                        frames = sensor.take_snapshot()
                        for img in frames:
                            # TEMP: Acredito que a imagem deva ser persistida sem ColorMap
                            #_data = cv2.applyColorMap(img.data, cv2.COLORMAP_VIRIDIS)
                            cv2.imwrite(f'output/{thing_id}_{now_in_milli}_{img.type}.jpg', img.data)
                            print('saved')
                    
                    except MediaSensorInitializationException as err:
                        print(f'{thread_name} - {err.msg}')
                    
                    except Exception as err:
                        print(f'{thread_name} - Unexpected {err=}, {type(err)=}')
                    
                    time.sleep(1)
                else:
                    print(f'waiting')
                    self.event.wait()
        
        self.event = threading.Event()
        self.thing = None

        self.threads = []
        i = 0
        for sensor in self.sensors:
            t = threading.Thread(target = handling, args=(f'Thread: {i}', sensor,))
            self.threads.append(t)
            
            t.start()
            i = i+1

        print('orchestration on')

    def start(self, thing):
        print('step: start')
        self.thing = thing
        self.event.set()
        
    def stop(self):
        print('step: stop')

        self.obj = None
        self.event.clear()