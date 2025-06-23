import time
import random
import json
from datetime import datetime
import paho.mqtt.client as mqtt

# Sensor simulation (in real implementation, use actual sensor libraries)
class SoilSensor:
    def read_moisture(self):
        return random.uniform(10, 60)  # Percentage
    
    def read_temperature(self):
        return random.uniform(10, 35)  # Celsius
    
    def read_npk(self):
        return {
            'nitrogen': random.uniform(0, 100),
            'phosphorus': random.uniform(0, 80),
            'potassium': random.uniform(0, 120)
        }

class WeatherStation:
    def read_conditions(self):
        return {
            'air_temp': random.uniform(5, 40),
            'humidity': random.uniform(20, 95),
            'rainfall': random.uniform(0, 10),
            'wind_speed': random.uniform(0, 25)
        }

# MQTT Configuration
BROKER = 'mqtt.eclipseprojects.io'
PORT = 1883
TOPIC = 'farm/field1/sensors'

client = mqtt.Client()
client.connect(BROKER, PORT)

soil_sensor = SoilSensor()
weather_station = WeatherStation()

while True:
    # Read sensor data
    data = {
        'timestamp': datetime.now().isoformat(),
        'soil': {
            'moisture': soil_sensor.read_moisture(),
            'temperature': soil_sensor.read_temperature(),
            'npk': soil_sensor.read_npk()
        },
        'weather': weather_station.read_conditions(),
        'node_id': 'field1_node1'
    }
    
    # Publish to MQTT broker
    client.publish(TOPIC, json.dumps(data))
    print(f"Published: {data}")
    
    time.sleep(300)  # Send data every 5 minutes
