import threading, cv2, json

from datetime import datetime

from app.data.sensors.camera.cameras import *
from app.domain.entities.basic import *

from app.domain.failures.exceptions import MediaSensorInitializationException
from app.data.datasource.datasource import Datasource
from app.domain.entities.helpers import ClockWatch

class MediaProvider():

    def __init__(self):
        self.durations = []

        self.factories = [
            lambda: MockCam(), # lambda: PiCamera(), lambda: MaixSenseA075V()
        ]

        # img acquisition
        def handling(thread_name: str, job_id: int, sensor_factory):
            
            ds = Datasource()
            sensor = None
            
            while True:
                clock_watch = ClockWatch(key=thread_name)
                
                if self.event.is_set():
                    print(f'{thread_name} is capturing ...')
                    try:
                        thing_id = self.thing["id"]

                        run = Run(job_id=job_id, thing_id=thing_id, begin_at=datetime.now())
                        run_id = ds.insert_run(run=run)

                        if sensor is None:
                            sensor = sensor_factory()
                             
                        timestamp = int(datetime.now().timestamp())
                        
                        
                        frames = clock_watch.watch(
                            step_name='0-capture', method=lambda: sensor.take_snapshot())
                        for img in frames:
                            # TODO: Acredito que a imagem deva ser persistida sem ColorMap
                            #_data = cv2.applyColorMap(img.data, cv2.COLORMAP_VIRIDIS)                            
                            
                            file_path = f'{run_id}_{thing_id}_{timestamp}_{img.type.name}.jpg'
                            clock_watch.watch(
                                step_name='1-store_img', 
                                method= lambda: cv2.imwrite(f'cv-node-data/output/{file_path}', img.data)
                            )

                            item = RunItem(
                                status=RunItemStatus.STAGED, sensor=thread_name, type=RunItemType.IMAGE,file_path=file_path, run_id=run_id,
                            )

                            item_id = clock_watch.watch(
                                step_name='2-store_db', method=lambda: ds.insert_item(item=item))
                            print(f'Item {item_id} inserted')

                        run.final_at = datetime.now()
                        ds.update_run(run_id=run_id, run=run)
                            
                        print(f'{thread_name} done! durations: {clock_watch.cron}')
                        self.durations.append(clock_watch.cron)
                    
                    except MediaSensorInitializationException as err:
                        print(f'{thread_name} - {err.msg}')
                    
                    except Exception as err:
                        print(f'{thread_name} - Unexpected {err=}, {type(err)=}')
                    
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
        self.durations = []

        self.thing = thing
        self.event.set()
        
    def stop(self):
        print('step: stop')

        self.obj = None
        self.event.clear()

        with open('watch/durations.json', 'w') as f:
            file_data = []
            for dur in self.durations:
                data = {}
                for tp in dur:
                    data[tp[0]] = tp[1]
                file_data.append(data)    
            json.dump(file_data, f)