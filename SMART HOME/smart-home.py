import paho.mqtt.client as mqtt
import time
from datetime import datetime
import json
import threading
from abc import ABC, abstractmethod

# Configuration
MQTT_BROKER = "your-broker.com"  # e.g., "localhost", "test.mosquitto.org"
MQTT_PORT = 1883

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT)

# Topics to publish to:
def publish_device_status(device_id, state):
    client.publish(
        f"home/{device_id}/status",  # Topic pattern
        json.dumps({
            "state": state,
            "timestamp": datetime.now().isoformat()
        })
    )

def publish_camera_feed(camera_id, image_url):
    client.publish(
        f"home/camera/{camera_id}/feed",  # Topic pattern
        json.dumps({
            "image_url": image_url,
            "timestamp": datetime.now().isoformat()
        })
    )

def publish_camera_feed(camera_id, image_url):
    client.publish(
        f"home/camera/front-door/feed",  # Topic pattern
        json.dumps({
            "image_url": "htpp://your-camera server/front-door.jpg",
            "timestamp": datetime.now().isoformat(),
            "status": "online"
        })
    )
    client.publish(
        "home/security/motion",
        json.dumps({
            "location": "Front-Door",
            "camera_id": "Front-Door",
            "type": "motion",
            "timestamp": datetime.now().isoformat()
        })
    )

def publish_security_alert(sensor_id, message):
    client.publish(
        "home/security/alerts",  # Single alert topic
        json.dumps({
            "sensor": sensor_id,
            "message": message,
            "severity": "high",  # or "medium"/"low"
            "timestamp": datetime.now().isoformat()
        })
    )

# Base Device Class
class SmartDevice(ABC):
    def __init__(self, device_id, name):
        self.device_id = device_id
        self.name = name
        self.status = "off"
        self.last_updated = datetime.now().isoformat()

    @abstractmethod
    def turn_on(self):
        pass

    @abstractmethod
    def turn_off(self):
        pass

    def get_status(self):
        return {
            "device_id": self.device_id,
            "name": self.name,
            "status": self.status,
            "last_updated": self.last_updated
        }

# Concrete Device Classes
class SmartLight(SmartDevice):
    def __init__(self, device_id, name, brightness=50):
        super().__init__(device_id, name)
        self.brightness = brightness
        self.color = "white"

    def turn_on(self):
        self.status = "on"
        self.last_updated = datetime.now().isoformat()
        print(f"{self.name} light turned on")

    def turn_off(self):
        self.status = "off"
        self.last_updated = datetime.now().isoformat()
        print(f"{self.name} light turned off")

    def set_brightness(self, level):
        if 0 <= level <= 100:
            self.brightness = level
            self.last_updated = datetime.now().isoformat()
            print(f"{self.name} brightness set to {level}%")
        else:
            print("Brightness level must be between 0 and 100")

    def set_color(self, color):
        self.color = color
        self.last_updated = datetime.now().isoformat()
        print(f"{self.name} color changed to {color}")

    def get_status(self):
        status = super().get_status()
        status.update({
            "brightness": self.brightness,
            "color": self.color,
            "type": "light"
        })
        return status


class SmartThermostat(SmartDevice):
    def __init__(self, device_id, name, current_temp=22, target_temp=22):
        super().__init__(device_id, name)
        self.current_temp = current_temp
        self.target_temp = target_temp
        self.mode = "cool"  # heat, cool, auto

    def turn_on(self):
        self.status = "on"
        self.last_updated = datetime.now().isoformat()
        print(f"{self.name} thermostat turned on")

    def turn_off(self):
        self.status = "off"
        self.last_updated = datetime.now().isoformat()
        print(f"{self.name} thermostat turned off")

    def set_temperature(self, temp):
        self.target_temp = temp
        self.last_updated = datetime.now().isoformat()
        print(f"{self.name} target temperature set to {temp}°C")

    def set_mode(self, mode):
        if mode in ["heat", "cool", "auto"]:
            self.mode = mode
            self.last_updated = datetime.now().isoformat()
            print(f"{self.name} mode set to {mode}")
        else:
            print("Invalid mode. Must be 'heat', 'cool', or 'auto'")

    def get_status(self):
        status = super().get_status()
        status.update({
            "current_temp": self.current_temp,
            "target_temp": self.target_temp,
            "mode": self.mode,
            "type": "thermostat"
        })
        return status


class SmartLock(SmartDevice):
    def __init__(self, device_id, name):
        super().__init__(device_id, name)
        self.status = "locked"

    def turn_on(self):
        self.lock()

    def turn_off(self):
        self.unlock()

    def lock(self):
        self.status = "locked"
        self.last_updated = datetime.now().isoformat()
        print(f"{self.name} locked")

    def unlock(self):
        self.status = "unlocked"
        self.last_updated = datetime.now().isoformat()
        print(f"{self.name} unlocked")

    def get_status(self):
        status = super().get_status()
        status.update({
            "type": "lock"
        })
        return status


# Sensor Class
class Sensor:
    def __init__(self, sensor_id, name, sensor_type):
        self.sensor_id = sensor_id
        self.name = name
        self.type = sensor_type
        self.value = None
        self.last_updated = datetime.now().isoformat()

    def update_value(self, value):
        self.value = value
        self.last_updated = datetime.now().isoformat()
        print(f"{self.name} {self.type} sensor updated: {value}")

    def get_status(self):
        return {
            "sensor_id": self.sensor_id,
            "name": self.name,
            "type": self.type,
            "value": self.value,
            "last_updated": self.last_updated
        }


