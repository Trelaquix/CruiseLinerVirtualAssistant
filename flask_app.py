from flask import Flask, request, jsonify
import sqlite3
from sqlite3 import Error
import random
import string
from datetime import datetime
import re

today_date = datetime.today().strftime('%Y-%m-%d')

app = Flask(__name__)

# set the location of the database file
DBFILENAME = "pythonsqlite.db"


@app.route('/')
def index():
    return ('flask webservice - activity 5')


@app.route('/webhook', methods=['POST'])
def webhook():
    # get the incoming JSON structure
    data = request.get_json(silent=True)
    # get the action name
    action = ""
    if 'action' in data['queryResult']:
        action = data['queryResult']['action']
    # conditional block to call relevant method for action
    if (action == 'test_connection'):
        return test_connection()
    elif (action == 'book_trip'):
        return book_trip()
    elif (action == 'get_all_ships'):
        return get_all_ships(data)
    elif (action == 'get_all_cruise'):
        return get_all_cruise(data)
    elif (action == 'get_ship_by_name'):
        return get_ship_by_name(data)
    elif (action == 'get_cruise_by_id'):
        return get_cruise_by_id(data)
    elif (action == 'create_booking'):
        return create_booking(data)
    elif (action == 'create_feedback'):
        return create_feedback(data)
    elif (action == 'cancel_booking'):
        return cancel_booking(data)
    elif (action == 'recommend_trip'):
        return recommend_trip(data)
    else:
        return no_implementation(data, action)


def create_connection(db_filename):
    try:
        conn = sqlite3.connect(db_filename)
        return conn
    except Error as e:
        print(e)
    return None


def book_trip():
    messages = []
    message = "🏴‍☠️ Yo-ho-ho I see you're eager to set sail but not so fast. To make a booking 🗓️, you need to fill in your details with the template provided:\n\n"
    messages.append({'text': {'text': [message]}})
    message = "Name:\n"
    message += "Phone:\n"
    message += "Email:\n"
    message += "Trip Id:\n"
    message += "Number of passengers:\n\n"
    messages.append({'text': {'text': [message]}})
    message = "1️⃣ To get the trip id, please view our available cruise by entering 'CRUISE'"
    message += "\n\n2️⃣ Then select a trip by entering the 'CRUISE ID'"
    messages.append({'text': {'text': [message]}})
    reply = {}
    reply["fulfillmentText"] = "Greetings from webhook"
    reply["fulfillmentMessages"] = messages
    return jsonify(reply)


def get_all_ships(data):
    messages = []
    try:
        conn = create_connection(DBFILENAME)
        cur = conn.cursor()
        cur.execute("SELECT ship_name, overview FROM ships")
        rows = cur.fetchall()
        if len(rows) == 0:
            message = "No projects found"
            messages.append({'text': {'text': [message]}})
        else:
            message = "Here are our available ships:\n\n"
            for row in rows:
                ship_name = row[0]
                ship_overview = row[1]
                message += "🚢 "+ship_name+"\n• "+ship_overview+"\n\n"
            message += "Want to get more information on a ship? Enter 'VIEW' followed by the ship name."
            message += "\n✅️ 'VIEW SPECTRUM'"
            message += "\n✅️ 'VIEW QUANTUM'"

            message += "\n\nOr enter 'CRUISE' to view our available cruises"
            message += "\n✅️ 'CRUISE'"
            messages.append({'text': {'text': [message]}})
        conn.close()
    except Error as e:
        print(e)

    reply = {}
    reply["fulfillmentText"] = ""
    reply["fulfillmentMessages"] = messages
    return jsonify(reply)


def get_all_cruise(data):
    messages = []
    try:
        conn = create_connection(DBFILENAME)
        cur = conn.cursor()
        sql = "SELECT c.id, c.cruise_name, c.number_of_nights, s.ship_name, MIN(t.interior_price) FROM cruise c, ships s, trips t WHERE c.ship_id = s.id AND c.id = t.cruise_id GROUP BY cruise_id"
        cur.execute(sql)
        rows = cur.fetchall()
        if len(rows) == 0:
            message = "No cruise found"
            messages.append({'text': {'text': [message]}})
        else:
            message = "Here is a list of our active cruises:\n\n"
            for row in rows:
                cruise_id = str(row[0])
                cruise_name = row[1]
                number_of_nights = str(row[2])
                ship_name = row[3]
                price = str(row[4])
                message += "🛳️ CRUISE ID: " + cruise_id + "\n " + cruise_name + "\n Ship name: " + \
                    ship_name + "\n No. of nights: " + number_of_nights + \
                    "\n Starting price: $" + price + "\n\n"
            message += "To find out more about the cruise and the available dates, just provide me the Cruise Id. "
            message += "\n✅(E.g. 'CRUISE ID 3')"
            message += "\n\nOr to find out more about the facilities on our ship, enter 'SHIPS'"
            message += "\n✅(E.g. 'SHIPS')"
            messages.append({'text': {'text': [message]}})
        conn.close()
    except Error as e:
        print(e)

    reply = {}
    reply["fulfillmentText"] = "The list of active cruises are:"
    reply["fulfillmentMessages"] = messages
    return jsonify(reply)


