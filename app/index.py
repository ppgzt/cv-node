from app.domain.providers.media_provider import MediaProvider
from app.domain.providers.agent_manager  import AgentManager

from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

agent_manager = AgentManager()
media_providr = MediaProvider()

@app.route("/capture", methods=['POST'])
def capture():
    params = request.get_json()
    action = params['action']

    if action == "start":
        media_providr.start(params['thing'])
        return "Capturing media at 60FPS"
    else:
        media_providr.stop()
        return "Capture stoped"
