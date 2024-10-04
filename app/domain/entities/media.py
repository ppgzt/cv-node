import numpy as np
from enum import Enum

class ImageType(Enum):
    RGB    = 0
    IR     = 1
    DEPTH  = 2
    STATUS = 3

class ImageRes(Enum):
    _320_240_1  = 0
    _640_480_3  = 1

class ImagePOV(Enum):
    TOP_DOWN = 0
    SIDEWAY  = 1

class Image:

    def __init__(self, image_type: ImageType, image_res: ImageRes, image_pov: ImagePOV, data: np.ndarray):
        self.type = image_type
        self.res  = image_res
        self.pov  = image_pov
        self.data = data