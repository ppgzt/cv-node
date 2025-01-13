import firebase_admin, uuid, re

from firebase_admin import credentials
from firebase_admin import firestore

from threading import Lock

from app.domain.failures.exceptions import ThingNotFoundToSyncException
from app.domain.entities.views import *

class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """

    _instances = {}

    _lock: Lock = Lock()
    """
    We now have a lock object that will be used to synchronize threads during
    first access to the Singleton.
    """

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        # Now, imagine that the program has just been launched. Since there's no
        # Singleton instance yet, multiple threads can simultaneously pass the
        # previous conditional and reach this point almost at the same time. The
        # first of them will acquire lock and will proceed further, while the
        # rest will wait here.
        with cls._lock:
            # The first thread to acquire the lock, reaches this conditional,
            # goes inside and creates the Singleton instance. Once it leaves the
            # lock block, a thread that might have been waiting for the lock
            # release may then enter this section. But since the Singleton field
            # is already initialized, the thread won't create a new object.
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class FirebaseDatasource(metaclass=SingletonMeta):

    def __init__(self):
        firebase_admin.initialize_app(credentials.Certificate('fb-credentials.json'))
        self.__db = firestore.client()

    def add_run_to_thing(self, run_row: RunRow, items: list):
        doc_ref = self.__db.collection(
            "projects"
        ).document(
            run_row.project_id
        ).collection(
            "collects"
        ).document(
            run_row.collect_id
        ).collection(
            "data"
        ).document(
            run_row.thing_id
        )

        doc = doc_ref.get()
        if not doc.exists:
            raise ThingNotFoundToSyncException(thing_id=run_row.thing_id)
        
        run_dict = {
            'begin_at':run_row.begin_at.isoformat(),
            'final_at':run_row.final_at.isoformat() if run_row.final_at is not None else None,
            'sensor'  :run_row.sensor
        }
        
        for item in items:
            run_dict[item.type.name.lower()] = item.file_path

        _uuid = uuid.uuid3(uuid.NAMESPACE_DNS, f"{run_row.run_id}")
        doc_ref.collection(
            "images"
        ).document(
            f"{_uuid}"
        ).set(run_dict)