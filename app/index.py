import threading

from app.domain.providers.media_provider import MediaProvider
from app.domain.providers.agent_manager  import AgentManager

from app.domain.entities.basic import *
from app.data.datasource.datasource import Datasource

from flask import Flask, request, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Start Agents
threading.Thread(
    target = lambda agent_mgt: agent_mgt.run(), args=(AgentManager(),)
).start()

# Start MediaProvider
media_provider = MediaProvider()

@app.route("/capture", methods=['POST'])
def capture():
    params = request.get_json()
    action = params['action']

    if action == "start":
        media_provider.start(thing=params['thing'])
        return "Capture ON"
    else:
        media_provider.stop()
        return "Capture OFF"

@app.route("/docs", methods=['GET'])
def docs():
    return render_template(
        "docs.html", 
        items=Datasource().list_items()
    )

@app.route("/ping", methods=['GET'])
def ping():
    return 'on'