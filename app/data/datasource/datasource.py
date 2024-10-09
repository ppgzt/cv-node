import sqlite3

from app.domain.entities.basic import *

class Datasource(object):

    def __init__(self):
        self.con = sqlite3.connect("cv-node-data/db/cvnode.db")
        
        self.__job_table = 'jobs'
        self.__run_table = 'runs'
        self.__itm_table = 'itens'

        # FIXME ~ Where to create Tables? 

        cur = self.__get_cursor()
        
        cur.execute(f'CREATE TABLE IF NOT EXISTS {self.__job_table} (id ROWID, begin_at, final_at)')
        cur.execute(f'CREATE TABLE IF NOT EXISTS {self.__run_table} (id ROWID, begin_at, final_at, thing_id, job_id)')
        cur.execute(f'CREATE TABLE IF NOT EXISTS {self.__itm_table} (id ROWID, status, sensor, type, data, run_id)')
        
        self.__commit
    
    def __get_cursor(self):
        return self.con.cursor()
    
    def __commit(self):
        self.con.commit() 
    
    # Insert | Update
    
    def insert_job(self, job: Job) -> int:
        res = self.__get_cursor().execute(
            f"INSERT INTO {self.__job_table} VALUES(null, ?, ?)", job.to_tuple()
        )                
        self.__commit()
        return res.lastrowid

    def insert_run(self, run: Run) -> int:
        res = self.__get_cursor().execute(
            f"INSERT INTO {self.__run_table} VALUES(null, ?, ?, ?, ?)", run.to_tuple()
        )                
        self.__commit()
        return res.lastrowid

    def update_run(self, run_id: int, run: Run) -> None:
        values = list(run.to_tuple())
        values.insert(0, run_id)

        self.__get_cursor().execute(
            f"""UPDATE {self.__run_table} 
                SET begin_at = ?, final_at = ?, thing_id = ?, job_id = ? 
                WHERE id = ?
            """, tuple(values)
        )                
        self.__commit()

    def insert_item(self, item: RunItem) -> int:
        res = self.__get_cursor().execute(
            f"INSERT INTO {self.__itm_table} VALUES(null, ?, ?, ?, ?, ?)", item.to_tuple()
        )                
        self.__commit()
        return res.lastrowid       

    # List

    def list_jobs(self):
        return self.db.table(self.__job_table).all()

    def list_runs(self):
        return self.db.table(self.__run_table).all()

    def list_items(self):
        return self.db.table(self.__itm_table).all()
