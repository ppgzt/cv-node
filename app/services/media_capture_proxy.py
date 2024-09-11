import threading
import time

class MediaCaptureProxy:

    def __init__(self):

        # img acquisition
        def handling():
            while True:
                if self.evt.is_set():
                    print(f'capturing: {self.obj["id"]}')
                    time.sleep(1)
                else:
                    print(f'waiting')
                    self.evt.wait()
        
        self.evt = threading.Event()
        self.obj = None
        
        t_capt = threading.Thread(target = handling)        
        t_capt.start()

        print('orchestration on')

    def start(self):
        print('step: start')
        self.obj = {'id':'xyzl'}
        self.evt.set()
        
    def stop(self):
        print('step: stop')

        self.obj = None
        self.evt.clear()