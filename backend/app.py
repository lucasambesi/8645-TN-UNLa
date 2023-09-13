from flask import Flask, request, Response
from flask_cors import CORS
from sqlalchemy import or_, and_
from datetime import datetime
import json
import logging
import jwt

from database import db_session, Clients, Flights, ClientsFlight, Airports
from config import get_env_vars
from mappers import *


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


# @app.before_request
def check_authentication():
    try:
        if request.path not in get_env_vars("PUBLIC_ROUTES"):
            if request.headers.get('Authorization') is None:
                return Response(json.dumps({"error": 'Missing authorization token'}), status=401, mimetype='application/json')

            access_token = request.headers.get('Authorization')
            jwt.decode(access_token.split(" ")[1], get_env_vars("JWT_PUBLIC_KEY"), options={
                       "verify_signature": True}, algorithms=["RS256"])
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=401, mimetype='application/json')


@app.route("/signin", methods=["POST"])
def signin():
    try:
        response = None

        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = Clients.query.filter(
            and_(Clients.email == email, Clients.password == password)).first()

        if (existing_user):
            response = Response(json.dumps(
                {"user": client_mapper(existing_user)}), status=200, mimetype='application/json')
            # access_token = jwt.encode({
            #     "exp": int(time.time()+3600),
            #     "email": existing_user.email
            # }, get_env_vars("JWT_PRIVATE_KEY"), algorithm='RS256')

            # response = Response(json.dumps(
            #     {"access_token": access_token, "type": "Bearer"}), status=200, mimetype='application/json')
        else:
            response = Response('Invalid credentials or non-existent client',
                                status=401, mimetype='application/json')

        return response

    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')


@app.route("/signup", methods=["POST"])
def signup():
    try:
        response = None

        password = request.form.get("password")
        name = request.form.get("name")
        email = request.form.get("email")
        document = int(request.form.get("document"))
        phone = request.form.get("phone")
        address = request.form.get("address")
        city = request.form.get("city")
        birthday = datetime.strptime(request.form.get("birthday"), '%d/%m/%Y')
        sex = request.form.get("sex")

        existing_client = Clients.query.filter(
            or_(Clients.document == document, Clients.email == email)).first()

        if (existing_client):
            response = Response('Client with document {} already exists'.format(
                document), status=409, mimetype='application/json')
        else:
            client = Clients(name=name, email=email, document=document, phone=phone,
                             address=address, city=city, birthday=birthday, sex=sex, password=password)

            db_session.add(client)
            db_session.commit()

            client_registered = Clients.query.filter_by(
                document=document).first()

            response = Response('Client with email {} created successfully'.format(
                client_registered.document), status=201, mimetype='application/json')

        return response

    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')


@app.route("/client/<id>", methods=["GET"])
def get_client(id):
    try:
        response = None
        client_data = Clients.query.get(id)
        if client_data is None:
            response = Response('Client with id {} does not exist'.format(
                id), status=404, mimetype='application/json')
        else:
            response = Response(json.dumps(client_mapper(
                client_data)), status=200, mimetype='application/json')
        return response
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')


@app.route("/client/<id>", methods=["PUT"])
def update_client(id):
    try:
        response = None
        name = request.form.get("name")
        email = request.form.get("email")
        document = int(request.form.get("document"))
        phone = int(request.form.get("phone"))
        address = request.form.get("address")
        city = request.form.get("city")
        birthday = datetime.strptime(request.form.get("birthday"), '%d/%m/%Y')
        sex = request.form.get("sex")

        client_data = Clients.query.get(id)
        if client_data is None:
            response = Response('Client with id {} does not exist'.format(
                id), status=200, mimetype='application/json')
        else:
            Clients.query.filter_by(id=id).update(dict(
                name=name, email=email, document=document, phone=phone, address=address, city=city, birthday=birthday, sex=sex))
            db_session.commit()
            response = Response('Client with id {} updated successfully'.format(
                id), status=200, mimetype='application/json')

        return response

    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')


@app.route("/client/<id>", methods=["DELETE"])
def delete_client(id):
    try:
        response = None
        client_data = Clients.query.get(id)
        if client_data is None:
            response = Response('Client with id {} does not exist'.format(
                id), status=200, mimetype='application/json')
        else:
            db_session.delete(client_data)
            db_session.commit()
            response = Response('Client with id {} deleted successfully'.format(
                id), status=200, mimetype='application/json')

        return response

    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')


