from tinydb import TinyDB, Query
from app.domain.entities.basic import *

class Datasource(object):

    def __init__(self):
        self.db = TinyDB("db/cvnode.json")
        
        self.__job_table = 'jobs'
        self.__run_table = 'runs'
        self.__itm_table = 'itens'

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Datasource, cls).__new__(cls)
        return cls.instance
    
    def insert_job(self, job: Job) -> int:
        return self.db.table(self.__job_table).insert(job.to_dict())

    def insert_run(self, run: Run) -> int:
        return self.db.table(self.__run_table).insert(run.to_dict())
    
    def insert_item(self, item: RunItem) -> int:
        return self.db.table(self.__itm_table).insert(item.to_dict())

    def list_jobs(self):
        return self.db.table(self.__job_table).all()
    
    def list_items(self):
        return self.db.table(self.__itm_table).all()