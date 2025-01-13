import threading

from app.domain.providers.media_provider import MediaProvider
from app.domain.providers.image_info_sync_provider import ImageInfoSyncProvider
from app.domain.providers.image_data_sync_provider import ImageDataSyncProvider
from app.domain.providers.agent_manager  import AgentManager

from app.domain.entities.basic import *
from app.data.datasource.datasource import Datasource
from app.data.datasource.firebase_datasource import FirebaseDatasource

from flask import Flask, request, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Create DB
FirebaseDatasource()
Datasource()

# Start Agents
threading.Thread(
    target = lambda agent_mgt: agent_mgt.run(), args=(AgentManager(),)
).start()

# Instance SynchProvider
img_info_sync_provider = ImageInfoSyncProvider()
img_data_sync_provider = ImageDataSyncProvider()

# Start MediaProvider
media_provider = MediaProvider()

@app.route("/capture", methods=['POST'])
def capture():
    params = request.get_json()
    action = params['action']

    if action == "start":
        media_provider.start(data=params['data'])
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

@app.route("/img-info-sync", methods=['GET'])
def data_sync():
    img_info_sync_provider.start()
    return 'synch on'

@app.route("/img-data-sync", methods=['GET'])
def image_sync():
    img_data_sync_provider.start()
    return 'synch on'