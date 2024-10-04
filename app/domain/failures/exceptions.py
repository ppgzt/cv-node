class MediaSensorInitializationException(Exception):

    def __init__(self, msg: str = None, *args: object):
        super().__init__(*args)
        self.msg = msg if msg is not None else f'Unexpected {self}, {type(self)}'