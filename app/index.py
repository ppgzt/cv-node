import threading, os

from datetime import datetime

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
        job_id = Datasource().insert_job(job=Job())

        media_provider.start(thing=params['thing'], job_id=job_id)
        return "Capturing media at 60FPS"
    else:
        media_provider.stop()
        return "Capture stoped"

@app.route("/docs", methods=['GET'])
def docs():
    return render_template("docs.html", items=Datasource().list_items())

@app.route("/reset", methods=['GET'])
def reset():
    now = datetime.now()
    os.rename("cv-node-data/db/cvnode.json", f"cv-node-data/db/cvnode_{now.microsecond}.json")
    return 'OK'