# Automation Rule Class
class AutomationRule:
    def __init__(self, rule_id, name, condition, actions):
        self.rule_id = rule_id
        self.name = name
        self.condition = condition  # Function that returns True/False
        self.actions = actions  # List of functions to execute
        self.enabled = True

    def check_and_execute(self, home):
        if self.enabled and self.condition(home):
            print(f"Executing rule: {self.name}")
            for action in self.actions:
                action(home)

    def get_status(self):
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "enabled": self.enabled
        }


# Smart Home Class
class SmartHome:
    def __init__(self, name):
        self.name = name
        self.devices = {}
        self.sensors = {}
        self.rules = {}
        self.schedules = []
        self.running = False

    def add_device(self, device):
        self.devices[device.device_id] = device

    def add_sensor(self, sensor):
        self.sensors[sensor.sensor_id] = sensor

    def add_rule(self, rule):
        self.rules[rule.rule_id] = rule

    def add_schedule(self, schedule):
        self.schedules.append(schedule)

    def get_device(self, device_id):
        return self.devices.get(device_id)

    def get_sensor(self, sensor_id):
        return self.sensors.get(sensor_id)

    def get_status(self):
        devices_status = {id: device.get_status() for id, device in self.devices.items()}
        sensors_status = {id: sensor.get_status() for id, sensor in self.sensors.items()}
        rules_status = {id: rule.get_status() for id, rule in self.rules.items()}

        return {
            "name": self.name,
            "devices": devices_status,
            "sensors": sensors_status,
            "rules": rules_status,
            "schedules": [s.__dict__ for s in self.schedules],
            "running": self.running
        }

    def start(self):
        self.running = True
        print(f"{self.name} smart home system started")
        self._monitor()

    def stop(self):
        self.running = False
        print(f"{self.name} smart home system stopped")

    def _monitor(self):
        def monitor_loop():
            while self.running:
                # Check all rules
                for rule in self.rules.values():
                    rule.check_and_execute(self)

                # Check schedules
                now = datetime.now()
                for schedule in self.schedules:
                    if schedule.time.hour == now.hour and schedule.time.minute == now.minute:
                        schedule.execute(self)

                time.sleep(1)

        monitor_thread = threading.Thread(target=monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()


# Schedule Class
class Schedule:
    def __init__(self, time, actions):
        self.time = time  # datetime.time object
        self.actions = actions  # List of functions to execute

    def execute(self, home):
        print(f"Executing scheduled actions at {self.time}")
        for action in self.actions:
            action(home)


# Example Usage
if __name__ == "__main__":
    # Create a smart home
    my_home = SmartHome("My Smart Home")

    # Add devices
    living_room_light = SmartLight("light1", "Living Room Light")
    bedroom_light = SmartLight("light2", "Bedroom Light")
    thermostat = SmartThermostat("thermo1", "Living Room Thermostat")
    front_door_lock = SmartLock("lock1", "Front Door Lock")

    my_home.add_device(living_room_light)
    my_home.add_device(bedroom_light)
    my_home.add_device(thermostat)
    my_home.add_device(front_door_lock)

    # Add sensors
    motion_sensor = Sensor("motion1", "Living Room Motion Sensor", "motion")
    temp_sensor = Sensor("temp1", "Living Room Temperature Sensor", "temperature")
    my_home.add_sensor(motion_sensor)
    my_home.add_sensor(temp_sensor)

    # Define some automation rules
    def motion_detected(home):
        motion_sensor = home.get_sensor("motion1")
        return motion_sensor and motion_sensor.value == "motion detected"

    def turn_on_lights(home):
        home.get_device("light1").turn_on()
        home.get_device("light2").turn_on()

    def no_motion_for_5min(home):
        # Simplified for example - in real implementation would track time
        motion_sensor = home.get_sensor("motion1")
        return motion_sensor and motion_sensor.value == "no motion"

    def turn_off_lights(home):
        home.get_device("light1").turn_off()
        home.get_device("light2").turn_off()

    motion_rule = AutomationRule(
        "rule1",
        "Turn on lights when motion detected",
        motion_detected,
        [turn_on_lights]
    )

    no_motion_rule = AutomationRule(
        "rule2",
        "Turn off lights when no motion for 5 minutes",
        no_motion_for_5min,
        [turn_off_lights]
    )

    my_home.add_rule(motion_rule)
    my_home.add_rule(no_motion_rule)

    # Add a schedule
    from datetime import time as dt_time

    def morning_routine(home):
        home.get_device("light1").turn_on()
        home.get_device("thermo1").set_temperature(21)

    morning_schedule = Schedule(
        dt_time(7, 0),  # 7:00 AM
        [morning_routine]
    )
    my_home.add_schedule(morning_schedule)

    # Start the system
    my_home.start()

    # Simulate some sensor updates
    print("\nSimulating motion detection...")
    motion_sensor.update_value("motion detected")
    time.sleep(2)

    print("\nSimulating no motion...")
    motion_sensor.update_value("no motion")
    time.sleep(2)

    # Print current status
    print("\nCurrent home status:")
    print(json.dumps(my_home.get_status(), indent=2))

    # Stop the system after some time
    time.sleep(5)
    my_home.stop()
