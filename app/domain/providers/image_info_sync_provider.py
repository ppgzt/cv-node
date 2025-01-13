import threading

from app.domain.entities.basic import *

from app.data.datasource.datasource import Datasource
from app.data.datasource.firebase_datasource import FirebaseDatasource
from app.domain.failures.exceptions import ThingNotFoundToSyncException

class ImageInfoSyncProvider():

    def __init__(self):
        self.event = threading.Event()

        # sync
        def handling():
            fireb_ds = FirebaseDatasource()
            local_ds = Datasource()

            while True:
                if self.event.is_set():
                    runs = local_ds.filter_runs_by_status_as_view(RunStatus.CREATED)
                    i = 1

                    for run_row in runs:
                        print(f"Run {i}/{len(runs)}")
                        print(run_row)

                        items = local_ds.filter_items_by_run_id(run_id=run_row.run_id)
                        try:
                            fireb_ds.add_run_to_thing(run_row=run_row,items=items)

                        except ThingNotFoundToSyncException as err:
                            print(err.msg)
                        
                        except Exception as err:
                            print(f'{run_row.id} - Unexpected {err=}, {type(err)=}')
                        
                        local_ds.update_run_status(run_row.run_id, RunStatus.SYNCED)
                        i+=1
                    
                    self.event.clear()
                else:
                    self.event.wait()
             
        t = threading.Thread(target = handling)
        t.start()

    def start(self):
        self.event.set()
        print('sync on')