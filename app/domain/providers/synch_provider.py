import threading

from app.domain.entities.basic import *

from app.data.datasource.datasource import Datasource
from app.data.datasource.firebase_datasource import FirebaseDatasource
from app.domain.failures.exceptions import ThingNotFoundToSyncException

class SynchProvider():

    def __init__(self):
        self.event = threading.Event()

        # sync
        def handling():
            fireb_ds = FirebaseDatasource()
            local_ds = Datasource()

            while True:
                if self.event.is_set():
                    runs = local_ds.filter_runs_by_status(RunStatus.CREATED)
                    i = 0

                    for run in runs:
                        print(f"Run {i}/{len(runs)}")

                        items = local_ds.filter_items_by_run_id(run_id=run.id)
                      
                        # FIXME ~ project_id e collect_id devem ser recuperadas do Job
                        try:
                            fireb_ds.add_run_to_thing(
                                project_id="ALue3cViohd03AlkOc5E", 
                                collect_id="OXlA4HTt69EhKln64Cjz", 
                                run=run,
                                items=items
                            )

                        except ThingNotFoundToSyncException as err:
                            print(err.msg)
                        
                        except Exception as err:
                            print(f'{run.id} - Unexpected {err=}, {type(err)=}')
                        
                        # TODO: update status do Run and remove break
                        i+=1
                        break
                    self.event.clear()
                else:
                    self.event.wait()
             
        t = threading.Thread(target = handling)
        t.start()

    def start(self):
        self.event.set()
        print('sync on')            