import pymongo as pym
import datetime
from bson.objectid import ObjectId
from pymongo import message
from pymongo import collection
from werkzeug.datastructures import cache_property
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
        result = collection.insert_one(item)
        msg_db = client['msg']
        msg_collection = msg_db['msgCollection']
        msg_item = {
            'user_id': str(result.inserted_id),
            'messages_array': []
        }
        msg_collection.insert_one(msg_item)

    except Exception as e:
        print('Exception in add user: ' + str(e))


def request_cancel(flight_id: str, date: datetime, email: str):
    global client
    try:

        user_db = client['users']
        user_collection = user_db['usersCollection']
        usr = user_collection.find_one({'email': email})
        cancel_db = client['cancels']

        collection = cancel_db['cancelsCollection']

        for each in usr['bookings']:
            if(each['flight_id'] == flight_id and each['date'] == date):

                item = {
                    'user_id': usr['_id'],
                    'flight_id': flight_id,
                    'e_count': each['e_count'],
                    'b_count': each['b_count'],
                    'date': date
                }

                d = datetime.date.today()

                x = int(date[len(date)-2:])
                month = int(date[len(date)-5:len(date)-3])
                if(x - d.day < 2 and month == d.month):
                    return -2
                if(d.month != month and x >= 30 and d.day <= 2):
                    return -2

                if(collection.find(item).count() != 0):

                    return -1

                result = collection.insert_one(item)
                print('inserted into db', collection.find_one(
                    {'flight_id': flight_id}))

                return 1

    except Exception as e:
        print('Exception in requesting cancel: ' + str(e))


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


def get_route_from_flight_id(flight_id: str):
    global client
    route = []
    route_id = "temp"

    try:
        route_db = client['route']
        route_collection = route_db['routeCollection']
        flight_db = client['flight']
        collection = flight_db['flightCollection']
        for each in collection.find():
            if(str(each['_id']) == flight_id):
                route_id = each['route_id']
        for each in route_collection:
            if(str(each['_id']) == route_id):
                route.append(each['source_city'])
                route.append(each['dest_city'])
        print('route: ', route)
        return route
    except Exception as e:
        print('Exception in get route by flight id: ' + str(e))


def get_all_flights_by_id():
    global client
    flights = []
    try:
        flights = []
        user_db = client['users']
        user_collection = user_db['usersCollection']
        for usr in user_collection.find():
            for each in usr['bookings']:
                flight = get_flight_by_id(each['flight_id'])
                # print('flight id: ',each['flight_id'])
                flight['user'] = usr['email']
                flight['e_seats'] = each['e_count']
                flight['b_seats'] = each['b_count']
                flight['date'] = each['date']
                flight['tdate'] = each['transactionDate']
                flight['admin'] = True
                # print(flight)
                flights.append(flight)

        return flights
    except Exception as e:
        print('Exception in getting user tickets: ' + str(e))


def get_user_bookings(email: str):
    global client
    try:
        flights = []
        user_db = client['users']
        user_collection = user_db['usersCollection']
        usr = user_collection.find_one({'email': email})
        for each in usr['bookings']:
            flight = get_flight_by_id(each['flight_id'])
            # print('flight id: ',each['flight_id'])
            flight['user'] = usr['email']
            flight['e_seats'] = each['e_count']
            flight['b_seats'] = each['b_count']
            flight['date'] = each['date']
            flight['tdate'] = each['transactionDate']

            flights.append(flight)

        return flights
    except Exception as e:
        print('Exception in getting user tickets: ' + str(e))


def get_all_flights_by_route():
    global client
    flights = []
    try:
        route_db = client['route']
        route_collection = route_db['routeCollection']
        flight_db = client['flight']
        collection = flight_db['flightCollection']

        for each in route_collection.find():
            flights.extend(flight for flight in collection.find(
                {'route_id': ObjectId(each['_id'])}))

        # print(flights)
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


def delete_flight(flight_id: str):
    global client
    try:
        flight_db = client['flight']
        flight_collection = flight_db['flightCollection']
        db = client['ticket']
        collection = db['ticketCollection']

        flight = flight_collection.find_one({'_id': ObjectId(flight_id)})

        flight_collection.delete_many({'_id': ObjectId(flight_id)})
        x = collection.delete_many({'flight_id': ObjectId(flight_id)})
        # print(x.deleted_count)

        user_db = client['users']
        user_collection = user_db['usersCollection']

        for user in user_collection.find():
            to_update = False
            new_booking = []
            for booking in user['bookings']:
                if booking['flight_id'] == flight_id:
                    to_update = True
                    continue
                else:
                    new_booking.append(booking)
            if to_update:
                user_collection.update_one({'_id': user['_id']}, {
                                           '$set': {'bookings': new_booking}})

                msg_db = client['msg']
                msg_collection = msg_db['msgCollection']
                msg = "Flight ID: " + \
                    str(flight['f_id']) + " has been cancelled due to unforceen circumstances! The amount will be refunded within 5 business days. Sorry for inconvineance cause"
                msg_item = {'user_id': str(
                    user['_id']), 'message': msg, 'timestamp': str(datetime.date.today())}

                msg_ob = msg_collection.find_one({'user_id': str(user['_id'])})
                current_msg_array = msg_ob['messages_array']
                current_msg_array.append(msg_item)
                msg_collection.update_one({'user_id': str(user['_id'])}, {
                                          '$set': {'messages_array': current_msg_array}})

        return True
    except Exception as e:
        print('Error in deleting flight: ' + str(e))


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


