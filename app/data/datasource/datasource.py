from tinydb import TinyDB, Query
from app.domain.entities.basic import *

from threading import Lock

class Datasource(object):

    def __init__(self):
        self.db = TinyDB("cv-node-data/db/cvnode.json")
        
        self.__job_table = 'jobs'
        self.__run_table = 'runs'
        self.__itm_table = 'itens'

        self.__lock = Lock()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Datasource, cls).__new__(cls)
        return cls.instance
    
    def __commit(self, f):
        with self.__lock:
            return f()
    
    # Insert
    
    def insert_job(self, job: Job) -> int:
        return self.__commit(
            lambda: self.db.table(self.__job_table).insert(job.to_dict())
        )

    def insert_run(self, run: Run) -> int:
        return self.__commit(
            lambda: self.db.table(self.__run_table).insert(run.to_dict()) 
        )

    def update_run(self, run_id: int, run: Run):
        self.__commit(
            self.db.table(self.__run_table).update(run.to_dict(), doc_ids=[run_id])
        )

    def insert_item(self, item: RunItem) -> int:
        return self.__commit(
            self.db.table(self.__itm_table).insert(item.to_dict())
        )

    # List

    def list_jobs(self):
        return self.db.table(self.__job_table).all()

    def list_runs(self):
        return self.db.table(self.__run_table).all()

    def list_items(self):
        return self.db.table(self.__itm_table).all()
