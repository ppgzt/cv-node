from datetime import datetime
from enum import Enum

class Job:

    def __init__(self):
        self.begin_at = datetime.now()
        self.final_at = None

    def to_dict(self):
        return {
            'begin_at': self.begin_at.isoformat(),
            'final_at': self.final_at.isoformat() if self.final_at is not None else None
        }    

class Run:

    def __init__(self, thing_id: str):
        self.begin_at = datetime.now()
        self.final_at = None
        self.thing_id = thing_id

    def to_dict(self):
        return {
            'begin_at': self.begin_at.isoformat(),
            'final_at': self.final_at.isoformat() if self.final_at is not None else None,
            'thing_id': self.thing_id
        }

class RunItemType(Enum):
    IMAGE = 0

class RunItemStatus(Enum):
    STAGED    = 0
    COMMITTED = 1
    CLEANED   = 2

class RunItem:

    def __init__(self, run_id: int, sensor: str, type: RunItemType, data: dict):
        self.status = RunItemStatus.STAGED
        self.run_id = run_id
        self.sensor = sensor
        self.type   = type
        self.data   = data

    def to_dict(self):
        return {
            'status': self.status.name,
            'run_id': self.run_id,
            'sensor': self.sensor,
            'type': self.type.name,
            'data': self.data
        }