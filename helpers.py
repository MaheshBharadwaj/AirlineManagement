import pymongo as pym
from bson.objectid import ObjectId
client = pym.MongoClient(
    'mongodb+srv://dbadmin:mahesh123@cluster0.lijkf.mongodb.net/sample_airbnb?retryWrites=true&w=majority')


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

        print("Error: " + str(e))


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
        print('Exception: ' + str(e))


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
        flight_collection.insert_one(item)
        # print(item)
    except Exception as e:
        print("Error: " + str(e))


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
        print('Exception: ' + str(e))


def get_flights_by_route(source_city: str, dest_city: str):
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
        print('Exception: ' + str(e))


if __name__ == '__main__':
    print(get_all_routes())
