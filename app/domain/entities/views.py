from datetime import datetime

class RunRow:

    def __init__(self, 
                 job_id: int, 
                 run_id: int,
                 project_id: str, 
                 collect_id: str, 
                 thing_id: str, 
                 sensor: str,
                 begin_at: datetime, 
                 final_at: datetime):
        self.job_id = job_id
        self.run_id = run_id
        self.project_id = project_id
        self.collect_id = collect_id
        self.thing_id = thing_id
        self.sensor = sensor
        self.begin_at = begin_at
        self.final_at = final_at

    @staticmethod
    def from_tuple(data: tuple):
        row = RunRow(
            job_id=data[0],
            run_id=data[1],
            project_id=data[2],
            collect_id=data[3],
            thing_id=data[4],
            sensor= data[5],
            begin_at = datetime.fromisoformat(data[6]),
            final_at = datetime.fromisoformat(data[7]) if data[7] is not None else None,
        )
        return row
    
    def __repr__(self):
        return f'''
            job_id: {self.job_id}
            run_id: {self.run_id}
            project_id:{self.project_id}
            collect_id:{self.collect_id}
            thing_id:{self.thing_id}
            sensor: {self.sensor}
            begin_at:{self.begin_at}
            final_at:{self.final_at}
        '''