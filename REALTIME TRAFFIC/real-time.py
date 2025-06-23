import time
import random
import threading
from datetime import datetime
import json
from collections import defaultdict
import heapq

class TrafficLight:
    client.publish('traffic/TL1/sensor', json.dumps({
        'node_id': 'TL1',
        'location': 'Main St & 1st Ave',
        'vehicle_count': 45,
        'avg_speed': 32,
        'light_state': 'green',
        'timestamp': datetime.now().isoformat()
    }))

# for camera feeds
client.publish('traffic/camera/cam1', json.dumps({
    'image_url': 'http://your-server/cam1.jpg',
    'timestamp': datetime.now().isoformat(),
    'location': 'Main St & 1st Ave'
}))

# for anomalies
client.publish('traffic/anomaly', json.dumps({
    'node_id': 'TL1',
    'anomaly_score': 0.82,
    'location': 'Main St & 1st Ave',
    'timestamp': datetime.now().isoformat()
}))
    def __init__(self, id, location):
        self.id = id
        self.location = location
        self.state = "red"  # red, yellow, green
        self.timer = 0
        self.default_green_duration = 30  # seconds
        self.last_changed = datetime.now()
        
    def change_state(self, new_state):
        self.state = new_state
        self.last_changed = datetime.now()
        print(f"Traffic light {self.id} at {self.location} changed to {new_state}")
        
    def update(self):
        """Update light state based on timer"""
        if self.state == "green" and self.timer <= 0:
            self.change_state("yellow")
            self.timer = 3  # 3 seconds for yellow
        elif self.state == "yellow" and self.timer <= 0:
            self.change_state("red")
            self.timer = self.default_green_duration  # Reset timer for next cycle
        elif self.state == "red" and self.timer <= 0:
            self.change_state("green")
            self.timer = self.default_green_duration
            
        self.timer -= 1
        
    def adjust_timing(self, duration):
        """Dynamically adjust green light duration"""
        if self.state == "green":
            remaining = max(5, min(duration, 60))  # Keep between 5-60 seconds
            self.timer = remaining
            print(f"Adjusted {self.id} green duration to {remaining}s")
            
    def get_status(self):
        return {
            "id": self.id,
            "location": self.location,
            "state": self.state,
            "timer": self.timer,
            "last_changed": self.last_changed.isoformat()
        }

class VehicleSensor:
    def __init__(self, id, location):
        self.id = id
        self.location = location
        self.vehicle_count = 0
        self.speed_readings = []
        self.last_updated = datetime.now()
        
    def detect_vehicle(self, speed):
        self.vehicle_count += 1
        self.speed_readings.append(speed)
        self.last_updated = datetime.now()
        
    def get_reading(self, window_seconds=60):
        """Get readings from the last time window"""
        now = datetime.now()
        recent_readings = [
            speed for speed in self.speed_readings
            if (now - self.last_updated).total_seconds() <= window_seconds
        ]
        
        avg_speed = sum(recent_readings)/len(recent_readings) if recent_readings else 0
        return {
            "id": self.id,
            "location": self.location,
            "vehicle_count": len(recent_readings),
            "avg_speed": avg_speed,
            "last_updated": self.last_updated.isoformat()
        }

