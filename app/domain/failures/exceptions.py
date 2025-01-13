class MediaSensorInitializationException(Exception):

    def __init__(self, msg: str = None, *args: object):
        super().__init__(*args)
        self.msg = msg if msg is not None else f'Unexpected {self}, {type(self)}'

class ThingNotFoundToSyncException(Exception):

    def __init__(self, thing_id: str, *args: object):
        super().__init__(*args)
        self.msg = f'Thing não encontrado. (ID: {thing_id})'