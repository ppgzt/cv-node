import threading, time, cv2

from datetime import datetime

from app.data.sensors.camera.cameras import *
from app.domain.entities.basic import *

from app.domain.failures.exceptions import MediaSensorInitializationException
from app.data.datasource.datasource import Datasource

class MediaProvider:

    def __init__(self):
        self.datasource = Datasource()

        self.sensors = [
            lambda: MockCam()
            # lambda: PiCamera(), lambda: MaixSenseA075V()
        ]

        # img acquisition
        def handling(thread_name: str, factory):
            sensor = None
            
            while True:
                if self.event.is_set():
                    print(f'{thread_name} is capturing ...')
                    try:
                        thing_id = self.thing["id"]

                        run = Run(thing_id=thing_id)
                        run_id = self.datasource.insert_run(run=run)                        

                        if sensor is None:
                            sensor = factory()
                             
                        timestamp = datetime.now().microsecond                        
                        frames = sensor.take_snapshot()
                        for img in frames:
                            # TEMP: Acredito que a imagem deva ser persistida sem ColorMap
                            #_data = cv2.applyColorMap(img.data, cv2.COLORMAP_VIRIDIS)
                            
                            file_path = f'output/{thing_id}_{timestamp}_{img.type.name}.jpg'
                            cv2.imwrite(file_path, img.data)

                            self.datasource.insert_item(item=RunItem(
                                run_id=run_id,
                                sensor=f'{type(sensor)}',
                                type=RunItemType.IMAGE,
                                data={'file_path':file_path}
                            ))

                            run.final_at = datetime.now()
                            self.datasource.update_run(run_id=run_id, run=run)
                            
                        print(f'{thread_name} done!')
                    
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

    def start(self, thing: dict, job_id: int):
        print(f'MediaProvider | starting job: {job_id}')
        self.thing = thing
        self.event.set()
        
    def stop(self):
        print('step: stop')

        self.obj = None
        self.event.clear()
        print(self.datasource.list_runs())