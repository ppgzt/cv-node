import struct
import numpy as np
import cv2
import requests

from picamzero import Camera

from app.domain.failures.exceptions import MediaSensorInitializationException
from app.domain.entities.media import *

class MediaSensor:

    def init_session(self) -> None:
        pass
    
    def take_snapshot(self) -> list:
        '''
            @return images, list
        '''
        pass

class PiCamera(MediaSensor):

    def __init__(self):
        self.cam = Camera()
        self.cam.still_size = (1920, 1080)

    def take_snapshot(self):
        frame = self.cam.capture_array()
        rgb = Image(
            image_pov=ImagePOV.SIDEWAY, 
            image_type=ImageType.RGB,
            image_res=ImageRes._1920_1080_3, 
            data=frame
        )
        return [rgb]

class MaixSenseA075V(MediaSensor):

    def __init__(self):
        self.HOST = '192.168.233.1'
        self.PORT = 80
        
        self.__session = requests.Session()

    def init_session(self):
        print('init session')
        self.__post_encode_config(self.__frame_config_encode(rgb_res=1))

    def take_snapshot(self):
        raw = self.__get_frame_from_http()
        
        decode_config = self.__frame_config_decode(raw[16:16+12])
        frame_bytes   = self.__frame_payload_decode(raw[16+12:], decode_config)

        rgb_data = np.frombuffer(frame_bytes[3], 'uint8').reshape(
            (480, 640, 3) if decode_config[6] == 1 else (600, 800, 3)) if frame_bytes[3] else None
        rgb = Image(
            image_pov=ImagePOV.SIDEWAY, 
            image_type=ImageType.RGB, 
            image_res=ImageRes._640_480_3, 
            data=rgb_data
        )

        depth_data = np.frombuffer(
            buffer=frame_bytes[0], 
            dtype='uint16' if 0 == decode_config[1] else 'uint8'
        ).reshape(240, 320) if frame_bytes[0] else None
        depth = Image(
            image_pov=ImagePOV.SIDEWAY, 
            image_type=ImageType.DEPTH, 
            image_res=ImageRes._320_240_1, 
            data=depth_data
        )

        ir_data = np.frombuffer(
            buffer=frame_bytes[1], 
            dtype='uint16' if 0 == decode_config[3] else 'uint8'
        ).reshape(240, 320) if frame_bytes[1] else None
        ir = Image(
            image_pov=ImagePOV.SIDEWAY, 
            image_type=ImageType.IR, 
            image_res=ImageRes._320_240_1, 
            data=ir_data
        )

        status_data = np.frombuffer(
            buffer=frame_bytes[2], 
            dtype='uint16' if 0 == decode_config[4] else 'uint8'
        ).reshape(240, 320) if frame_bytes[2] else None
        status = Image(
            image_pov=ImagePOV.SIDEWAY, 
            image_type=ImageType.STATUS, 
            image_res=ImageRes._320_240_1, 
            data=status_data
        )

        return [rgb, depth, ir, status]

    def __frame_config_encode(
            self, 
            trigger_mode=1, 
            deep_mode=1, 
            deep_shift=255, 
            ir_mode=1, 
            status_mode=2, 
            status_mask=7, 
            rgb_mode=1, 
            rgb_res=0, 
            expose_time=0):
        '''
            @return frame_config bytes
        '''
        return struct.pack("<BBBBBBBBi",
                        trigger_mode, deep_mode, deep_shift, ir_mode, status_mode, status_mask, rgb_mode, rgb_res, expose_time)

    def __frame_config_decode(self, frame_config):
        '''
            @frame_config bytes

            @return fields, tuple (
                trigger_mode, 
                deep_mode, 
                deep_shift, 
                ir_mode, 
                status_mode, 
                status_mask, 
                rgb_mode, 
                rgb_res, 
                expose_time
            )
        '''
        return struct.unpack("<BBBBBBBBi", frame_config)
    

    def __frame_payload_decode(self, frame_data: bytes, with_config: tuple):
        '''
            @frame_data, bytes

            @with_config, tuple (
                trigger_mode, 
                deep_mode, 
                deep_shift, 
                ir_mode, 
                status_mode, 
                status_mask, 
                rgb_mode, 
                rgb_res, 
                expose_time
            )

            @return imgs, tuple (deepth_img, ir_img, status_img, rgb_img)
        '''
        deep_data_size, rgb_data_size = struct.unpack("<ii", frame_data[:8])
        frame_payload = frame_data[8:]
        # 0:16bit 1:8bit, resolution: 320*240
        deepth_size = (320*240*2) >> with_config[1]
        deepth_img = struct.unpack("<%us" % deepth_size, frame_payload[:deepth_size])[
            0] if 0 != deepth_size else None
        frame_payload = frame_payload[deepth_size:]

        # 0:16bit 1:8bit, resolution: 320*240
        ir_size = (320*240*2) >> with_config[3]
        ir_img = struct.unpack("<%us" % ir_size, frame_payload[:ir_size])[
            0] if 0 != ir_size else None
        frame_payload = frame_payload[ir_size:]

        status_size = (320*240//8) * (16 if 0 == with_config[4] else
                                    2 if 1 == with_config[4] else 8 if 2 == with_config[4] else 1)
        status_img = struct.unpack("<%us" % status_size, frame_payload[:status_size])[
            0] if 0 != status_size else None
        frame_payload = frame_payload[status_size:]

        assert(deep_data_size == deepth_size+ir_size+status_size)

        rgb_size = len(frame_payload)
        assert(rgb_data_size == rgb_size)
        rgb_img = struct.unpack("<%us" % rgb_size, frame_payload[:rgb_size])[
            0] if 0 != rgb_size else None

        if (not rgb_img is None):
            if (1 == with_config[6]):
                jpeg = cv2.imdecode(np.frombuffer(
                    rgb_img, 'uint8', rgb_size), cv2.IMREAD_COLOR)
                if not jpeg is None:
                    # rgb = cv2.cvtColor(jpeg, cv2.COLOR_BGR2RGB)
                    rgb_img = jpeg.tobytes()
                else:
                    rgb_img = None
            # elif 0 == with_config[6]:
            #     yuv = np.frombuffer(rgb_img, 'uint8', rgb_size)
            #     print(len(yuv))
            #     if not yuv is None:
            #         rgb = cv2.cvtColor(yuv, cv2.COLOR_YUV420P2RGB)
            #         rgb_img = rgb.tobytes()
            #     else:
            #         rgb_img = None

        return (deepth_img, ir_img, status_img, rgb_img)
    
    '''
        @config, tuple (
            trigger_mode, 
            deep_mode, 
            deep_shift, 
            ir_mode, 
            status_mode, 
            status_mask, 
            rgb_mode, 
            rgb_res, 
            expose_time
        )

        @return void
    '''
    def __post_encode_config(self, config):
        try:
            with self.__session as s:
                timeout = 5
                r = s.post(
                    url='http://{}:{}/set_cfg'.format(self.HOST, self.PORT), 
                    data=config,
                    timeout=timeout
                )
                if(r.status_code != requests.codes.ok):
                    raise MediaSensorInitializationException(msg=f'Error: status_code={r.status_code}')            
        
        except requests.exceptions.Timeout as err:
            raise MediaSensorInitializationException(msg=f'Err: {err}; Timeout: {timeout}')
        except Exception as err:
            raise MediaSensorInitializationException()

    def __get_frame_from_http(self):
        with self.__session as s:
            r = s.get('http://{}:{}/getdeep'.format(self.HOST, self.PORT), stream=False)
            if(r.status_code == requests.codes.ok):
                # print('Get deep image')
                deepimg = r.content
                # print('Length={}'.format(len(deepimg)))
                (frameid, stamp_msec) = struct.unpack('<QQ', deepimg[0:8+8])
                # print((frameid, stamp_msec/1000))
                return deepimg
        
class MockCam(MediaSensor):

    def take_snapshot(self):
        '''
            @return images, list
        '''
        return [
            Image(
                image_pov=ImagePOV.SIDEWAY, 
                image_type=ImageType.RGB,
                image_res=ImageRes._320_240_1, 
                data=np.random.randint(0, 256, size=(1920, 1080, 3), dtype=np.uint8)
            )            
        ]