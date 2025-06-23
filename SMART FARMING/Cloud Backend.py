from flask import Flask, jsonify, request
from flask_mqtt import Mqtt
from datetime import datetime
import json
from pymongo import MongoClient

app = Flask(__name__)

# MQTT Configuration
app.config['MQTT_BROKER_URL'] = 'mqtt.eclipseprojects.io'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_KEEPALIVE'] = 60

mqtt = Mqtt(app)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['smart_farm']
sensors_collection = db['sensor_data']
actions_collection = db['irrigation_actions']

@app.route('/api/data', methods=['GET'])
def get_data():
    field = request.args.get('field', 'field1')
    limit = int(request.args.get('limit', 100))
    
    data = list(sensors_collection.find({'node_id': field})
                             .sort('timestamp', -1)
                             .limit(limit))
    
    # Convert ObjectId to string for JSON serialization
    for item in data:
        item['_id'] = str(item['_id'])
    
    return jsonify(data)

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    # Implement analytics logic (e.g., daily averages, trends)
    return jsonify({"status": "Analytics endpoint"})

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('farm/+/sensors')
    mqtt.subscribe('farm/+/control')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    topic = message.topic
    payload = json.loads(message.payload.decode())
    
    if 'sensors' in topic:
        sensors_collection.insert_one(payload)
    elif 'control' in topic:
        actions_collection.insert_one(payload)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
