import requests, struct

HOST = '192.168.233.1'
PORT = 80

r = requests.get('http://{}:{}/getinfo'.format(HOST, PORT))
if(r.status_code == requests.codes.ok):
    lenscoeff_bin = r.content
    (_fx,_fy,_cx,_cy) = struct.unpack('<ffff', lenscoeff_bin[41:41+4*4])
    print(_fx,_fy,_cx,_cy)
