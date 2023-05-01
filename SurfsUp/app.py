
# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
from datetime import date, timedelta



    #################################################
    # Database Setup
    #################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite", echo=False)
#################engine.execute("SELECT * From ").fetchall()
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save reference to the table
#Base.classes.keys()
Station = Base.classes.station
Measurement = Base.classes.measurement

# #################################################
# # Flask Setup
# #################################################
app = Flask(__name__)
# #################################################
# # Flask Routes
# #################################################


@app.route("/")
def welcome():
    # """List all available api routes."""
    print("Server Recieved request for Home Page")
    return (
        "You have reached the Station Measurement Home Page < br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"Please enter Start search in the format of yyyy-mm-dd for Searching<br/>"
        f"/api/v1.0/<start>/<br/>"
        f"Please enter Start/End search in the format of yyyy-mm-dd/yyyy-mm-dd for Searching<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server Recieved request for Precipitation")
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data)
    #  to a dictionary using date as the key and prcp as the value.
    one_year_from_recent = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    date_prcp = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date >= one_year_from_recent).all()
    prcp_list = []
    for date, prcp in date_prcp:
        date_prcp_dict = {}
        date_prcp_dict["date"] = date
        date_prcp_dict["prcp"] = prcp
        prcp_list.append(date_prcp_dict)
    session.close()
    return jsonify(prcp_list)
   

@app.route("/api/v1.0/stations")
def stations():
    print("Server Recieved request for Stations")
    session = Session(engine)
    all_stations = session.query(Station.station, Station.name).all()

    all_names = list(np.ravel(all_stations))
    session.close()
    return jsonify(all_names)


@app.route("/api/v1.0/tobs")
def tobs():
    print("Server Recieved request for tobs")
    session = Session(engine)
    station_counts = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).
                                               desc()).all()
    most_active = station_counts[0][0]

    one_year_from_recent = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temp_obs = session.query(Measurement.station, Measurement.tobs).\
        filter(Measurement.date >= one_year_from_recent).\
        filter(Measurement.station == most_active).all()
    temp_obs_list = list(np.ravel(temp_obs))
    session.close()
    return jsonify(temp_obs_list)


@app.route("/api/v1.0/<start>")
def start(start):
    print("Server Recieved request for Start- MIn, Avg, and Max")
    session = Session(engine)
    start_results = session.query(func.min(Measurement.tobs),
                                  func.avg(Measurement.tobs),
                                  func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()
    start_list = list(np.ravel(start_results))
    return jsonify (f"Start date:{start}", start_list)


@app.route("/api/v1.0/<start>/<end>")
def results(start, end):
    print("Server Recieved request for Start/End -MIn, Avg, and Max")
    session = Session(engine)
    results = session.query(func.max(Measurement.tobs),
                            func.min(Measurement.tobs),
                            func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start,
               Measurement.date <= end).all()
    session.close()
    results_list = []
    for res in results:
        tobs_dict = {}
        tobs_dict["max"] = res[0]
        tobs_dict["min"] = res[1]
        tobs_dict["avg"] = res[2]
        results_list.append(tobs_dict)

    return jsonify (f"Start date:{start}", f"End date:{end}", results_list)


if __name__ == "__main__":
    app.run(debug=True)
