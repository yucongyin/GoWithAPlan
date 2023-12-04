import os
import psycopg2
from psycopg2.extras import execute_values
from pyowm import OWM
import googlemaps
from abc import ABC, abstractmethod
from flask import Flask, request, jsonify,render_template,send_from_directory


#a python file I used to delete all the records and do tests
def create_postgres_conn():
    conn = psycopg2.connect(
        dbname='gowithaplan',  
        user=os.getenv("POSTGRES_USER", 'postgres'),
        host=os.getenv("POSTGRES_HOST", 'itinerary.cd9zsk2sclln.ca-central-1.rds.amazonaws.com'),
        port=os.getenv("POSTGRES_PORT", '5432'),
        password=os.getenv("POSTGRES_PASSWORD", 'Yucong1!')
    )
    return conn


conn = create_postgres_conn()
cur = conn.cursor()


cur.execute('''
DELETE FROM locations;
DELETE FROM itineraries;            
''')


conn.commit()
cur.close()
