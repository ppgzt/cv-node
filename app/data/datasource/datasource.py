import sqlite3

from datetime import datetime
from app.domain.entities.basic import *

class Datasource(object):

    def __init__(self):
        self.con = sqlite3.connect("cv-node-data/db/cvnode.db")
        
        self.__job_table = 'jobs'
        self.__run_table = 'runs'
        self.__itm_table = 'itens'

        # FIXME ~ Where to create Tables? 

        cur = self.__get_cursor()
        
        cur.execute(f'''CREATE TABLE IF NOT EXISTS {self.__job_table} (begin_at, final_at)''')
        cur.execute(f'''CREATE TABLE IF NOT EXISTS {self.__run_table} (
                    begin_at, 
                    final_at, 
                    sensor, 
                    thing_id,
                    thing_tag,
                    job_id)''')
        cur.execute(f'''CREATE TABLE IF NOT EXISTS {self.__itm_table} (
                    status,
                    type, 
                    pov,
                    res,
                    file_path,
                    run_id)''')
        
        self.__commit()
    
    def __get_cursor(self):
        return self.con.cursor()
    
    def __commit(self):
        self.con.commit()
    
    # Insert | Update
    
    def insert_job(self, job: Job) -> int:
        res = self.__get_cursor().execute(
            f"INSERT INTO {self.__job_table} VALUES(?, ?)", job.to_tuple()
        )                
        self.__commit()
        return res.lastrowid
    
    def close_job(self, job_id: int, final_at: datetime) -> None:
        self.__get_cursor().execute(
            f"""UPDATE {self.__job_table} SET final_at = ? WHERE rowid = ?""", 
            (final_at, job_id)
        )                
        self.__commit()

    def insert_run(self, run: Run) -> int:
        res = self.__get_cursor().execute(
            f"INSERT INTO {self.__run_table} VALUES(?, ?, ?, ?, ?, ?)", 
            run.to_tuple()
        )                
        self.__commit()
        return res.lastrowid

    def update_run(self, run_id: int, run: Run) -> None:
        values = list(run.to_tuple())
        values.append(run_id)

        self.__get_cursor().execute(
            f"""UPDATE {self.__run_table} 
                SET begin_at = ?, 
                    final_at = ?, 
                    sensor = ?, 
                    thing_id = ?, 
                    thing_tag = ?, 
                    job_id = ? 
                WHERE rowid = ?
            """, tuple(values)
        )                
        self.__commit()

    def insert_item(self, item: RunItem) -> int:
        res = self.__get_cursor().execute(
            f"INSERT INTO {self.__itm_table} VALUES(?, ?, ?, ?, ?, ?)", 
            item.to_tuple()
        )                
        self.__commit()
        return res.lastrowid       

    # List

    def list_jobs(self):
        res = self.__get_cursor().execute(
            f'SELECT rowid, * FROM {self.__job_table}'
        )
        jobs = []
        for row in res.fetchall():
            jobs.append(Job.from_tuple(row))

        return jobs

    def list_items(self):
        res = self.__get_cursor().execute(
            f'SELECT rowid, * FROM {self.__itm_table}'
        )
        items = []
        for row in res.fetchall():
            items.append(RunItem.from_tuple(row))

        return items

    # Filter
    
    def filter_runs_by_status(self, status: RunStatus):
        # FIXME
        res = self.__get_cursor().execute(
            f'SELECT rowid, * FROM {self.__run_table} WHERE rowid > 6800'
        )
        
        runs = []
        for row in res.fetchall():
            runs.append(Run.from_tuple(row))

        return runs
    
    def filter_items_by_run_id(self, run_id: int):
        res = self.__get_cursor().execute(
            f'''SELECT rowid, * 
                FROM {self.__itm_table}
                WHERE run_id = ?
            ''', (run_id,)
        )
        items = []
        for row in res.fetchall():
            items.append(RunItem.from_tuple(row))

        return items