def get_ship_by_name(data):
    messages = []
    ship_name = data['queryResult']['parameters']['ship_name']
    try:
        conn = create_connection(DBFILENAME)
        cur = conn.cursor()

        sql = "SELECT * FROM ships WHERE ship_name LIKE '" + ship_name + "%'"
        cur.execute(sql)
        rows = cur.fetchall()

        if len(rows) == 0:
            message = "Apologies, I didn't get that. Can you rephrase your question?"
            messages.append({'text': {'text': [message]}})
        else:
            message = ""
            for row in rows:
                ship_name = row[1]
                ship_overview = row[2]
                ship_description = row[3]
                ship_attractions = row[4]
                message += "🚢 "+ship_name+"\n\n "+ship_description+"\n\n "+ship_attractions

            message += "\n\nWhat are you waiting for? Enter 'CRUISE' to view our available cruise trips now and book your next holiday🏖️!"
            messages.append({'text': {'text': [message]}})

        conn.close()
    except Error as e:
        print(e)

    reply = {}
    reply["fulfillmentText"] = " "
    reply["fulfillmentMessages"] = messages
    return jsonify(reply)


def get_cruise_by_id(data):
    messages = []
    # extract cruise_id from fulfillment request
    cruise_id = data['queryResult']['parameters']['cruise_id']
    try:
        conn = create_connection(DBFILENAME)
        cur = conn.cursor()

        cruise_id = str(cruise_id)
        cruise_name = ""
        # create select query to retrieve details
        sql = "SELECT c.cruise_name, c.number_of_nights, c.itinerary, s.ship_name, t.id, t.interior_price, t.outside_view_price, t.balcony_price, t.suites_price, t.start_date, t.end_date FROM ships s, cruise c, trips t WHERE s.id = c.ship_id AND t.cruise_id = c.id AND c.id = '" + cruise_id + "' GROUP BY start_date"
        cur.execute(sql)
        rows = cur.fetchall()

        # construct fulfillment messages
        if len(rows) == 0:
            message = "No details found for cruise " + \
                cruise_id + ". Please enter a valid Cruise Id."
            messages.append({'text': {'text': [message]}})
        else:
            message = "🛳️ Cruise Id: " + cruise_id
            for row in rows:
                # Checks if cruise_name is empty, if empty then execute code
                # This is to prevent the following data from being shown repeated
                if not cruise_name:
                    cruise_name = row[0]
                    number_of_nights = str(row[1])
                    itinerary = row[2]
                    ship_name = row[3]
                    message += "\nName: " + cruise_name
                    message += "\nShip:  " + ship_name
                    message += "\nNo. Of Nights: " + number_of_nights

                    message += "\n\nItinerary:\n\n"

                    if len(itinerary) > 4096:
                        itinerary_list = itinerary.split("split_here")
                        message += itinerary_list[0]
                        messages.append({'text': {'text': [message]}})
                        message = itinerary_list[1]
                    else:
                        message += itinerary

                    message += "\n\nHere are the available dates for the trip:\n\n"

                trip_id = str(row[4])
                interior_price = str(row[5])
                outside_view_price = str(row[6])
                balcony_price = str(row[7])
                suites_price = str(row[8])
                start_date = row[9]
                end_date = row[10]
                message += "🏖️ Trip Id: " + trip_id
                message += "\n🗓️ From: " + start_date + " to " + end_date
                message += "\n📌 Interior room: $" + interior_price
                message += "\n📌 Outside view: $" + outside_view_price
                message += "\n📌 Balcony: $" + balcony_price
                message += "\n📌 Suites: $" + suites_price+"\n\n"

            message += "Ready to book your next adventure?🔥 Simply fill up the template below:\n\n"
            messages.append({'text': {'text': [message]}})
            message = "Name:\n"
            message += "Phone:\n"
            message += "Email:\n"
            message += "Trip Id:\n"
            message += "Number of passengers:\n\n"
            messages.append({'text': {'text': [message]}})

        conn.close()
    except Error as e:
        print(e)

    reply = {}
    reply["fulfillmentText"] = " "
    reply["fulfillmentMessages"] = messages
    return jsonify(reply)


