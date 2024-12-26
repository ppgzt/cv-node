from datetime import datetime
from enum import Enum
from app.domain.entities.media import Image

class Job:

    def __init__(self, begin_at: datetime, final_at: datetime = None):
        self.id = None
        
        self.begin_at = begin_at
        self.final_at = final_at

    def to_tuple(self):
        return (
            self.begin_at.isoformat(), 
            self.final_at.isoformat() if self.final_at is not None else None
        )
    
    @staticmethod
    def from_tuple(data: tuple):
        job = Job(
            begin_at = datetime.fromisoformat(data[1]),
            final_at = datetime.fromisoformat(data[2]) if data[2] is not None else None,
        )
        job.id = data[0]
        return job
    
class RunStatus(Enum):
    CREATED = 0
    SYNCED  = 1

class Run:

    def __init__(self, 
                 begin_at: datetime, 
                 sensor: str, 
                 thing_id: str, 
                 thing_tag: str, 
                 job_id: int, 
                 final_at: datetime = None):
        self.id = None

        self.begin_at = begin_at
        self.final_at = final_at
        self.sensor = sensor
        
        self.thing_id = thing_id
        self.thing_tag = thing_tag
        
        self.job_id = job_id

    def to_tuple(self):
        return (
            self.begin_at.isoformat(), 
            self.final_at.isoformat() if self.final_at is not None else None,
            self.sensor,
            self.thing_id,
            self.thing_tag,
            self.job_id
        )
    
    @staticmethod
    def from_tuple(data: tuple):
        obj = Run(
            begin_at = datetime.fromisoformat(data[1]),
            final_at = datetime.fromisoformat(data[2]) if data[2] is not None else None,
            sensor   = data[3],
            thing_id = data[4],
            thing_tag= data[5],
            job_id   = data[6]
        )
        obj.id = data[0]
        return obj
    
    def __repr__(self):
        return f'''
            id:{self.id}
            begin_at:{self.begin_at}
            final_at:{self.final_at}
            sensor: {self.sensor}
            thing_id: {self.thing_id}
            thing_tag: {self.thing_tag}
            job_id: {self.job_id}
        '''
        
class RunItemType(Enum):
    IMAGE = 0

class RunItemStatus(Enum):
    STAGED    = 0
    COMMITTED = 1
    CLEANED   = 2

class RunItem:

    def __init__(self, status: RunItemStatus, type: RunItemType, data: Image, file_path: dict, run_id: int):
        self.id = None

        self.status = status
        self.type   = type
        self.data   = data
        self.file_path = file_path
        self.run_id = run_id

    def to_tuple(self):
        return (
            self.status.name,
            self.type.name, 
            self.data.pov.name,
            self.data.res.name,
            self.file_path, 
            self.run_id
        )
    
    @staticmethod
    def from_tuple(data: tuple):
        item = RunItem(
            status = RunItemStatus[data[1]],
            type   = RunItemType[data[2]],
            # FIXME
            data=None,
            file_path = data[5],
            run_id = data[6]
        )
        item.id = data[0]
        return item
    
    def __repr__(self):
        return f'''
            status:{self.status.name} 
            type: {self.type.name} 
            file_path: {self.file_path} 
            run_id: {self.run_id}
        '''