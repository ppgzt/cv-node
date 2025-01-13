from datetime import datetime
from enum import Enum

from app.domain.entities.media import *

class Job:

    def __init__(self, 
                 begin_at: datetime, 
                 project_id: str, 
                 collect_id: str, 
                 thing_id: str, 
                 thing_tag: str, 
                 final_at: datetime = None):
        self.id = None
        
        self.begin_at = begin_at
        self.project_id = project_id
        self.collect_id = collect_id
        self.thing_id = thing_id
        self.thing_tag = thing_tag
        self.final_at = final_at

    def to_tuple(self):
        return (
            self.begin_at.isoformat(),
            self.project_id,
            self.collect_id,
            self.thing_id,
            self.thing_tag,
            self.final_at.isoformat() if self.final_at is not None else None
        )
    
    @staticmethod
    def from_tuple(data: tuple):
        job = Job(
            begin_at = datetime.fromisoformat(data[1]),
            project_id=data[2],
            collect_id=data[3],
            thing_id = data[4],
            thing_tag= data[5],
            final_at = datetime.fromisoformat(data[6]) if data[6] is not None else None,
        )
        job.id = data[0]
        return job
    
    def __repr__(self):
        return f'''
            id:{self.id}
            begin_at:{self.begin_at}
            project_id: {self.project_id}
            collect_id: {self.collect_id}
            thing_id: {self.thing_id}
            thing_tag: {self.thing_tag}
            final_at:{self.final_at}
        '''
    
class RunStatus(Enum):
    CREATED = 0
    SYNCED  = 1

class Run:

    def __init__(self, 
                 begin_at: datetime, 
                 status: RunStatus,
                 sensor: str, 
                 job_id: int, 
                 final_at: datetime = None):
        self.id = None

        self.begin_at = begin_at
        self.status = status
        self.sensor = sensor
        self.job_id = job_id
        self.final_at = final_at

    def to_tuple(self):
        return (
            self.begin_at.isoformat(), 
            self.status.name,
            self.sensor,
            self.job_id,
            self.final_at.isoformat() if self.final_at is not None else None,
        )
    
    @staticmethod
    def from_tuple(data: tuple):
        obj = Run(
            begin_at = datetime.fromisoformat(data[1]),
            status=RunStatus[data[2]],
            sensor   = data[3],
            job_id   = data[4],
            final_at = datetime.fromisoformat(data[5]) if data[5] is not None else None,
        )
        obj.id = data[0]
        return obj
    
    def __repr__(self):
        return f'''
            id:{self.id}
            begin_at:{self.begin_at}
            status:{self.status}
            sensor: {self.sensor}
            job_id: {self.job_id}
            final_at:{self.final_at}
        '''
        
class RunItemStatus(Enum):
    STAGED    = 0
    COMMITTED = 1
    CLEANED   = 2

class RunItem:

    def __init__(self, 
                 status: RunItemStatus, 
                 type: ImageType, 
                 pov: ImagePOV, 
                 res: ImageRes, 
                 file_path: dict, 
                 run_id: int):
        self.id = None

        self.status = status
        self.type   = type
        self.pov    = pov
        self.res    = res
        self.file_path = file_path
        self.run_id = run_id

    def to_tuple(self):
        return (
            self.status.name,
            self.type.name,
            self.pov.name,
            self.res.name,
            self.file_path, 
            self.run_id
        )
    
    @staticmethod
    def from_tuple(data: tuple):
        item = RunItem(
            status = RunItemStatus[data[1]],
            type   = ImageType[data[2]],
            pov = ImagePOV[data[3]],
            res = ImageRes[data[4]],
            file_path = data[5],
            run_id = data[6]
        )
        item.id = data[0]
        return item
    
    def __repr__(self):
        return f'''
            status:{self.status.name} 
            type: {self.type.name} 
            pov: {self.pov.name}
            res: {self.res.name}
            file_path: {self.file_path} 
            run_id: {self.run_id}
        '''