def recommend_trip(data):
    messages = []
    # extract cruise_id from fulfillment request
    trip_budget = data['queryResult']['parameters']['trip_budget']
    try:
        conn = create_connection(DBFILENAME)
        cur = conn.cursor()

        trip_budget = str(trip_budget)
        # create select query to retrieve details

        sql = "SELECT c.id, c.cruise_name, c.number_of_nights, s.ship_name, MIN(t.interior_price) FROM cruise c, ships s, trips t WHERE c.ship_id = s.id AND c.id = t.cruise_id AND t.interior_price < '" + str(trip_budget) + "' GROUP BY cruise_id"
        #sql = "SELECT c.cruise_id, c.cruise_name, c.number_of_nights, c.itinerary, s.ship_name, t.id, t.interior_price, t.start_date, t.end_date FROM ships s, cruise c, trips t WHERE s.id = c.ship_id AND t.cruise_id = c.id AND t.interior_price < '" + str(trip_budget) + "' GROUP BY start_date"
        cur.execute(sql)
        rows = cur.fetchall()

        # construct fulfillment messages
        if len(rows) == 0:
            message = "We are have no trips that meet your budget of $"+trip_budget+". Perhaps you could squeeze out some more from ye loot💰?"
            messages.append({'text': {'text': [message]}})
        else:
            message = "Here's where you can go on your budget:\n\n"
            for row in rows:
                cruise_id = str(row[0])
                cruise_name = row[1]
                number_of_nights = str(row[2])
                ship_name = row[3]
                price = str(row[4])
                message += "🛳️ CRUISE ID: " + cruise_id
                message += "\ncruise_name"+cruise_name
                message += "\n Ship name: "+ship_name
                message += "\n No. of nights: "+number_of_nights
                message += "\n Starting price: $" + price + "\n\n"

            message += "To find out more about the cruise and the available dates, just provide me the Cruise Id."
            message += "\n✅(E.g. 'CRUISE ID 3')"
            messages.append({'text': {'text': [message]}})
        conn.close()
    except Error as e:
        print(e)

    reply = {}
    reply["fulfillmentText"] = "The list of active cruises are:"
    reply["fulfillmentMessages"] = messages
    return jsonify(reply)


# check if trip id exists in table
def validate_trip_id(trip_id):
    conn = create_connection(DBFILENAME)
    cur = conn.cursor()
    sql = "SELECT * FROM trips WHERE id = '"+str(trip_id)+"'"
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    if len(rows) == 0:
        trip_id = None
    else:
        for row in rows:
            trip_id = str(row[0])

    return trip_id


# Function for validating an Email
def check_email(email_address):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email_address)):
        email_address = email_address

    else:
        email_address = None

    return email_address


# Function for validating a phone number
def check_phone(phone_number):
    regex = r'^[89][0-9]{7}$'
    if(re.fullmatch(regex, phone_number)):
        phone_number = phone_number

    else:
        phone_number = None

    return phone_number


def create_booking(data):
    messages = []
    passenger_name = data['queryResult']['parameters']['passenger_name']
    phone_number = data['queryResult']['parameters']['phone_number']
    email_address = data['queryResult']['parameters']['email_address']
    trip_id = data['queryResult']['parameters']['trip_id']
    number_of_passengers = data['queryResult']['parameters']['number_of_passengers']

    # check if phone number is valid
    phone_number = check_phone(phone_number)

    # check if email is valid
    email_address = check_email(email_address)

    # check if trip id exist in trip table
    trip_id = validate_trip_id(trip_id)

    if passenger_name is None:
        messages.append({'text': {'text': ["Please enter your name"]}})

    elif phone_number is None:
        messages.append({'text': {'text': ["Please provide a valid phone number"]}})

    elif email_address is None:
        messages.append({'text': {'text': ["Please provide a valid email address"]}})

    elif trip_id is None:
        messages.append({'text': {'text': ["Please provide a valid trip id"]}})

    elif type(number_of_passengers) is int:
        messages.append({'text': {'text': ["Please enter number of passengers"]}})

    else:
        # get random reference number of length 8 with letters and digits for security purposes
        generate_reference_number = ''.join(
            random.choice(string.digits) for i in range(12))
        reference_number = str(generate_reference_number)
        booking_date = today_date
        booking = (trip_id, passenger_name, phone_number, email_address,
                   number_of_passengers, booking_date, reference_number)
        try:
            conn = create_connection(DBFILENAME)
            cur = conn.cursor()
            sql = 'INSERT INTO bookings(trip_id,passenger_name,phone_number,email_address,number_of_passengers,booking_date,reference_number) VALUES(?,?,?,?,?,?,?)'
            cur.execute(sql, booking)
            conn.commit()
            conn.close()
        except Error as e:
            print(e)

        message = "🛳️🌊You're now ready to set sail! Here are your booking details:"
        message += "\n\nName: "+passenger_name
        message += "\nPhone: "+str(phone_number)
        message += "\nEmail: "+email_address
        message += "\nTrip Id: "+str(trip_id)
        message += "\nNumber of Passengers: "+number_of_passengers
        message += "\nReference number: "+reference_number
        message += "\n\n*Please keep your reference number as it is required for making cancellations, or leave us a feedback if you would like our customer service agent to contact you."

        message += "\n\nFor cancellations, enter 'CANCEL' followed by your reference number. To send a feedback, please provide the following details:"
        message += "\n\nReference number: "
        message += "\nFeedback: "

        message += "\n\nThank you for booking with Royal Caribbeans! We can't wait to have you onboard💯🔥!"
        messages.append({'text': {'text': [message]}})

    reply = {}
    reply["fulfillmentText"] = " "
    reply["fulfillmentMessages"] = messages
    return jsonify(reply)


