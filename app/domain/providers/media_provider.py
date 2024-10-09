import threading, time, cv2

from datetime import datetime

from app.data.sensors.camera.cameras import *
from app.domain.entities.basic import *

from app.domain.failures.exceptions import MediaSensorInitializationException
from app.data.datasource.datasource import Datasource

class MediaProvider:

    def __init__(self):

        self.factories = [
            lambda: MockCam(), 
            # lambda: PiCamera(), lambda: MaixSenseA075V()
        ]

        # img acquisition
        def handling(thread_name: str, job_id: int, sensor_factory):
            datasource = Datasource()
            sensor = None
            
            while True:
                if self.event.is_set():
                    print(f'{thread_name} is capturing ...')
                    try:
                        thing_id = self.thing["id"]

                        run = Run(job_id=job_id, thing_id=thing_id, begin_at=datetime.now())
                        run_id = datasource.insert_run(run=run)

                        if sensor is None:
                            sensor = sensor_factory()
                             
                        timestamp = int(datetime.now().timestamp())
                        frames = sensor.take_snapshot()
                        for img in frames:
                            # TEMP: Acredito que a imagem deva ser persistida sem ColorMap
                            #_data = cv2.applyColorMap(img.data, cv2.COLORMAP_VIRIDIS)
                            
                            file_path = f'{run_id}_{thing_id}_{timestamp}_{img.type.name}.jpg'
                            cv2.imwrite(f'cv-node-data/output/{file_path}', img.data)

                            # self.datasource.insert_item(item=RunItem(
                            #     run_id=run_id,
                            #     sensor=thread_name,
                            #     type=RunItemType.IMAGE,
                            #     data={'file_path':file_path}
                            # ))

                        # run.final_at = datetime.now()
                        # self.datasource.update_run(run_id=run_id, run=run)
                            
                        print(f'{thread_name} done!')
                    
                    except MediaSensorInitializationException as err:
                        print(f'{thread_name} - {err.msg}')
                    
                    except Exception as err:
                        print(f'{thread_name} - Unexpected {err=}, {type(err)=}')
                    
                    # time.sleep(1)
                else:
                    print(f'waiting')
                    self.event.wait()
        
        self.event = threading.Event()
        self.thing = None

        self.threads = []
        i = 0
        for sensor_factory in self.factories:
            # FIXME: set job_id

            t = threading.Thread(target = handling, args=(f'Thread: {i}', 0, sensor_factory,))
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