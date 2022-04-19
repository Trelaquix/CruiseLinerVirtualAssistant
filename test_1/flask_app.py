from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/')
def index():
   return ('flask webservice - activity 2')


@app.route('/webhook', methods=['POST'])
def webhook():
   # get the incoming JSON structure
   data = request.get_json(silent=True)
   # data is a dictionary
   # data = request.get_json(silent=True)
  
   # get the dictionary value for queryResult
   # queryResult is a dictionary
   # queryResult = data['queryResult']
  
   # from the queryResult dictionary
   # get the value for the key action
   # somevalue = dictionary['key']
   # action is our variable name
   # action in queryResult['action'] is the key name
   # action = queryResult['action']
   
   # get the action name
   action = ""
   if 'action' in data['queryResult']:
       action = data['queryResult']['action']
   # conditional block to call relevant method for action
   # action name must be the same as dialogflow > intents > action
   if (action == 'test_connection'): 
       return test_connection()
   else:
       return no_implementation(data, action)


def test_connection():
   reply = {}
   reply["fulfillmentText"] = "Greetings from webhook"
   reply["fulfillmentMessages"] = []
   return jsonify(reply)


def no_implementation(data, action):
   intent_name = data['queryResult']['intent']['displayName']
   fulfillment_text = ""
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