@app.route("/clients", methods=["GET"])
def get_clients():
    try:
        clients = Clients.query.all()
        response = []
        for client in clients:
            response.append(client_mapper(client))
        return Response(json.dumps(response), status=200, mimetype='application/json')

    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')


@app.route("/flight/<id>", methods=["GET"])
def get_flight(id):
    try:
        response = None
        flight_data = Flights.query.get(id)
        if flight_data is None:
            response = Response('Flight with id {} does not exist'.format(
                id), status=404, mimetype='application/json')
        else:
            response = Response(json.dumps(flight_mapper(
                flight_data)), status=200, mimetype='application/json')
        return response
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')


@app.route("/flights", methods=["GET"])
def get_flights():
    try:
        filters = set()

        if request.args.get("from") and request.args.get("to"):
            date_from = datetime.strptime(request.args.get("from"), '%d/%m/%Y')
            date_to = datetime.strptime(request.args.get("to"), '%d/%m/%Y')
            filters.add(Flights.departure_datetime.between(date_from, date_to))

        elif request.args.get("from"):
            date_from = datetime.strptime(request.args.get("from"), '%d/%m/%Y')
            date_to = datetime.strptime("12/12/2999", '%d/%m/%Y')
            filters.add(Flights.departure_datetime.between(date_from, date_to))

        elif request.args.get("to"):
            date_to = datetime.strptime(request.args.get("to"), '%d/%m/%Y')
            now = datetime.now()
            filters.add(Flights.departure_datetime.between(now, date_to))

        if request.args.get("origin"):
            origin = request.args.get("origin")
            filters.add(Flights.origin == origin)

        if request.args.get("destination"):
            destination = request.args.get("destination")
            filters.add(Flights.destination == destination)

        if request.args.get("price_min") and request.args.get("price_max"):
            price_min = float(request.args.get("price_min"))
            price_max = float(request.args.get("price_max"))
            filters.add(Flights.price.between(price_min, price_max))

        elif request.args.get("price_min"):
            price_min = float(request.args.get("price_min"))
            filters.add(Flights.price.between(price_min, float(9999999999)))

        elif request.args.get("price_max"):
            price_max = float(request.args.get("price_max"))
            filters.add(Flights.price.between(float(0), price_max))

        if request.args.get("max_flight_time"):
            max_flight_time = datetime.time(
                request.args.get("max_flight_time"))
            filters.add(Flights.flight_time <= max_flight_time)

        flights = Flights.query.filter(*filters).all()

        response = []
        for flight in flights:
            origin_airport_data = Airports.query.get(flight.origin)
            destination_airport_data = Airports.query.get(flight.destination)

            response.append(flight_mapper(
                flight, origin_airport_data, destination_airport_data))
        return Response(json.dumps(response), status=200, mimetype='application/json')

    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')


@app.route("/book-flight", methods=["GET"])
def get_flight_book():
    try:
        response = None
        client_id = request.form.get("client_id")
        flight_id = request.form.get("flight_id")
        seat = request.form.get("seat")

        client = Clients.query.filter_by(id=client_id).first()
        flight = Flights.query.filter_by(id=flight_id).first()

        if client is None:
            response = Response("Client with id {} does not exist".format(
                client_id), status=404, mimetype='application/json')
        elif flight is None:
            response = Response("Flight with id {} does not exist".format(
                client_id), status=404, mimetype='application/json')
        else:
            clients_flight = ClientsFlight(
                client_id=client_id, flight_id=flight_id, seat=seat)

            db_session.add(clients_flight)
            db_session.commit()
            response = Response("Flight {} was booked by client with document {} successfully".format(
                flight.id, client.document), status=201, mimetype='application/json')
        return response

    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')


@app.route("/airports", methods=["GET"])
def get_airports():
    try:
        airports = Airports.query.all()
        response = []
        for airport in airports:
            response.append(airport_mapper(airport))
        return Response(json.dumps(response), status=200, mimetype='application/json')

    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')


@app.route("/airport/<id>", methods=["GET"])
def get_airport(id):
    try:
        response = None
        airport_data = Airports.query.get(id)
        if airport_data is None:
            response = Response('Airport with id {} does not exist'.format(
                id), status=404, mimetype='application/json')
        else:
            response = Response(json.dumps(airport_mapper(
                airport_data)), status=200, mimetype='application/json')
        return response
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')


@app.teardown_appcontext
def shutdown_session(Error=None):
    db_session.remove()


if __name__ == '__main__':
    logging.basicConfig()
    app.run(debug=True)
