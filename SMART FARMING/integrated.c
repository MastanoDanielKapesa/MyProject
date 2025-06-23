#include <DHT.h>
#include <LiquidCrystal_I2C.h>
#include <SD.h>
#include <SoftwareSerial.h>

// Sensor pins
#define DHTPIN 2
#define DHTTYPE DHT22
#define MOISTURE_PIN A0
#define LDR_PIN A1
#define PH_PIN A2
#define WATER_LEVEL_PIN A3

// Actuator pins
#define PUMP_PIN 3
#define FAN_PIN 4
#define LIGHT_PIN 5
#define PH_UP_PUMP 6
#define PH_DOWN_PUMP 7
#define BUZZER_PIN 8  // For alarms

// Parameters
#define MOISTURE_THRESHOLD 40    // Percentage
#define TEMP_THRESHOLD_HIGH 30   // Celsius
#define TEMP_THRESHOLD_LOW 18     // Celsius
#define HUMIDITY_THRESHOLD_HIGH 80 // Percentage
#define HUMIDITY_THRESHOLD_LOW 40  // Percentage
#define LIGHT_THRESHOLD 300       // Lux
#define PH_TARGET 6.5
#define PH_TOLERANCE 0.3
#define WATER_LEVEL_CRITICAL 10   // Percentage

// Calibration values for pH sensor
#define PH_CALIBRATION_LOW 4.0
#define PH_CALIBRATION_HIGH 9.18
#define PH_RAW_LOW 150           // Raw ADC value at pH 4.0
#define PH_RAW_HIGH 850          // Raw ADC value at pH 9.18

DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal_I2C lcd(0x27, 16, 2);
SoftwareSerial gsm(10, 11); // RX, TX for GSM module

// Variables for sensor data averaging
const int numReadings = 5;
int moistureReadings[numReadings];
int lightReadings[numReadings];
int phReadings[numReadings];
int readIndex = 0;

void setup() {
  Serial.begin(9600);
  gsm.begin(9600);
  dht.begin();
  lcd.begin();
  lcd.backlight();
  
  // Initialize actuator pins
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(FAN_PIN, OUTPUT);
  pinMode(LIGHT_PIN, OUTPUT);
  pinMode(PH_UP_PUMP, OUTPUT);
  pinMode(PH_DOWN_PUMP, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  
  // Initialize sensor readings arrays
  for (int i = 0; i < numReadings; i++) {
    moistureReadings[i] = 0;
    lightReadings[i] = 0;
    phReadings[i] = 0;
  }
  
  initializeSDCard();
  displayWelcomeMessage();
}

void loop() {
  // Read sensors
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  
  // Check if any reads failed
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    lcd.clear();
    lcd.print("DHT Error");
    digitalWrite(BUZZER_PIN, HIGH);
    delay(1000);
    digitalWrite(BUZZER_PIN, LOW);
    return;
  }
  
  // Read analog sensors with averaging
  int soilMoistureRaw = analogRead(MOISTURE_PIN);
  int lightLevelRaw = analogRead(LDR_PIN);
  int phRaw = analogRead(PH_PIN);
  int waterLevelRaw = analogRead(WATER_LEVEL_PIN);
  
  // Add readings to arrays
  moistureReadings[readIndex] = soilMoistureRaw;
  lightReadings[readIndex] = lightLevelRaw;
  phReadings[readIndex] = phRaw;
  readIndex = (readIndex + 1) % numReadings;
  
  // Calculate averages
  int soilMoistureAvg = calculateAverage(moistureReadings);
  int lightLevelAvg = calculateAverage(lightReadings);
  int phRawAvg = calculateAverage(phReadings);
  
  // Convert readings to appropriate units
  int soilMoisture = map(soilMoistureAvg, 0, 1023, 0, 100);  // Percentage
  int lightLevel = map(lightLevelAvg, 0, 1023, 0, 1000);      // Lux approximation
  float pH = map(phRawAvg, PH_RAW_LOW, PH_RAW_HIGH, PH_CALIBRATION_LOW * 100, PH_CALIBRATION_HIGH * 100) / 100.0;
  int waterLevel = map(waterLevelRaw, 0, 1023, 0, 100);       // Percentage
  
  // Control systems
  controlIrrigation(soilMoisture, waterLevel);
  controlClimate(temperature, humidity);
  controlLighting(lightLevel);
  controlNutrients(pH);
  
  // Check for critical conditions
  checkCriticalConditions(waterLevel, temperature);
  
  // Display data
  displayData(temperature, humidity, soilMoisture, lightLevel, pH, waterLevel);
  
  // Log data
  logData(temperature, humidity, soilMoisture, lightLevel, pH, waterLevel);
  
  delay(10000); // Wait 10 seconds between readings
}

