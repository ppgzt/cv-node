import sqlite3

from datetime import datetime
from app.domain.entities.basic import *
from app.domain.entities.views import *

class Datasource(object):

    def __init__(self):
        self.con = sqlite3.connect("cv-node-data/db/cvnode.db")
        
        self.__job_table = 'jobs'
        self.__run_table = 'runs'
        self.__itm_table = 'itens'

        # FIXME ~ Where to create Tables? 

        cur = self.__get_cursor()
        
        cur.execute(f'''CREATE TABLE IF NOT EXISTS {self.__job_table} (
                    begin_at, 
                    project_id,
                    collect_id,
                    thing_id,
                    thing_tag,
                    final_at)''')
        cur.execute(f'''CREATE TABLE IF NOT EXISTS {self.__run_table} (
                    begin_at,
                    status, 
                    sensor, 
                    job_id,
                    final_at)''')
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
            f"INSERT INTO {self.__job_table} VALUES(?, ?, ?, ?, ?, ?)", job.to_tuple()
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
            f"INSERT INTO {self.__run_table} VALUES(?, ?, ?, ?, ?)", 
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
                    status = ?,
                    sensor = ?, 
                    job_id = ?, 
                    final_at = ? 
                WHERE rowid = ?
            """, tuple(values)
        )                
        self.__commit()

    def update_run_status(self, run_id: int, status: RunStatus) -> None:
        print((run_id, status))
        self.__get_cursor().execute(
            f"""UPDATE {self.__run_table} 
                SET status  = ?
                WHERE rowid = ?
            """, (status.name, run_id)
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
    
    # As View

    def filter_runs_by_status_as_view(self, status: RunStatus):
        res = self.__get_cursor().execute(
            f'''
            SELECT job.rowid, 
                run.rowid, 
                job.project_id, 
                job.collect_id, 
                job.thing_id, 
                run.sensor, 
                run.begin_at, 
                run.final_at
            FROM {self.__run_table} as run
            JOIN {self.__job_table} as job on run.job_id = job.rowid
            WHERE run.status = ?
            ''',
            (status.name,)
        )
        
        runs = []
        for row in res.fetchall():
            runs.append(RunRow.from_tuple(row))

        return runs