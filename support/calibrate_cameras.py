import matplotlib.pyplot as plt
import cv2, requests, struct
import numpy as np

def frame_config_decode(frame_config):
    '''
        @frame_config bytes

        @return fields, tuple (trigger_mode, deep_mode, deep_shift, ir_mode, status_mode, status_mask, rgb_mode, rgb_res, expose_time)
    '''
    return struct.unpack("<BBBBBBBBi", frame_config)


def frame_config_encode(
        trigger_mode=1, 
        deep_mode=1, 
        deep_shift=255, 
        ir_mode=1, 
        status_mode=2, 
        status_mask=7, 
        rgb_mode=1, 
        rgb_res=0, 
        expose_time=0):
    return struct.pack("<BBBBBBBBi",
                       trigger_mode, deep_mode, deep_shift, ir_mode, status_mode, status_mask, rgb_mode, rgb_res, expose_time)


def frame_payload_decode(frame_data: bytes, with_config: tuple):
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

    if (not rgb_img is None) and (1 == with_config[6]):
        jpeg = cv2.imdecode(np.frombuffer(
            rgb_img, 'uint8', rgb_size), cv2.IMREAD_COLOR)
        if not jpeg is None:
            rgb = cv2.cvtColor(jpeg, cv2.COLOR_BGR2RGB)
            rgb_img = rgb.tobytes()
        else:
            rgb_img = None

    return (deepth_img, ir_img, status_img, rgb_img)


HOST = '192.168.233.1'
PORT = 80

def post_encode_config(config=frame_config_encode(), host=HOST, port=PORT):
    r = requests.post('http://{}:{}/set_cfg'.format(host, port), config, timeout=5)
    print(r.status_code)
    if(r.status_code == requests.codes.ok):
        return True
    return False

def get_img_from_a075v(host=HOST, port=PORT):
    r = requests.get('http://{}:{}/getdeep'.format(host, port))
    if(r.status_code == requests.codes.ok):
        deepimg = r.content
        (frameid, stamp_msec) = struct.unpack('<QQ', deepimg[0:8+8])

        config = frame_config_decode(deepimg[16:16+12])
        frame_bytes = frame_payload_decode(deepimg[16+12:], config)

        depth = np.frombuffer(frame_bytes[0], 'uint16' if 0 == config[1] else 'uint8').reshape(240, 320)
        ir    = np.frombuffer(frame_bytes[1], 'uint16' if 0 == config[3] else 'uint8').reshape(240, 320)
        rgb = np.frombuffer(frame_bytes[3], 'uint8').reshape((480, 640, 3))

        return (depth, ir, rgb)

if post_encode_config(frame_config_encode(1, 1, 255, 0, 2, 7, 1, 0, 0)):
    with plt.ion():
        fig = plt.figure('2D frame', figsize=(20, 12), clear=True)
        while True:
            depth, ir, rgb = get_img_from_a075v()
            
            ax1 = fig.add_subplot(221)
            ax1.imshow(depth, cmap='jet_r')

            ax2 = fig.add_subplot(222)
            ax2.imshow(rgb)

            ax3 = fig.add_subplot(223)
            ax3.imshow(ir)

            ax4 = fig.add_subplot(224)
            ax4.imshow(np.random.randint(0, 256, size=(1080, 1920, 3), dtype=np.uint8), cmap='gray')
            
            # 停顿时间
            plt.pause(0.1)
            # 清除当前画布
            fig.clear()