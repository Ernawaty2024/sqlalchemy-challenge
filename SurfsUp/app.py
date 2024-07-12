# Import the dependencies.
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd
import datetime as dt
# Import Flask
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
Station = Base.classes.station
Measurement= Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

# Create an app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# API STATIC ROUTES

# 1. Home Route
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:</br>"
        f"/api/v1.0/precipitation</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/<start></br>"
        f"/api/v1.0/<start>/<end></br>"
    )

# 2. Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Calculate date 1 year ago from the last data point in the database
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=365)
    
    # Query precipitation data for the last 1 year
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    
    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(precipitation_dict)

# 3. Stations Route
@app.route("/api/v1.0/stations")
def stations():
  
    # Query all stations
    stations_result = session.query(Station.station).all()

    # Convert list of tuples into normal list
    stations_list= [station[0] for station in stations_result]

    return jsonify(stations_list)
         
# 4. Tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date 1 year ago from the last data point in the database
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=365)
    
    # Query most active stations
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    # Query temperature observations for the last year from the most active station
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.station == most_active_station,
        Measurement.date >= one_year_ago).all()
    
    # Convert the query results to a list of dictionaries
    tobs_list = [{"date": date, "tobs":tobs} for date, tobs in tobs_data]
    
    return jsonify(tobs_list)

# API DYNAMIC ROUTE
# 1. Start Route
@app.route("/api/v1.0/<start>")
def start(start):
   
    # Query min, avg, max temperatures from the start date to the end of the dataset
    Temperature_stats = session.query(
        func.min(Measurement.tobs).label('min_temp'),
        func.avg(Measurement.tobs).label('avg_temp'),
        func.max(Measurement.tobs).label('max_temp'),
    ).filter(Measurement.date >= start).all()

    # Convert the query results to a dictionary
    Temperature_stats_dict = {
        "TMIN": Temperature_stats[0][0],
        "TAVG": Temperature_stats[0][1],
        "TMAX": Temperature_stats[0][2] 
    }

    return jsonify(Temperature_stats_dict)

# 2. Start and End Route
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    Temp_stats = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert the query results to a dictionary
    Temp_stats_dict = {
        "TMIN" : Temp_stats[0][0],
        "TAVG" : Temp_stats[0][1],
        "TMAX" : Temp_stats[0][2]    
    }

    return jsonify(Temp_stats_dict)

# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)
