import os
import psycopg2
from psycopg2.extras import execute_values
from pyowm import OWM
import googlemaps
from abc import ABC, abstractmethod
from flask import Flask, request, jsonify,render_template,send_from_directory
from datetime import datetime
from credentials import google_api,openweather_api,postgres_password

app = Flask(__name__)
gmaps = googlemaps.Client(key=google_api)

#class definition for WeatherData
class WeatherData(ABC):
    
    def __init__(self, location):
        self.location = location
#abstract method for child classes to implement
    @abstractmethod
    def output(self):
        pass
class Wind(WeatherData):
    def __init__(self, location, speed):
        super().__init__(location)
        self.speed = speed

    def output(self):
        return f"Wind speed: {self.speed} m/s"

class Humidity(WeatherData):
    def __init__(self, location, humidity):
        super().__init__(location)
        self.humidity = humidity

    def output(self):
        return f"Humidity: {self.humidity}%"

class Temperature(WeatherData):
    def __init__(self, location, temp):
        super().__init__(location)
        self.temp = temp

    def output(self):
        return f"Temperature: {self.temp}°C"
    
class Factory:
    def __init__(self):
        self.owm = OWM(openweather_api) 
        self.manager = self.owm.weather_manager()

    def createData(self, location, datatype):
        observation = self.manager.weather_at_place(location)
        weather = observation.weather

        if datatype == "wind":
            speed = weather.wind()["speed"]
            return Wind(location, speed)
        elif datatype == "humidity":
            humidity = weather.humidity
            return Humidity(location, humidity)
        elif datatype == "temperature":
            temp = weather.temperature(unit='celsius')["temp"]
            return Temperature(location, temp)


# PostgreSQL Database setup
def create_postgres_conn():
    conn = psycopg2.connect(
        dbname='gowithaplan',
        user=os.getenv("POSTGRES_USER", 'postgres'), # Default 'postgres' if not set
        host=os.getenv("POSTGRES_HOST",'itinerary.cd9zsk2sclln.ca-central-1.rds.amazonaws.com'), # Should be set in environment or hardcoded
        port=os.getenv("POSTGRES_PORT", '5432'), # Default value '5432' if not set
        password=os.getenv("POSTGRES_PASSWORD",postgres_password)
    )
    return conn

conn = create_postgres_conn()
cur = conn.cursor()


# Inserting and retrieving data from the database
# DMLs
def create_itinerary(user_id):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO itineraries (user_id) VALUES (%s) RETURNING id", (user_id,))
        itinerary_id = cur.fetchone()[0]
        conn.commit()
        return itinerary_id

def add_location_to_itinerary(itinerary_id, name, type, description, weather, distance,duration):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO locations (itinerary_id, name, type, description, weather, distance,duration) VALUES (%s, %s, %s, %s, %s, %s,%s)", 
                    (itinerary_id, name, type, description, weather, distance,duration))
        conn.commit()


def get_itinerary(user_id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM itineraries WHERE user_id=%s", (user_id,))
        itineraries = cur.fetchall()
        return itineraries

def get_locations_for_itinerary(itinerary_id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM locations WHERE itinerary_id=%s", (itinerary_id,))
        locations = cur.fetchall()
        return locations



def fetch_weather(location):
    factory = Factory()

    # Fetch different weather data types
    wind_data = factory.createData(location, "wind")
    humidity_data = factory.createData(location, "humidity")
    temperature_data = factory.createData(location, "temperature")

    # Format the weather data
    weather_info = f"{temperature_data.output()}, {humidity_data.output()}, {wind_data.output()}"
    return weather_info

def get_coordinates(address):
    #transfer an address to coordinates
    geocode_result = gmaps.geocode(address)

    if not geocode_result:
        return None

    location = geocode_result[0]['geometry']['location']
    return f"{location['lat']},{location['lng']}"



def fetch_distance(origin, destination):
    print(origin)
    print(destination)
    distance_result = gmaps.directions(origin,destination,mode="transit",alternatives=True)
    return distance_result[0]['legs'][0]['distance']['text'],distance_result[0]['legs'][0]['duration']['text']

#in current case, we assume the user is me and the user is logged in, this could be a variable when an auth service is developed
user_id = "001335114"


#Endpoints Definitions

#Default endpoint, rendering html template
@app.route('/')
def index():
    return render_template('index.html')

#add_location endpoint, used to store destination information to database
@app.route('/add_location', methods=['POST'])
def add_location():
    data = request.json
    itinerary_id = create_itinerary(data['user_id'])

    # Fetch weather and distance
    weather = fetch_weather(data['name'])
    user_location = data['user_location'] # "latitude,longitude" format
    print("User location received:", user_location)
    destination_coords = get_coordinates(data['name'])
    if destination_coords:
        distance, duration = fetch_distance(user_location, destination_coords)
    else:
        distance = "Coordinates not available"

    add_location_to_itinerary(itinerary_id, data['name'], data['type'], data['description'], weather, distance,duration)
    return jsonify({"status": "success"})

#get_ininerary endpoint, used to get all the stored ininerary without getting the detailed locations
@app.route('/get_itinerary', methods=['GET'])
def get_itinerary_route():
    user_id = request.args.get('user_id')
    itinerary = get_itinerary(user_id)
    return jsonify(itinerary)

#endpoint to get all information from the location table from the database
@app.route('/get_detailed_itinerary', methods=['GET'])
def get_detailed_itinerary():
    user_id = request.args.get('user_id')
    itinerary = get_itinerary(user_id)
    detailed_itinerary = []

    for itin in itinerary:
        locations = get_locations_for_itinerary(itin[0])
        for loc in locations:
            detailed_itinerary.append({
                'name': loc[2],  # Name
                'type': loc[3],  # Type
                'description': loc[4],  # Description
                'weather': loc[5],  # Weather
                'distance': loc[6],  # Distance
                'duration': loc[7]#duration
            })

    return jsonify(detailed_itinerary)


#running on 0.0.0.0:5000, preparing for future containerization accepting traffic from other ips
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)

# Close the connection when done
conn.close()