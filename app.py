# import Flask etc.
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt


######## Set up engine and connect to DB

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)


######## Set up Flask 
app = Flask(__name__)


## Homepage
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start_date><br/>"
        f"/api/v1.0/<start_date>/<end_date><br/>"
        
    )


## Precipitation
@app.route("/api/v1.0/precipitation")

def precipitation_raw():
    prcp_raw = session.query(Measurement.station,Measurement.date,Measurement.prcp).all()
    all_prcp_raw = []
    
    for station,date,prcp in prcp_raw:
        row={}
        row["station"]=station
        row["date"]=date
        row["prcp"]=prcp
        all_prcp_raw.append(row)
        
    return jsonify(all_prcp_raw)


## Stations
@app.route("/api/v1.0/stations")

def station_raw():
    station_raw = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    all_station=[]
    
    for station,name,lat,lng,elev in station_raw:
        row={}
        row["station"]=station
        row["name"]=name
        row["lat"]=lat
        row["lng"]=lng
        row["elev"]=elev
        all_station.append(row)
        
    return jsonify(all_station)

### Temperature
# * `/api/v1.0/tobs`
#   * query for the dates and temperature observations from a year from the last data point.
#   * Return a JSON list of Temperature Observations (tobs) for the previous year.

@app.route("/api/v1.0/tobs")

def tobs():
    last_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_yr=int(last_date[0:4])
    last_mn=int(last_date[6:7])
    last_dy=int(last_date[8:10])
    start_date=dt.date(last_yr,last_mn,last_dy)-dt.timedelta(days=365)
    
    lst_yr_tobs_raw=session.query(Measurement.station,Measurement.date,Measurement.tobs).filter(Measurement.date>start_date).all()
    lst_yr_tobs=[]
    
    for station,date,tob in lst_yr_tobs_raw:
        row={}
        row["station"]=station
        row["date"]=date
        row["temperature"]=tob
        lst_yr_tobs.append(row)
        
    return jsonify(lst_yr_tobs)


# * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
#   * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#   * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
#   * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start_date>")

def calc_temps(start_date):
    if(start_date):
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()[0]
         
    else:
        return "please enter a start date in the yyyy-mm-dd format"

    

# Ending part
if __name__ == '__main__':
    app.run(debug=True)