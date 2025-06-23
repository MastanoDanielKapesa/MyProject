import paho.mqtt.client as mqtt
import json
from gpiozero import Device, OutputDevice  # For actual hardware control
from gpiozero.pins.mock import MockFactory
import warnings

#suppress specific deprecation warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

# Set appropriate pin factory
try:
    from gpiozero.pins.rpigpio import RPiGPIOFactory
    Device.pin_factory = RPiGPIOFactory()
except ImportError:
    Device.pin_factory = MockFactory()

# MQTT Configuration
BROKER = 'mqtt.eclipseprojects.io'
PORT = 1883
SENSOR_TOPIC = 'farm/field1/sensors'
CONTROL_TOPIC = 'farm/field1/control'

# initiate hardware
valve = OutputDevice(17) # GPIO pin for valve control

def on_message(client, userdata, message):
    """Handle incoming MQTT messages with API version 2"""
    try:
        data = json.loads(message.payload.decode())

        soil_moisture = data['soil']['moisture']
        rainfall = data['weather']['rainfall']

# Irrigation thresholds
MOISTURE_THRESHOLD = 30  # Percentage
RAIN_THRESHOLD = 5       # mm

valve = OutputDevice(17)  # GPIO pin for valve control

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    
    soil_moisture = data['soil']['moisture']
    rainfall = data['weather']['rainfall']
    
    # Decision logic
    if soil_moisture < 30 and rainfall < 5: #threshhold values
        valve.on()
        status = "Irrigation ON"
    else:
        valve.off()
        status = "Irrigation OFF"
    
    # Send status update
    client.publish(
        CONTROL_TOPIC,
        payload=json.dumps({
        'timestamp': data['timestamp'],
        'status': status,
        'moisture': soil_moisture,
        'rainfall': rainfall
    }),
    qos=1)
except Exception as e:
    print("error processing message:{e}")

def on_connect(client, userdata, flags, reason_code, properties):
    """Connect callback with API version 2"""
    if reason_code == 0:
        print("Successfully connected to MQTT broker")
        client.subscribe(SENSOR_TOPIC, qos=1)
    else:
        print("Connection failed with code {reason_code}")

def main():
# initiate MQTT client with explicit API version
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# set callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to broker
client.connect(BROKER, PORT)

print("Irrigation controller running (updated MQTT API version)...")
client.loop_forever()

if __name__ == '__main__':
    main()
 