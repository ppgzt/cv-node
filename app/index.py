from app.services.media_capture_proxy import MediaCaptureProxy
from flask import Flask, request

app = Flask(__name__)
orc = MediaCaptureProxy()

@app.route("/capture", methods=['POST'])
def capture():
    params = request.get_json()
    action = params['action']

    if action == "start":
        orc.start()
        return "Capturing media at 60FPS"
    else:
        orc.stop()
        return "Capture stoped"
