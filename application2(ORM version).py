import os

from models import *

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import scoped_session, sessionmaker

from flask import Flask, redirect, url_for,  render_template, request, session, jsonify
from flask_session import Session



app = Flask(__name__)
app.secret_key = "super secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://login:password@localhost/postgres'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)



@app.route("/", methods=['POST', 'GET'])
def index():
	flights = Flight.query.all()
	olist = set()
	dlist = set()

	for flight in flights:
		olist.add(flight.origin)
		dlist.add(flight.destination)
		
	if not session.get('loginstatus'):	
		return render_template("index2.html", flights=flights, olist=olist, dlist=dlist)
	else:
		return render_template("index2.html", flights=flights, olist=olist, dlist=dlist)

@app.route("/searchform", methods=["POST"])
def searchform():
	ori = request.form.get("Origin")
	dest = request.form.get("Destination")
	date = request.form.get("Date1")
	seats = request.form.get("Seats")
	
	flight = Flight.query.filter(and_(Flight.origin == ori, Flight.destination == dest, Flight.date1 == date)).all()
	if flight :
		searchres = flight 
		return render_template("searchform.html", searchres=searchres)
	else:
		return render_template("error.html", message="Nope")
		
@app.route("/flights/<int:flight_id>")
def book(flight_id):
	session['flight_id'] = flight_id
	return render_template("bookflight.html")

@app.route("/success", methods=["POST"])
def success():
	name = request.form.get("Name")
	flight_id = session.get('flight_id')
	
	if name is None:
		return render_template("error.html", message="Enter your name please")
	
	flight = Flight.query.get(flight_id)
	flight.add_passenger(name)
	return render_template("success.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
	username = request.form.get("username")
	password = request.form.get("password")

	if request.method == 'POST':
		if not UserData.query.filter(and_(UserData.login == username, UserData.password == password)).first():
		
			return render_template('error.html', message="Wrong Username or password")
		else:
			user = UserData.query.filter(and_(UserData.login == username, UserData.password == password)).first()
			session['loginstatus'] = True
			session['username'] = username
			session['prava'] = user.priveleges
			return index()	
    
@app.route("/logout")
def logout():
	session['loginstatus'] = False
	return index()


@app.route("/flightsinfo", methods=['POST'])
def info():
	flights = Flight.query.all()
	return render_template('flightsinfo.html', flights=flights)

@app.route("/flightsinfo/<int:flight_id>")
def flightsinfo(flight_id):
	if session.get('loginstatus'):
		passengers = Passenger.query.filter_by(flight_id=flight_id)
		return render_template("flightspass.html", passengers=passengers)
	else:
		return render_template("error.html", message="You need to login first")

@app.route("/api/flights/<int:flight_id>")
def flight_api(flight_id):

    flight = Flight.query.get(flight_id)
    if flight is None:
        return jsonify({"error": "Invalid flight_id"}), 422

    passengers = flight.passengers
    names = []
    for passenger in passengers:
        names.append(passenger.name)
    return jsonify({
            "origin": flight.origin,
            "destination": flight.destination,
            "date": flight.date1,
            "passengers": names
        })

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    sess.init_app(app)

    app.debug = True
    app.run()
