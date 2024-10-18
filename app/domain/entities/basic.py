from datetime import datetime
from enum import Enum

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

    def __init__(self, begin_at: datetime, thing_id: str, job_id: int, final_at: datetime = None):
        self.begin_at = begin_at
        self.final_at = final_at
        self.thing_id = thing_id
        self.job_id = job_id

    def to_tuple(self):
        return (
            self.begin_at.isoformat(), 
            self.final_at.isoformat() if self.final_at is not None else None,
            self.thing_id,
            self.job_id
        )
    
    def to_dict(self):
        return {
            'begin_at': self.begin_at.isoformat(),
            'final_at': self.final_at.isoformat() if self.final_at is not None else None,
            'thing_id': self.thing_id,
            'job_id': self.job_id
        }

class RunItemType(Enum):
    IMAGE = 0

class RunItemStatus(Enum):
    STAGED    = 0
    COMMITTED = 1
    CLEANED   = 2

class RunItem:

    def __init__(self, status: RunItemStatus, sensor: str, type: RunItemType, file_path: dict, run_id: int):
        self.status = status
        self.sensor = sensor
        self.type   = type
        self.file_path   = file_path
        self.run_id = run_id

    def to_tuple(self):
        return (
            self.status.name, 
            self.sensor, 
            self.type.name, 
            self.file_path, 
            self.run_id
        )
    
    def to_dict(self):
        return {
            'status': self.status.name,
            'sensor': self.sensor,
            'type': self.type.name,
            'data': self.file_path,
            'run_id': self.run_id,
        }
    
