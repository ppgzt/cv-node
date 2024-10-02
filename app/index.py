from app.domain.providers.media_provider import MediaProvider

from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

orc = MediaProvider()

@app.route("/capture", methods=['POST'])
def capture():
    params = request.get_json()
    action = params['action']

    if action == "start":
        orc.start(params['thing'])
        return "Capturing media at 60FPS"
    else:
        orc.stop()
        return "Capture stoped"