// Function implementations

void initializeSDCard() {
  Serial.print("Initializing SD card...");
  if (!SD.begin(9)) {  // CS pin 9
    Serial.println("SD card initialization failed!");
    lcd.clear();
    lcd.print("SD Card Error");
    digitalWrite(BUZZER_PIN, HIGH);
    delay(1000);
    digitalWrite(BUZZER_PIN, LOW);
    return;
  }
  Serial.println("SD card initialized.");
}

void displayWelcomeMessage() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(" Smart Farm 1.0 ");
  lcd.setCursor(0, 1);
  lcd.print("Initializing...");
  delay(2000);
}

int calculateAverage(int* readings) {
  int sum = 0;
  for (int i = 0; i < numReadings; i++) {
    sum += readings[i];
  }
  return sum / numReadings;
}

float readPH() {
  int rawValue = analogRead(PH_PIN);
  return map(rawValue, PH_RAW_LOW, PH_RAW_HIGH, PH_CALIBRATION_LOW * 100, PH_CALIBRATION_HIGH * 100) / 100.0;
}

void controlIrrigation(int moisture, int waterLevel) {
  static unsigned long lastWatering = 0;
  const unsigned long wateringInterval = 3600000; // 1 hour minimum between waterings
  
  if (waterLevel < WATER_LEVEL_CRITICAL) {
    sendAlert("Water tank critically low!");
    return; // Don't run pump if water is low
  }
  
  if (moisture < MOISTURE_THRESHOLD && millis() - lastWatering > wateringInterval) {
    digitalWrite(PUMP_PIN, HIGH);
    delay(5000); // Water for 5 seconds
    digitalWrite(PUMP_PIN, LOW);
    lastWatering = millis();
    logEvent("Irrigation activated");
  }
}

void controlClimate(float temp, float humidity) {
  // Temperature control
  if (temp > TEMP_THRESHOLD_HIGH) {
    digitalWrite(FAN_PIN, HIGH);
  } else if (temp < TEMP_THRESHOLD_LOW) {
    // In a real system, this would activate a heater
    digitalWrite(FAN_PIN, LOW);
  } else {
    digitalWrite(FAN_PIN, LOW);
  }
  
  // Humidity control (simple version)
  if (humidity > HUMIDITY_THRESHOLD_HIGH) {
    digitalWrite(FAN_PIN, HIGH); // Increase ventilation
  } else if (humidity < HUMIDITY_THRESHOLD_LOW) {
    // Could activate misters in a more advanced system
  }
}

void controlLighting(int light) {
  static bool lightsOn = false;
  static unsigned long lastCheck = 0;
  
  // Only check lighting every 30 minutes to prevent rapid switching
  if (millis() - lastCheck > 1800000) {
    if (light < LIGHT_THRESHOLD && !lightsOn) {
      digitalWrite(LIGHT_PIN, HIGH);
      lightsOn = true;
      logEvent("Grow lights activated");
    } else if (light >= LIGHT_THRESHOLD && lightsOn) {
      digitalWrite(LIGHT_PIN, LOW);
      lightsOn = false;
      logEvent("Grow lights deactivated");
    }
    lastCheck = millis();
  }
}

