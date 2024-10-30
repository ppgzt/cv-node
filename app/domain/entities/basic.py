from datetime import datetime
from enum import Enum
from app.domain.entities.media import Image

class Job:

    def __init__(self, begin_at: datetime, final_at: datetime = None):
        self.begin_at = begin_at
        self.final_at = final_at

    def to_tuple(self):
        return (
            self.begin_at.isoformat(), 
            self.final_at.isoformat() if self.final_at is not None else None
        )
    
    def to_dict(self):
        return {
            'begin_at': self.begin_at.isoformat(),
            'final_at': self.final_at.isoformat() if self.final_at is not None else None
        }

class Run:

    def __init__(self, 
                 begin_at: datetime, 
                 sensor: str, 
                 thing_id: str, 
                 thing_tag: str, 
                 job_id: int, 
                 final_at: datetime = None):
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
        
class RunItemType(Enum):
    IMAGE = 0

class RunItemStatus(Enum):
    STAGED    = 0
    COMMITTED = 1
    CLEANED   = 2

class RunItem:

    def __init__(self, status: RunItemStatus, type: RunItemType, data: Image, file_path: dict, run_id: int):
        self.status = status
        self.type   = type
        self.data   = data
        self.file_path   = file_path
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