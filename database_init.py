import os
import psycopg2
from psycopg2.extras import execute_values
from pyowm import OWM
import googlemaps
from abc import ABC, abstractmethod
from flask import Flask, request, jsonify,render_template,send_from_directory


# PostgreSQL Database setup
def create_database():
    conn = psycopg2.connect(
        dbname='postgres',  # connect to the default 'postgres' database
        user=os.getenv("POSTGRES_USER", 'postgres'), 
        host=os.getenv("POSTGRES_HOST", 'itinerary.cd9zsk2sclln.ca-central-1.rds.amazonaws.com'),
        port=os.getenv("POSTGRES_PORT", '5432'),
        password=os.getenv("POSTGRES_PASSWORD", 'Yucong1!')
    )
    conn.autocommit = True  
    cur = conn.cursor()

#Create a database called gowithaplan
    try:
        cur.execute("CREATE DATABASE gowithaplan;")
        print("Database gowithaplan created successfully.")
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

create_database()


#Estabilish connection to the newly created database
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

# Create tables

# Create the tables needed for our application
# DDLs
cur.execute('''
CREATE TABLE IF NOT EXISTS itineraries (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    itinerary_id INTEGER,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT NOT NULL,
    weather TEXT,
    distance TEXT,
    duration TEXT,
    FOREIGN KEY(itinerary_id) REFERENCES itineraries(id)
)
''')

conn.commit()
cur.close()



