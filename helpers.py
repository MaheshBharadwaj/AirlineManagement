import pymongo as pym
import datetime
from bson.objectid import ObjectId
client = pym.MongoClient(
    'mongodb+srv://dbadmin:mahesh123@cluster0.lijkf.mongodb.net/sample_airbnb?retryWrites=true&w=majority')


def add_user_to_mongo(email: str):
    global client
    try:
        db = client['users']
        collection = db['usersCollection']
        item = {
            'email': email,
            'bookings': []
        }
        collection.insert_one(item)
    except Exception as e:
        print('Exception in add user: ' + str(e))


def add_route_to_db(request):
    global client
    try:
        source_city = request.form.get('source_city')
        dest_city = request.form.get("dest_city")
        distance = request.form.get("distance")
        add_rev = request.form.get("checkbox_rev")
        db = client['route']
        collection = db['routeCollection']
        item = {'source_city': source_city,
                'dest_city': dest_city,
                'distance': distance}
        collection.insert_one(item)
        if add_rev == "add_rev":
            db = client['route']
            collection = db['routeCollection']
            item_rev = {'source_city': dest_city,
                        'dest_city': source_city,
                        'distance': distance}
            collection.insert_one(item_rev)
    except Exception as e:

        print("Error in add route to db: " + str(e))


def get_all_routes():
    global client
    try:
        db = client['route']
        collection = db['routeCollection']
        routes = [route for route in collection.find()]
        for route in routes:
            route['_id'] = str(route['_id'])
        return routes
    except Exception as e:
        print('Exception in get all routes: ' + str(e))


def add_flight_to_db(request):
    global client
    try:
        route_id = request.form.get('route')
        b_seats = request.form.get('b_seats')
        e_seats = request.form.get('e_seats')
        d_time = request.form.get('d_time')
        a_time = request.form.get('a_time')
        f_id = request.form.get('f_id')
        db = client['route']
        collection = db['routeCollection']
        route = collection.find_one({'_id': ObjectId(route_id)})
        distance = int(route.get("distance"))
        b_cost = distance * 5
        e_cost = distance * 2
        flight_db = client['flight']
        flight_collection = flight_db['flightCollection']
        item = {'route_id': ObjectId(route_id),
                'b_seats': b_seats,
                'b_cost': b_cost,
                'e_seats': e_seats,
                'e_cost': e_cost,
                'f_id': f_id,
                'd_time': d_time,
                'a_time': a_time
                }
        result = flight_collection.insert_one(item)

        ticket_db = client['ticket']
        ticket_collection = ticket_db['ticketCollection']
        item = {'flight_id': result.inserted_id, 'tickets_array': {}}
        ticket_collection.insert_one(item)
        # print(item)
    except Exception as e:
        print("Error in add flight to db: " + str(e))


def get_route(source_city: str, dest_city: str):
    global client
    try:
        db = client['route']
        collection = db['routeCollection']
        routes = [route for route in collection.find(
            {'source_city': source_city, 'dest_city': dest_city})]
        if len(routes) > 0:
            return routes[0]
        return None
    except Exception as e:
        print('Exception in get route: ' + str(e))


def get_flights_by_route(source_city: str, dest_city: str):
    global client
    route = get_route(source_city=source_city, dest_city=dest_city)
    if route is None:
        return
    try:
        flight_db = client['flight']
        collection = flight_db['flightCollection']
        flights = [flight for flight in collection.find(
            {'route_id': route.get('_id')})]
        for flight in flights:
            flight['route_id'] = str(flight['route_id'])
            flight['_id'] = str(flight['_id'])
        return flights

    except Exception as e:
        print('Exception in get flights by route: ' + str(e))


def get_flight_by_id(flight_id: str):
    global client
    try:
        db = client['flight']
        collection = db['flightCollection']
        # flights = [flight for flight in collection.find({})]
        flight = collection.find_one({'_id': ObjectId(flight_id)})
        flight['_id'] = str(flight['_id'])
        db = client['route']
        collection = db['routeCollection']
        route = collection.find_one({'_id': flight['route_id']})
        flight['route_id'] = str(flight['route_id'])
        flight['source_city'] = route['source_city']
        flight['dest_city'] = route['dest_city']
        return flight
    except Exception as e:
        print('Exception in get flight by id: ' + str(e))


def get_tickets_left(flight_id: str, date: str):
    global client
    try:
        db = client['ticket']
        collection = db['ticketCollection']
        flight_entry = collection.find_one({'flight_id': ObjectId(flight_id)})
        flight_ticket = flight_entry['tickets_array']
        tickets_left = flight_ticket.get(date)

        if tickets_left is None:
            db = client['flight']
            collection = db['flightCollection']
            # flights = [flight for flight in collection.find({})]
            flight = collection.find_one({'_id': ObjectId(flight_id)})
            return {'e_left': flight['e_seats'], 'b_left': flight['b_seats']}
        return tickets_left

    except Exception as e:
        print('Exception in get tickets left: ' + str(e))


def book_tickets(email: str, flight_id: str, b_count: int, e_count: int, date: str):
    global client
    try:
        ticket_db = client['ticket']
        ticket_collection = ticket_db['ticketCollection']
        flight_entry = ticket_collection.find_one(
            {'flight_id': ObjectId(flight_id)})
        flight_ticket = flight_entry['tickets_array']
        tickets_left = flight_ticket.get(date)

        if tickets_left is None:
            flight_db = client['flight']
            flight_collection = flight_db['flightCollection']
            flight = flight_collection.find_one({'_id': ObjectId(flight_id)})
            # flight['e_seats'] = str(int(flight['e_seats']) - e_count)
            # flight['b_seats'] = str(int(flight['b_seats']) - b_count)
            new_e_seats = str(int(flight['e_seats']) - e_count)
            new_b_seats = str(int(flight['b_seats']) - b_count)

            flight_ticket[
                date] = {'e_left': new_e_seats, 'b_left': new_b_seats}

            ticket_collection.update_one({'flight_id': ObjectId(flight_id)},
                                         {"$set": {"tickets_array": flight_ticket}})
        else:
            # print('E COUNT: ', e_count)
            # print("B COUNT: ", b_count)
            new_e_seats = str(int(tickets_left['e_left']) - e_count)
            new_b_seats = str(int(tickets_left['b_left']) - b_count)
            # print('New E: ', new_e_seats)
            # print('New B: ', new_b_seats)

            flight_ticket[date] = {
                'e_left': new_e_seats, 'b_left': new_b_seats}

            ticket_collection.update_one({'flight_id': ObjectId(flight_id)},
                                         {"$set": {"tickets_array": flight_ticket}})
        user_db = client['users']
        users_collection = user_db['usersCollection']
        today = datetime.date.today()
        today = today.strftime("%Y-%m-%d")
        booking = {
            'flight_id': flight_id,
            'e_count': e_count,
            'b_count': b_count,
            'date': date,
            'transactionDate': today}
        current_user_ob = users_collection.find_one({'email': email})
        new_booking = current_user_ob['bookings'] + [booking]
        users_collection.update_one(
            {'email': email}, {'$set': {'bookings': new_booking}})

    except Exception as e:
        print('Error in book tickets: ' + str(e))


if __name__ == '__main__':
    print(get_all_routes())
