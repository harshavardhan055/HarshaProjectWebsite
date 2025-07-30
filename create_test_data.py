#!/usr/bin/env python3
"""
Script to create test data for the Harsha Projects website
"""
from app import app, db
from models import User, Project, Testing, ProjectComment, ProjectRating
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_test_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create owner/admin user (ID will be 1)
        admin_user = User(
            username='harsha',
            email='harsha@example.com',
            password_hash=generate_password_hash('admin123'),
            interests='electronics,arduino,programming,robotics',
            is_verified=True
        )
        db.session.add(admin_user)
        db.session.commit()
        
        # Create a test user
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('test123'),
            interests='programming,web_development',
            is_verified=True
        )
        db.session.add(test_user)
        db.session.commit()
        
        # Create sample projects
        projects = [
            {
                'title': 'Arduino LED Controller',
                'description': 'A smart LED controller using Arduino with WiFi connectivity. This project allows remote control of LED strips with various patterns and colors.',
                'code': '''
#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "your_wifi";
const char* password = "your_password";

WebServer server(80);

void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  
  server.on("/", handleRoot);
  server.on("/led/on", handleLEDOn);
  server.on("/led/off", handleLEDOff);
  server.begin();
}

void loop() {
  server.handleClient();
}

void handleRoot() {
  server.send(200, "text/html", "<h1>LED Controller</h1>");
}
                ''',
                'connections': 'LED strip connected to pin 13, WiFi module to pins 2,3',
                'procedure': 'Step 1: Connect components\nStep 2: Upload code\nStep 3: Configure WiFi\nStep 4: Test remote control',
                'user_id': 1
            },
            {
                'title': 'Raspberry Pi Weather Station',
                'description': 'Complete weather monitoring system using Raspberry Pi with temperature, humidity, and pressure sensors.',
                'code': '''
import time
import board
import adafruit_dht
import adafruit_bmp280

# Initialize sensors
dht = adafruit_dht.DHT22(board.D4)
i2c = board.I2C()
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

while True:
    try:
        temperature = dht.temperature
        humidity = dht.humidity
        pressure = bmp280.pressure
        
        print(f"Temp: {temperature:.1f}C")
        print(f"Humidity: {humidity:.1f}%")
        print(f"Pressure: {pressure:.2f} hPa")
        
    except RuntimeError as error:
        print(error.args[0])
    
    time.sleep(30)
                ''',
                'connections': 'DHT22 to GPIO4, BMP280 to I2C pins (SDA, SCL)',
                'procedure': 'Step 1: Wire sensors\nStep 2: Install libraries\nStep 3: Run calibration\nStep 4: Start monitoring',
                'user_id': 1
            }
        ]
        
        for proj_data in projects:
            project = Project(**proj_data)
            db.session.add(project)
        
        db.session.commit()
        
        # Create sample testing items
        testing_items = [
            {
                'title': 'Sensor Accuracy Test',
                'description': 'Testing the accuracy of temperature sensors under different conditions.',
                'code': 'sensor_data = read_sensor()\nreference_temp = get_reference()\naccuracy = abs(sensor_data - reference_temp)',
                'connections': 'Test sensor to ADC channel 0',
                'procedure': 'Step 1: Setup reference\nStep 2: Take measurements\nStep 3: Calculate accuracy',
                'user_id': 1
            }
        ]
        
        for test_data in testing_items:
            testing = Testing(**test_data)
            db.session.add(testing)
        
        db.session.commit()
        
        # Create sample comments and ratings
        project1 = Project.query.first()
        if project1:
            comment = ProjectComment(
                content='Great project! The code is well-documented and easy to follow.',
                user_id=2,  # test user
                project_id=project1.id
            )
            db.session.add(comment)
            
            rating = ProjectRating(
                rating=5,
                user_id=2,  # test user
                project_id=project1.id
            )
            db.session.add(rating)
        
        db.session.commit()
        
        print("Test data created successfully!")
        print("Admin user: harsha / admin123")
        print("Test user: testuser / test123")

if __name__ == '__main__':
    create_test_data()