def get_messages(email: str):
    global client
    try:
        db = client['users']
        collection = db['usersCollection']

        user_ob = collection.find_one({'email': email})
        user_id = str(user_ob['_id'])
        msg_db = client['msg']
        msg_collection = msg_db['msgCollection']
        messages = msg_collection.find_one({'user_id': user_id})
        return messages['messages_array']
    except Exception as e:
        print('Exception in get messages: ' + str(e))


def get_all_cancellations():
    global client
    try:
        cancel_db = client['cancels']
        cancel_collection = cancel_db['cancelsCollection']
        cancellations_array = [
            cancellation for cancellation in cancel_collection.find()]

        if (len(cancellations_array) == 0):
            return []

        user_db = client['users']
        users_collection = user_db['usersCollection']

        flight_db = client['flight']
        flight_collection = flight_db['flightCollection']

        route_db = client['route']
        route_collection = route_db['routeCollection']

        for cancellation in cancellations_array:
            cancellation['_id'] = str(cancellation['_id'])
            user = users_collection.find_one({'_id': cancellation['user_id']})
            cancellation['email'] = user['email']
            cancellation['user_id'] = str(cancellation['user_id'])

            flight = flight_collection.find_one(
                {'_id': ObjectId(cancellation['flight_id'])})
            cancellation['a_time'] = flight['a_time']
            cancellation['d_time'] = flight['d_time']

            route = route_collection.find_one({'_id': flight['route_id']})

            cancellation['source_city'] = route['source_city']
            cancellation['dest_city'] = route['dest_city']

        return cancellations_array
    except Exception as e:
        print('Exception in get all cancellations: ' + str(e))


def handle_cancellation(status: str, c_id: str):
    global client
    try:
        cancel_db = client['cancels']
        cancel_collection = cancel_db['cancelsCollection']
        cancellation = cancel_collection.find_one({'_id': ObjectId(c_id)})

        user_db = client['users']
        users_collection = user_db['usersCollection']

        ticket_db = client['ticket']
        ticket_collection = ticket_db['ticketCollection']

        msg_db = client['msg']
        msg_collection = msg_db['msgCollection']

        cancellation['_id'] = str(cancellation['_id'])

        cancel_collection.delete_one({'_id': ObjectId(c_id)})
        if status == 'reject':
            msg_ob = msg_collection.find_one(
                {'user_id': str(cancellation['user_id'])})

            message_array = msg_ob['messages_array']

            msg_item = {'user_id': str(
                cancellation['user_id']), 'message': 'Your request for cancellation has been DENIED! Contact support for further information', 'timestamp': str(datetime.date.today())}

            message_array.append(msg_item)
            msg_collection.update_one({'user_id': str(cancellation['user_id'])}, {
                                      '$set': {'messages_array': message_array}})
        else:
            msg_ob = msg_collection.find_one(
                {'user_id': str(cancellation['user_id'])})

            message_array = msg_ob['messages_array']

            msg_item = {'user_id': str(
                cancellation['user_id']), 'message': 'Your request for cancellation has been APPROVED! The amount will be refunded in 5 business days', 'timestamp': str(datetime.date.today())}

            message_array.append(msg_item)
            msg_collection.update_one({'user_id': str(cancellation['user_id'])}, {
                '$set': {'messages_array': message_array}})

            user = users_collection.find_one({'_id': cancellation['user_id']})
            bookings_array = user['bookings']
            new_bookings_array = []
            to_update = False
            for booking in bookings_array:
                if booking['flight_id'] == cancellation['flight_id'] and booking['date'] == cancellation['date']:
                    to_update = True
                    continue
                new_bookings_array.append(booking)

            if to_update:
                users_collection.update_one({'_id': cancellation['user_id']}, {
                    '$set': {'bookings': new_bookings_array}})

            ticket_ob = ticket_collection.find_one(
                {'flight_id': ObjectId(cancellation['flight_id'])})
            tickets_array = ticket_ob['tickets_array']
            tickets_array[cancellation['date']]['e_left'] = str(
                int(cancellation['e_count']) + int(tickets_array[cancellation['date']]['e_left']))
            tickets_array[cancellation['date']]['b_left'] = str(
                int(cancellation['b_count']) + int(tickets_array[cancellation['date']]['b_left']))

            ticket_collection.update_one({'flight_id': ObjectId(cancellation['flight_id'])}, {
                                         '$set': {'tickets_array': tickets_array}})

    except Exception as e:
        print('Exception in get all cancellations: ' + str(e))


if __name__ == '__main__':
    print(get_all_routes())
