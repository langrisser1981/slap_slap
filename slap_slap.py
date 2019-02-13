import paho.mqtt.client as paho
from urllib.parse import urlparse
import os
import sys
import json
import random

mqttc = paho.Client()


def on_session_started(session_started_request, session):
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
    if intent_name == "play":
        return talk(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        return talk(intent, session)
        #raise ValueError("Invalid intent")
        
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
    print(getnow() + "on_connect:'mqtt://35.185.154.72:1883', " + str(rc))

def on_message(mosq, obj, msg):
    print(getnow() + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_publish(mosq, obj, mid):
    print(getnow()+ "on_publish: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    print(getnow() + "on_subscribe: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    print(getnow() + string)


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
    mqttc.loop_start()
    print("mqtt info, host:" + str(url.hostname) + ", port:" + str(url.port))


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {'counter':1}
    card_title = "Welcome"
    #speech_output = "Hi, I am Lucy from Compal electronic. " \                    "Please tell me what you want to do"
    speech_output = get_conversation(session_attributes['counter'])
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me what you want to do."
    should_end_session = False
       
    #return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
    return build_response(session_attributes, build_speechlet_ssml_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    #speech_output = "Thank you for trying the Alexa Skills Kit sample. " \                    "Have a nice day! "
    speech_output = "bye bye~ Have a nice day!"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def talk(intent, session):
    session_attributes = session['attributes']
    if "counter" in session_attributes:
        session_attributes['counter'] += 1
    else:
        session_attributes['counter'] = 1
        
    card_title = intent['name']
    counter = session_attributes['counter']
    if counter > 9:
        should_end_session = True
    else:
        should_end_session = False

    #speech_output = "<speak>"+"number:"+str(counter)+"Welcome to Car-Fu. <audio src='soundbank://soundlibrary/transportation/amzn_sfx_car_accelerate_01' />     You can order a ride, or request a fare estimate.     Which will it be?</speak>"
    speech_output = get_conversation(counter)
    reprompt_text = "I'm not sure what you are saying, please say again."    
    
    return build_response(session_attributes, build_speechlet_ssml_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_conversation(num):
    # Publish a message
    # mqttc.loop()
    data = {"Command":"SlapSlap","Pages":str(num)}
    message = json.dumps(data)
    print("mqtt message=> topic:ces/slap, payload:"+message)
    mqttc.publish("ces/slap", message )

    group_of_items = ["<audio src='soundbank://soundlibrary/animals/amzn_sfx_cat_meow_1x_01'/>",
            "<audio src='soundbank://soundlibrary/animals/amzn_sfx_dog_med_bark_1x_01'/>",
            "<audio src='soundbank://soundlibrary/animals/amzn_sfx_elephant_01'/>",
            "<audio src='soundbank://soundlibrary/animals/amzn_sfx_horse_huff_whinny_01'/>",
            "<audio src='soundbank://soundlibrary/animals/amzn_sfx_lion_roar_01'/>",
            "<audio src='soundbank://soundlibrary/animals/amzn_sfx_rat_squeaks_01'/>",
            "<audio src='soundbank://soundlibrary/animals/amzn_sfx_rooster_crow_01'/>",
            "<audio src='soundbank://soundlibrary/animals/amzn_sfx_wolf_howl_02'/>",
            "<audio src='soundbank://soundlibrary/animals/amzn_sfx_bird_chickadee_chirp_1x_01'/>",
            "<audio src='soundbank://soundlibrary/animals/amzn_sfx_crow_caw_1x_02'/>"]
    num_to_select = 5
    #audio = ", ".join(group_of_items[:num_to_select])
    audio = ", ".join(random.sample(set(group_of_items), num_to_select))
    
    audio_fixed = {
        3:"<audio src='soundbank://soundlibrary/animals/amzn_sfx_bird_chickadee_chirp_1x_01'/>" + \
            "<audio src='soundbank://soundlibrary/animals/amzn_sfx_sheep_bleat_03'/>" + \
            "<audio src='soundbank://soundlibrary/animals/amzn_sfx_cat_meow_1x_01'/>" + \
            "<audio src='soundbank://soundlibrary/animals/amzn_sfx_dog_med_bark_1x_01'/>",
        4:"<audio src='soundbank://soundlibrary/animals/amzn_sfx_elephant_01'/>" + \
            "<audio src='soundbank://soundlibrary/animals/amzn_sfx_horse_huff_whinny_01'/>" + \
            "<audio src='soundbank://soundlibrary/animals/amzn_sfx_rooster_crow_01'/>" + \
            "<audio src='soundbank://soundlibrary/animals/amzn_sfx_cat_meow_1x_01'/>",
        8:"<audio src='soundbank://soundlibrary/animals/amzn_sfx_sheep_baa_01'/>" + \
            "<audio src='soundbank://soundlibrary/animals/amzn_sfx_wolf_howl_02'/>" + \
            "<audio src='soundbank://soundlibrary/animals/amzn_sfx_bear_groan_roar_01'/>" + \
            "<audio src='soundbank://soundlibrary/animals/amzn_sfx_dog_med_bark_1x_01'/>",
    }
    audio = audio_fixed.get(num, "")
    print("num:"+str(num)+", audio:"+audio)
    
    dialogs = {
        1:"<speak>OK! Let us play Slap Slap, what level do you want to play?</speak>",
        2:"<speak>Let us start the game, Are you ready?</speak>",
        3:"<speak>five, four, three, two, one. Slap the dog sound!"+audio+"</speak>",
        4:"<speak>Next, slap the cat sound!"+audio+"</speak>",
        5:"<speak>Oops! You are lose! Do you wanna resume the game or start the punishment?</speak>",
        6:"<speak>OK! Welcome back, What level do you want to play?</speak>",
        7:"<speak>Let’s start the game, Are you ready?</speak>",
        8:"<speak>five, four, three, two, one. Slap number 22 in blue circle with cat sound!"+audio+"</speak>",
        9:"<speak>Great! Do you wanna continue?</speak>",
        10:"<speak>bye bye</speak>"
    }
    
    dialog = dialogs.get(num, "I am not sure what you are saying, please say again.")
    print("speech_output:"+dialog)
    return dialog

        
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
def build_speechlet_ssml_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
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
