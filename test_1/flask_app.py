from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/')
def index():
   return ('flask webservice - activity 3')


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
   elif (action == 'get_projectnames'):
       return get_projectnames(data)
   else:
       return no_implementation(data, action)


def get_projectnames(data):
   reply = {}
   reply["fulfillmentText"] = "The list of active projects are:"
   reply["fulfillmentMessages"] = []
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