class TrafficManagementSystem:
    def __init__(self):
        self.traffic_lights = {}
        self.sensors = {}
        self.emergency_vehicles = set()
        self.intersections = defaultdict(list)
        self.adaptive_timing_enabled = True
        self.running = False
        self.event_log = []
        
    def add_traffic_light(self, light):
        self.traffic_lights[light.id] = light
        self.intersections[light.location].append(light.id)
        
    def add_sensor(self, sensor):
        self.sensors[sensor.id] = sensor
        
    def register_emergency_vehicle(self, vehicle_id):
        self.emergency_vehicles.add(vehicle_id)
        print(f"Emergency vehicle {vehicle_id} registered - prioritizing route")
        self.prioritize_emergency_route(vehicle_id)
        
    def prioritize_emergency_route(self, vehicle_id):
        """Simple emergency vehicle prioritization"""
        for light_id, light in self.traffic_lights.items():
            if "hospital" in light.location.lower() or "main" in light.location.lower():
                light.change_state("green")
                light.timer = 20  # Extend green time
                
    def adaptive_timing_control(self):
        """Adjust traffic light timing based on sensor data"""
        if not self.adaptive_timing_enabled:
            return
            
        for location, light_ids in self.intersections.items():
            # Get all sensors at this intersection
            sensors = [s for s in self.sensors.values() if s.location == location]
            if not sensors:
                continue
                
            total_vehicles = sum(sensor.get_reading()["vehicle_count"] for sensor in sensors)
            avg_speed = sum(sensor.get_reading()["avg_speed"] for sensor in sensors) / len(sensors)
            
            # Simple adaptive logic - can be enhanced
            for light_id in light_ids:
                light = self.traffic_lights[light_id]
                if light.state == "green":
                    # Increase green time if many vehicles or low speed (indicating congestion)
                    adjustment = min(60, light.default_green_duration + (total_vehicles // 5))
                    light.adjust_timing(adjustment)
                    
    def detect_congestion(self, threshold=10):
        """Identify congested areas based on vehicle count and speed"""
        congested = []
        for sensor in self.sensors.values():
            reading = sensor.get_reading()
            if (reading["vehicle_count"] > threshold and 
                reading["avg_speed"] < 20):  # km/h
                congested.append(sensor.location)
        return congested
    
    def optimize_route(self, start, end):
        """Simple route optimization avoiding congested areas"""
        # This is a simplified version - real implementation would use graph algorithms
        congested = self.detect_congestion()
        if not congested:
            return f"Direct route from {start} to {end}"
        else:
            return f"Alternative route avoiding {', '.join(congested)}"
    
    def start(self):
        self.running = True
        print("Traffic Management System started")
        self.monitor_thread = threading.Thread(target=self._monitor)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop(self):
        self.running = False
        print("Traffic Management System stopped")
        
    def _monitor(self):
        while self.running:
            # Update all traffic lights
            for light in self.traffic_lights.values():
                light.update()
                
            # Adaptive timing control
            if self.adaptive_timing_enabled:
                self.adaptive_timing_control()
                
            # Simulate sensor data (in real system this would come from actual sensors)
            self._simulate_sensor_data()
            
            time.sleep(1)
            
    def _simulate_sensor_data(self):
        """Simulate vehicle detection for demo purposes"""
        for sensor in self.sensors.values():
            if random.random() > 0.7:  # 30% chance of vehicle detection
                speed = random.randint(20, 80)  # Random speed between 20-80 km/h
                sensor.detect_vehicle(speed)
                
    def get_system_status(self):
        lights_status = {light_id: light.get_status() for light_id, light in self.traffic_lights.items()}
        sensors_status = {sensor_id: sensor.get_reading() for sensor_id, sensor in self.sensors.items()}
        
        return {
            "timestamp": datetime.now().isoformat(),
            "traffic_lights": lights_status,
            "sensors": sensors_status,
            "congestion": self.detect_congestion(),
            "emergency_vehicles": list(self.emergency_vehicles),
            "adaptive_timing": self.adaptive_timing_enabled
        }
    
    

# Example Usage
if __name__ == "__main__":
    # Create system
    tms = TrafficManagementSystem()
    
    # Add traffic lights
    tms.add_traffic_light(TrafficLight("TL1", "Main St & 1st Ave"))
    tms.add_traffic_light(TrafficLight("TL2", "Main St & 2nd Ave"))
    tms.add_traffic_light(TrafficLight("TL3", "Elm St & 1st Ave"))
    tms.add_traffic_light(TrafficLight("TL4", "Hospital Entrance"))
    
    # Add sensors
    tms.add_sensor(VehicleSensor("VS1", "Main St & 1st Ave"))
    tms.add_sensor(VehicleSensor("VS2", "Main St & 2nd Ave"))
    tms.add_sensor(VehicleSensor("VS3", "Elm St & 1st Ave"))
    tms.add_sensor(VehicleSensor("VS4", "Hospital Entrance"))
    
    # Start system
    tms.start()

    BROKER = 'localhost'
    
    # Simulate system running
    try:
        for i in range(10):
            # Randomly register emergency vehicle
            if i == 3:
                tms.register_emergency_vehicle("AMB-123")
                
            # Print status every 2 iterations
            if i % 2 == 0:
                print("\nSystem Status:")
                print(json.dumps(tms.get_system_status(), indent=2))
                
            time.sleep(5)
    finally:
        tms.stop()
