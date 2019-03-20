import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from flask import Flask, redirect, url_for, render_template, request, session
from flask_session import Session

engine = create_engine('postgresql://login:password123@localhost/postgres')
db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/", methods=['POST', 'GET'])
def index():
	flights = db.execute("SELECT * FROM flights").fetchall()
	olist = set()
	dlist = set()

	for flight in flights:
		olist.add(flight.origin)
		dlist.add(flight.destination)
	return render_template("index2.html", flights=flights, olist=olist, dlist=dlist)


@app.route("/searchform", methods=["POST"])
def searchform():
	ori = request.form.get("Origin")
	dest = request.form.get("Destination")
	date = request.form.get("Date1")
	seats = request.form.get("Seats")
	
	if db.execute("SELECT * FROM flights WHERE origin = :ori AND destination = :dest AND date1 = :date",{"ori": ori, "dest": dest, "date": date}).rowcount == 0:
		return render_template("error.html", message="Nope")
	else:
		searchres = db.execute("SELECT * FROM flights WHERE origin = :ori AND destination = :dest AND date1 = :date",{"ori": ori, "dest": dest, "date": date}).fetchall()
		return render_template("searchform.html", searchres=searchres)
		
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
	db.execute("INSERT INTO passengers (name, flight_id) VALUES (:name, :flight_id)", {"name": name, "flight_id": flight_id})
	db.commit()
	return render_template("success.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
	username = request.form.get("username")
	password = request.form.get("password")

	if request.method == 'POST':
		if db.execute("SELECT * FROM userdata WHERE login = :login AND password = :password", {"login": username, "password": password}).rowcount == 0:
			return render_template('error.html', message="Wrong Username or password")
		else:
			session['loginstatus'] = True
			session['username'] = username
			session['prava'] = db.execute("SELECT priveleges FROM userdata WHERE login = :login AND password = :password", {"login": username, "password": password}).fetchone()
			return index()	
    
@app.route("/logout")
def logout():
	session['loginstatus'] = False
	return index()


@app.route("/flightsinfo", methods=['POST'])
def info():
	flights = db.execute("SELECT * FROM flights").fetchall()
	return render_template('flightsinfo.html', flights=flights)

@app.route("/flightsinfo/<int:flight_id>")
def flightsinfo(flight_id):
	if session.get('loginstatus'):
		passengers = db.execute("SELECT * FROM passengers WHERE flight_id= :flight_id", {"flight_id": flight_id}).fetchall()
		return render_template("flightspass.html", passengers=passengers)
	else:
		return render_template("error.html", message="You need to login first")


