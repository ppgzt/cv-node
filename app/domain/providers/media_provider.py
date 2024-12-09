import threading, cv2, json, os

from datetime import datetime

from app.data.sensors.camera.cameras import *
from app.domain.entities.basic import *

from app.domain.failures.exceptions import MediaSensorInitializationException
from app.data.datasource.datasource import Datasource
from app.domain.entities.helpers import ClockWatch

class MediaProvider():

    def __init__(self):
        self.durations = []
        self.sensors   = []

        self.sensor_factories = [
            # lambda: MockCam(), 
            # lambda: PiCamera(), 
            lambda: MaixSenseA075V()
        ]

        # img acquisition
        def handling(thread_name: str, sensor_factory):
            
            ds = Datasource()
            sensor = None

            while True:
                clock_watch = ClockWatch(key=thread_name)
                
                if self.event.is_set():
                    print(f'{thread_name} is capturing ...')
                    try:
                        if sensor is None:
                            sensor = sensor_factory()                            
                            sensor.init_session()
                            self.sensors.append(sensor)
                        
                        thing_tag = self.thing["tag"]
                        run = Run(
                            begin_at=datetime.now(),
                            sensor=sensor.name,
                            thing_id=self.thing['id'],
                            thing_tag=thing_tag,
                            job_id=self.job_id)
                        run_id = ds.insert_run(run=run)

                        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
                        frames = clock_watch.watch(
                            step_name='0-capture', method=lambda: sensor.take_snapshot())
                        
                        i = 1
                        for img in frames:
                            file_name = f'{thing_tag}_{run_id}_{timestamp}_{img.type.name}{img.res.name}.png'
                            clock_watch.watch(
                                step_name=f'1-store_img_{i}', 
                                method=lambda: cv2.imwrite(
                                    f'{self.__job_folder}/{img.type.name}/{file_name}', img.data
                                )
                            )

                            item = RunItem(
                                status=RunItemStatus.STAGED, 
                                type=RunItemType.IMAGE,
                                data=img,
                                file_path=file_name, 
                                run_id=run_id
                            )

                            item_id = clock_watch.watch(
                                step_name=f'2-store_db_{i}', method=lambda: ds.insert_item(item=item))
                            print(f'Item {item_id} inserted')
                            
                            i = i+1

                        run.final_at = datetime.now()
                        ds.update_run(run_id=run_id, run=run)
                            
                        print(f'{thread_name} done! durations: {clock_watch.cron}')
                        self.durations.append(clock_watch.cron)
                    
                    except MediaSensorInitializationException as err:
                        print(f'{thread_name} - {err.msg}')
                    
                    except Exception as err:
                        print(f'{thread_name} - Unexpected {err=}, {type(err)=}')
                    
                else:
                    self.event.wait()
                    if self.job_id is not None:
                        try:
                            ds.close_job(job_id=self.job_id, final_at=datetime.now())
                        except:
                            # TODO
                            pass
                        self.job_id = None

                    print(f'waiting')
        
        self.event = threading.Event()
        self.thing = None

        self.threads = []
        i = 0
        for factory in self.sensor_factories:
            t = threading.Thread(target = handling, args=(f'Thread: {i}', factory,))
            self.threads.append(t)
            
            t.start()
            i = i+1

        print('orchestration on')

    def start(self, thing: dict):
        job_id = Datasource().insert_job(job=Job(begin_at=datetime.now()))
        self.__job_folder = f"cv-node-data/output/{job_id}"

        print(f'MediaProvider | starting job: {job_id}')
        self.job_id = job_id
        self.durations = []

        for s in self.sensors:
            s.init_session()
        
        self.thing = thing

        if not os.path.exists(self.__job_folder):
            os.makedirs(f"{self.__job_folder}/{ImageType.DEPTH.name}")
            os.makedirs(f"{self.__job_folder}/{ImageType.RGB.name}")
            os.makedirs(f"{self.__job_folder}/{ImageType.IR.name}") 
            os.makedirs(f"{self.__job_folder}/{ImageType.STATUS.name}")
            os.makedirs(f"{self.__job_folder}/watch")
            
        self.event.set()
        
    def stop(self):
        print('step: stop')

        self.thing = None
        self.event.clear()

        try:
            with open(f'{self.__job_folder}/watch/durations.json', 'w') as f:
                file_data = []
                for dur in self.durations:
                    data = {}
                    for tp in dur:
                        data[tp[0]] = tp[1]
                    file_data.append(data)    
                json.dump(file_data, f)
        except Exception as err:
            # TODO
            pass