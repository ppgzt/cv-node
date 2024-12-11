import firebase_admin, uuid, re

from firebase_admin import credentials
from firebase_admin import firestore

from threading import Lock

from app.domain.failures.exceptions import ThingNotFoundToSyncException
from app.domain.entities.basic import Run

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

    def add_run_to_thing(self, project_id: str, collect_id: str, run: Run, items: list):
        doc_ref = self.__db.collection(
            "projects"
        ).document(
            project_id
        ).collection(
            "collects"
        ).document(
            collect_id
        ).collection(
            "data"
        ).document(
            run.thing_id
        )

        doc = doc_ref.get()
        if not doc.exists:
            raise ThingNotFoundToSyncException(
                thing_id=run.thing_id, 
                thing_tag=run.thing_tag
            )
        
        run_dict = {
            'begin_at':run.begin_at.isoformat(),
            'final_at':run.final_at.isoformat() if run.final_at is not None else None,
            'sensor'  :run.sensor
        }
        
        for item in items:
            # FIXME
            key = re.search('RGB|DEPTH|IR|STATUS', item.file_path).group()
            run_dict[key.lower()] = item.file_path

        _uuid = uuid.uuid3(uuid.NAMESPACE_DNS, f"{run.id}")
        doc_ref.collection(
            "images"
        ).document(
            f"{_uuid}"
        ).set(run_dict)