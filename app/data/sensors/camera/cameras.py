import struct
import numpy as np
import cv2
import requests

class CameraSensor:

    # return a map<ImageType, data>
    def get_frame(self):
        pass

class MaixSenseA075V(CameraSensor):

    def __init__(self):
        self.HOST = '192.168.233.1'
        self.PORT = 80

    def __frame_config_decode(self, frame_config):
        '''
            @frame_config bytes

            @return fields, tuple (trigger_mode, deep_mode, deep_shift, ir_mode, status_mode, status_mask, rgb_mode, rgb_res, expose_time)
        '''
        return struct.unpack("<BBBBBBBBi", frame_config)


    def __frame_config_encode(self, trigger_mode=1, deep_mode=1, deep_shift=255, ir_mode=1, status_mode=2, status_mask=7, rgb_mode=1, rgb_res=0, expose_time=0):
        '''
            @trigger_mode, deep_mode, deep_shift, ir_mode, status_mode, status_mask, rgb_mode, rgb_res, expose_time

            @return frame_config bytes
        '''
        return struct.pack("<BBBBBBBBi",
                        trigger_mode, deep_mode, deep_shift, ir_mode, status_mode, status_mask, rgb_mode, rgb_res, expose_time)


    def __frame_payload_decode(self, frame_data: bytes, with_config: tuple):
        '''
            @frame_data, bytes

            @with_config, tuple (trigger_mode, deep_mode, deep_shift, ir_mode, status_mode, status_mask, rgb_mode, rgb_res, expose_time)

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
                    rgb = cv2.cvtColor(jpeg, cv2.COLOR_BGR2RGB)
                    rgb_img = rgb.tobytes()
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

    def __post_encode_config(self, config):
        r = requests.post('http://{}:{}/set_cfg'.format(self.HOST, self.PORT), config)
        if(r.status_code == requests.codes.ok):
            return True
        return False

    def __post_CameraParmsBytes(self, cameraParms:bytes):
        r = requests.post('http://{}:{}/calibration'.format(self.HOST, self.PORT), cameraParms)
        if(r.status_code == requests.codes.ok):
            print("ok")

    def __show_frame(self, frame_data: bytes):
        config = self.__frame_config_decode(frame_data[16:16+12])
        frame_bytes = self.__frame_payload_decode(frame_data[16+12:], config)

        depth = np.frombuffer(frame_bytes[0], 'uint16' if 0 == config[1] else 'uint8').reshape(
            240, 320) if frame_bytes[0] else None

        ir = np.frombuffer(frame_bytes[1], 'uint16' if 0 == config[3] else 'uint8').reshape(
            240, 320) if frame_bytes[1] else None

        status = np.frombuffer(frame_bytes[2], 'uint16' if 0 == config[4] else 'uint8').reshape(
            240, 320) if frame_bytes[2] else None

        rgb = np.frombuffer(frame_bytes[3], 'uint8').reshape(
            (480, 640, 3) if config[6] == 1 else (600, 800, 3)) if frame_bytes[3] else None

        figsize = (12, 12)
        # fig = plt.figure(figsize=figsize)

        # ax1 = fig.add_subplot(221)
        # if not depth is None:
        #     ax1.imshow(depth)
        #     # np.save("fg1.npy", depth)
        #     # np.savetxt("depth.csv", (depth/4).astype('uint16'), delimiter="," )
        # ax2 = fig.add_subplot(222)
        # if not ir is None:
        #     ax2.imshow(ir)
        # ax3 = fig.add_subplot(223)
        # if not status is None:
        #     ax3.imshow(status)
        # ax4 = fig.add_subplot(224)
        # if not rgb is None:
        #     ax4.imshow(rgb)        

    def __get_frame_from_http(self):
        r = requests.get('http://{}:{}/getdeep'.format(self.HOST, self.PORT))
        if(r.status_code == requests.codes.ok):
            print('Get deep image')
            deepimg = r.content
            print('Length={}'.format(len(deepimg)))
            (frameid, stamp_msec) = struct.unpack('<QQ', deepimg[0:8+8])
            print((frameid, stamp_msec/1000))
            return deepimg
        
    def get_frame(self):
        if self.__post_encode_config(self.__frame_config_encode(1,0,255,0,2,7,1,0,0)):
            raw = self.__get_frame_from_http()
            
            config = self.__frame_config_decode(raw[16:16+12])
            frame_bytes = self.__frame_payload_decode(raw[16+12:], config)

            rgb = np.frombuffer(frame_bytes[3], 'uint8').reshape(
                (480, 640, 3) if config[6] == 1 else (600, 800, 3)) if frame_bytes[3] else None
            
            return rgb

        return None