# get booking id using reference number for deleting bookings and creating feedback
def get_booking_id(reference_number):
    conn = create_connection(DBFILENAME)
    cur = conn.cursor()
    sql = "SELECT id FROM bookings WHERE reference_number ='"+reference_number+"'"
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    if len(rows) == 0:
        booking_id = None
    else:
        for row in rows:
            booking_id = str(row[0])

    return booking_id


def create_feedback(data):
    messages = []
    reference_number = data['queryResult']['parameters']['reference_number']
    feedback_content = data['queryResult']['parameters']['feedback_content']
    feedback_date = today_date
    reference_number = str(reference_number)
    booking_id = get_booking_id(reference_number)
    feedback = (booking_id, feedback_date, feedback_content)
    if booking_id is not None:
        try:
            conn = create_connection(DBFILENAME)
            cur = conn.cursor()
            sql = "INSERT INTO feedback(booking_id,feedback_date,feedback_content) VALUES(?,?,?)"
            cur.execute(sql, feedback)
            conn.commit()
            conn.close()

        except Error as e:
            print(e)

        message = {"text": {"text": [
            "We have recieved your feedback for booking reference number "+reference_number+" and our crewmate will contact you shortly!"]}}
        messages.append(message)
    else:
        message = {"text": {"text": [
            "Please provide a valid reference number"]}}
        messages.append(message)

    reply = {}
    reply["fulfillmentText"] = " "
    reply["fulfillmentMessages"] = messages
    return jsonify(reply)


def cancel_booking(data):
    messages = []
    reference_number = data['queryResult']['parameters']['reference_number']
    reference_number = str(reference_number)
    booking_id = get_booking_id(reference_number)
    if booking_id is not None:
        booking_id = str(booking_id)
        try:
            conn = create_connection(DBFILENAME)
            cur = conn.cursor()
            sql = "DELETE FROM feedback WHERE booking_id = '" + booking_id + "'"
            cur.execute(sql)
            conn.commit()
            sql = "DELETE FROM bookings WHERE reference_number = '" + reference_number + "'"
            cur.execute(sql)
            conn.commit()
            conn.close()

            message = "Shiver Me Timbers‼️ Your booking with reference number " + \
                reference_number + " has been cancelled. We hope to have you onboard for our next adventure."
            messages.append({'text': {'text': [message]}})

        except Error as e:
            print(e)

    else:
        message = "There are no bookings found for reference number " + \
            str(reference_number)+". Please enter a valid reference number."
        messages.append({'text': {'text': [message]}})

    reply = {}
    reply["fulfillmentText"] = " "
    reply["fulfillmentMessages"] = messages
    return jsonify(reply)


def test_connection():
    reply = {}
    reply["fulfillmentText"] = "Greetings from webhook"
    reply["fulfillmentMessages"] = []
    return jsonify(reply)


def no_implementation(data, action):
    intent_name = data['queryResult']['intent']['displayName']
    fulfillment_text = " "
    if action == "":
        fulfillment_text = "No action name specified for intent " + intent_name
    else:
        fulfillment_text = "No implementation for action " + \
            action + " for intent " + intent_name

    reply = {}
    reply["fulfillmentText"] = fulfillment_text
    reply["fulfillmentMessages"] = []
    return jsonify(reply)


if __name__ == "__main__":
    app.run()
