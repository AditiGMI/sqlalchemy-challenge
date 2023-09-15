# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    # 1. List all avl routes
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/prcp<br/>"
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/tobs/start<br/>"
        f"/api/v1.0/tobs/start/end"
    )

# 2. convert the query result from 12 months of precipitation data to dic.
@app.route("/api/v1.0/prcp")
def precipitation():

    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    prcp_results = session.query(measurement.date,measurement.prcp).\
        filter(measurement.date >= query_date).all()
    session.close()

    # Convert list of tuples into normal list
    precipitation_data = list(np.ravel(prcp_results))

    # return JSON list of data
    return jsonify(precipitation_data)

# 3. return JSON list of stations from Dataset
@app.route("/api/v1.0/station")
def stations():
    
    """Return a list of stations"""
    station_list = session.query(station.name).all()
    session.close()

    # Convert list of tuples into normal list
    station_names = list(np.ravel(station_list))

    return jsonify(station_names)

# 4. return JSON query to find the most active stations (i.e. which stations have the most rows?) dates & temp
@app.route("/api/v1.0/tobs")
def temprature():
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temprature_list = session.query(measurement.date, measurement.tobs).\
    filter(measurement.station == 'USC00519281').\
    filter(measurement.date >= query_date).all()
    session.close()

    temprature_data = list(np.ravel(temprature_list))
    return jsonify(temprature_data) 
    
#5 return JSON list of min max & avg temp. from start to end date
@app.route("/api/v1.0/tobs/<start>")
@app.route("/api/v1.0/tobs/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    # Select statement
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel).\
            filter(measurement.date >= start).all()

        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    results = session.query(*sel).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run(debug=True)
