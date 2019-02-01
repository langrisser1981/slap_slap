import paho.mqtt.client as paho
from urllib.parse import urlparse
import os
import sys
import json

mqttc = paho.Client()

def lambda_handler(event, context):
    initMQTT()

    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
    print(event["context"]["System"]["device"])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    # Publish a message
    data = {"Command":"step","Target":"1"}
    message = json.dumps(data)
    print("message is:"+message)
    #SendMQTT(data)
    mqttc.publish("ces/slap", message )

    """ Called when the session starts """
    print(session["user"]["userId"])


    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "ShowCamera":
        return ShowCamera_session(intent, session)
    elif intent_name == "ShowPhoto":
        return ShowPhoto_session(intent, session)
    elif intent_name == "ShowVideo":
        return ShowVideo_session(intent, session)
    elif intent_name == "GoToHomeScreen":
        return GoToHomeScreen_session(intent, session)
    elif intent_name == "ShowMusic":
        return ShowMusic_session(intent, session)
    elif intent_name == "PhoneCall":
        return PhoneCall_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")
        
    #if intent_name == "MyColorIsIntent":
    #    return set_color_in_session(intent, session)
    #elif intent_name == "WhatsMyColorIntent":
    #    return get_color_from_session(intent, session)
    #elif intent_name == "AMAZON.HelpIntent":
    #    return get_welcome_response()
    #elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
    #    return handle_session_end_request()
    #else:
    #    raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


# Define event callbacks
def getnow():
    #return str(datetime.now()) + " "
    return " "

def on_connect(mosq, obj, rc):
    print(getnow() + "rc: " + str(rc))

def on_message(mosq, obj, msg):
    print(getnow() + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_publish(mosq, obj, mid):
    print(getnow()+ "mid: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    print(getnow() + "Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    print(getnow() + string)
    
    

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Hi, I am Lucy from Compal electronic. " \
                    "Please tell me what you want to do"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me what you want to do."
    should_end_session = True
       
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def initMQTT():    
    # Assign event callbacks
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
  
    # Uncomment to enable debug messages
    #mqttc.on_log = on_log

    # Parse CLOUDMQTT_URL (or fallback to localhost)
    #url_str = os.environ.get('CLOUDMQTT_URL', 'mqtt://localhost:1883')  #CCI_ROGER
    #url_str = os.environ.get('CLOUDMQTT_URL', 'mqtt://ec2-54-165-229-254.compute-1.amazonaws.com:1883')
    url_str = os.environ.get('CLOUDMQTT_URL', 'mqtt://35.185.154.72:1883')
    url = urlparse(url_str)

    # Connect
    #mqttc.username_pw_set(url.username, url.password) #CCI_ROGER
    mqttc.connect(url.hostname, url.port)


def ShowCamera_session(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    data = {"Command":"Start","Target":"Camera"}

    SendMQTT(data)
    
    speech_output = "OK, I have show the camera."
    reprompt_text = "I'm not sure what you are saying, please say again."    
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def ShowPhoto_session(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    data = {"Command":"Start","Target":"Photo"}

    SendMQTT(data)
    
    speech_output = "OK, I have show the Photo."
    reprompt_text = "I'm not sure what you are saying, please say again."    
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def ShowVideo_session(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    data = {"Command":"Start","Target":"Video"}

    SendMQTT(data)
    
    speech_output = "OK, I have show the Video."
    reprompt_text = "I'm not sure what you are saying, please say again."    
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def GoToHomeScreen_session(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    data = {"Command":"Start","Target":"HomeScreen"}

    SendMQTT(data)
    
    speech_output = "OK."
    reprompt_text = "I'm not sure what you are saying, please say again."    
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def ShowMusic_session(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    data = {"Command":"Start","Target":"Music"}

    SendMQTT(data)
    
    speech_output = "OK, I will play the music"
    reprompt_text = "I'm not sure what you are saying, please say again."    
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def PhoneCall_session(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    data = {"Command":"Start","Target":"PhoneCall"}

    SendMQTT(data)
    
    speech_output = "OK."
    reprompt_text = "I'm not sure what you are saying, please say again."    
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
        
def set_color_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Color' in intent['slots']:
        favorite_color = intent['slots']['Color']['value']
        session_attributes = create_favorite_color_attributes(favorite_color)
        speech_output = "I now know your favorite color is " + \
                        favorite_color + \
                        ". You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
        reprompt_text = "You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your favorite color is. " \
                        "You can tell me your favorite color by saying, " \
                        "my favorite color is red."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def create_favorite_color_attributes(favorite_color):
    return {"favoriteColor": favorite_color}


def get_color_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "favoriteColor" in session.get('attributes', {}):
        favorite_color = session['attributes']['favoriteColor']
        speech_output = "Your favorite color is " + favorite_color + \
                        ". Goodbye."
        should_end_session = True
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "You can say, my favorite color is red."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