void controlNutrients(float pH) {
  static unsigned long lastAdjustment = 0;
  const unsigned long minAdjustmentInterval = 600000; // 10 minutes
  
  if (millis() - lastAdjustment > minAdjustmentInterval) {
    if (pH < PH_TARGET - PH_TOLERANCE) {
      // pH is too low, add pH up solution
      digitalWrite(PH_UP_PUMP, HIGH);
      delay(1000); // Adjust timing based on your system
      digitalWrite(PH_UP_PUMP, LOW);
      logEvent("pH Up solution added");
      lastAdjustment = millis();
    } else if (pH > PH_TARGET + PH_TOLERANCE) {
      // pH is too high, add pH down solution
      digitalWrite(PH_DOWN_PUMP, HIGH);
      delay(1000); // Adjust timing based on your system
      digitalWrite(PH_DOWN_PUMP, LOW);
      logEvent("pH Down solution added");
      lastAdjustment = millis();
    }
  }
}

void checkCriticalConditions(int waterLevel, float temp) {
  if (waterLevel < WATER_LEVEL_CRITICAL) {
    digitalWrite(BUZZER_PIN, HIGH);
    sendAlert("CRITICAL: Water level very low!");
    delay(1000);
    digitalWrite(BUZZER_PIN, LOW);
  }
  
  if (temp > TEMP_THRESHOLD_HIGH + 5 || temp < TEMP_THRESHOLD_LOW - 5) {
    sendAlert("CRITICAL: Temperature out of safe range!");
  }
}

void displayData(float temp, float humidity, int moisture, int light, float pH, int waterLevel) {
  lcd.clear();
  
  // Line 1: Temperature and Humidity
  lcd.setCursor(0, 0);
  lcd.print("T:");
  lcd.print(temp, 1);
  lcd.print("C H:");
  lcd.print(humidity, 0);
  lcd.print("%");
  
  // Line 2: Soil and Water
  lcd.setCursor(0, 1);
  lcd.print("S:");
  lcd.print(moisture);
  lcd.print("% W:");
  lcd.print(waterLevel);
  lcd.print("%");
  
  // Alternate display every 5 seconds
  static unsigned long lastChange = 0;
  if (millis() - lastChange > 5000) {
    lcd.clear();
    // Line 1: Light and pH
    lcd.setCursor(0, 0);
    lcd.print("L:");
    lcd.print(light);
    lcd.print(" pH:");
    lcd.print(pH, 1);
    
    // Line 2: System status
    lcd.setCursor(0, 1);
    lcd.print("System Normal");
    lastChange = millis();
  }
}

void logData(float temp, float humidity, int moisture, int light, float pH, int waterLevel) {
  File dataFile = SD.open("datalog.txt", FILE_WRITE);
  
  if (dataFile) {
    dataFile.print(millis());
    dataFile.print(",");
    dataFile.print(temp);
    dataFile.print(",");
    dataFile.print(humidity);
    dataFile.print(",");
    dataFile.print(moisture);
    dataFile.print(",");
    dataFile.print(light);
    dataFile.print(",");
    dataFile.print(pH);
    dataFile.print(",");
    dataFile.println(waterLevel);
    dataFile.close();
  } else {
    Serial.println("Error opening datalog.txt");
  }
}

void logEvent(const char* event) {
  File logFile = SD.open("events.txt", FILE_WRITE);
  
  if (logFile) {
    logFile.print(millis());
    logFile.print(",");
    logFile.println(event);
    logFile.close();
    Serial.println(event);
  } else {
    Serial.println("Error opening events.txt");
  }
}

void sendAlert(const char* message) {
  // Send SMS alert via GSM module
  gsm.println("AT+CMGF=1"); // Set SMS text mode
  delay(1000);
  gsm.println("AT+CMGS=\"+1234567890\""); // Replace with your phone number
  delay(1000);
  gsm.print(message);
  delay(1000);
  gsm.write(26); // CTRL+Z to send
  delay(1000);
  
  Serial.print("Alert sent: ");
  Serial.println(message);
}
