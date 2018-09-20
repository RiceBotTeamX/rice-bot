#Python libraries that we need to import for our bot
from flask import Flask, request
from pymessenger.bot import Bot
import random
import sys
import os 
import json
import csv
import subprocess
import datetime
import time
from spell_checker import correct_sentence

from wit import Wit
dir_path = os.path.dirname(os.path.realpath(__file__))
access_token = "GGDBZAV5X6J5CJBCKOOLWWWMMMMSHTHR"
wit_client = Wit(access_token)

app = Flask(__name__) ## This is how we create an instance of the Flask class for our app

ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot(ACCESS_TOKEN) ## Create an instance of the bot

HELP_MESSAGE = "I can provide information about dining options, allergies, and schedules here at Rice!"
EXAMPLES = ["gluten-free", "is there vegetarian at West or Seibel?", "are eggs served at North today?", "vegan at South?", "west"]
EMOJIS = [u'\U001F600', u'\U001F44C', u'\U001F64C', u'\U001F37D']

EATERIES = ["west", "north", "south", "seibel", "sid", "baker", "sammy's"]
CONFIDENCE_THRESH = .575
#MEALTIMES = {"breakfast" : }

def help_statement():
    return HELP_MESSAGE + " Ask me a question like \"" + random.choice(EXAMPLES) + "\"" + random.choice(EMOJIS)

def verify_fb_token(token_sent):
    ## Verifies that the token sent by Facebook matches the token sent locally
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

def time_stamp_gen():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    return st;

def dining_reader():
    filename = "diningData-" + time_stamp_gen() + ".csv"
    dining_data_file = "./data/" + filename
    print ("file name: ", dining_data_file)
    # If there is no file in the data folder with todays date, call ruby.
    # Else, use the file in the data folder.
    if (not os.path.isfile(dining_data_file)):
        subprocess.check_output(['python3', dir_path+'/severyAPI/getMenu.py', filename])

    dining_data = []
    with open(dining_data_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            dining_data.append(row)

        return dining_data
    return []

def is_open(servery, dining_data):
    for row in dining_data:
        if row[0].lower() == servery:
            if row[1] == "true":
                words = row[2].split()
                if words[1].lower() != "available":
                    return True

    return False

def menu_options(servery, dining_data):
    options = []
    for row in dining_data:
        if row[0].lower() == servery:
            if row[2]:
                options.append(row[2].strip('\"'))

    return options

def print_menu(servery, dining_data):
    menu = menu_options(servery, dining_data)
    menu_text = ""
    if len(menu) > 0:
        menu_text += servery.capitalize() + " is serving "
        for m in range(len(menu)):
            menu_text += menu[m]
            if m < len(menu) - 2:
                menu_text += ", "
            elif m == len(menu) - 2:
                menu_text += " and "
    return menu_text

def servery_food_find(food, dining_data):
    serveries = []
    for row in dining_data:
        servery = row[0].lower()
        if ((food in row[3].lower().split()) or (food in row[2].lower().split())) and servery not in serveries:
            serveries.append(servery)
    return serveries

def single_servery_food_find(food, servery, dining_data):
    meals = []
    for row in dining_data:
        serv = row[0].lower()
        if servery == serv:
            if food in row[2].lower().split() or food in row[3].lower().split():
                meals.append(row[2])

    return meals

def servery_food_exclude(food, dining_data):
    serveries = []
    for row in dining_data:
        servery = row[0].lower()
        if (food not in row[3].lower().split()) and (food not in row[2].lower().split()) and servery not in serveries:
            serveries.append(servery)

    return serveries

def single_servery_food_exclude(food, servery, dining_data):
    meals = []
    for row in dining_data:
        serv = row[0].lower()
        if servery == serv:
            if food not in row[2].lower().split() and food not in row[3].lower().split():
                meals.append(row[2])

    return meals

# Chooses a message to send to the user
def get_response_text(message):
    message_text = ""
    if 'text' in message:
        message_text = message['text']
    else:
        return help_statement()

    response_message = ""

    message_text_correct = correct_sentence(message_text)

    nlp_response = wit_client.message(message_text_correct)

    if ('entities' in nlp_response):

        nlp_entities = nlp_response['entities']

        dining_data = dining_reader()

        eating = False
        schedule = []
        time_input = []
        serveries = []
        serveries_mentioned = False
        mealtype_input = []
        foodtype_input = []
        diet_input = []

        if ('eating' in nlp_entities and nlp_entities['eating'][0]['confidence'] > CONFIDENCE_THRESH):
            #response_message += "I am " + str(round(nlp_entities['eating'][0]['confidence'] * 100)) + \
            #                    "% confident you are talking about eating\n"
            
            # If the user provided no information other than indication that they are talking about eating
            eating = True         

        if ('schedule' in nlp_entities):
            """
            response_message += "I am " + str(round(nlp_entities['schedule'][0]['confidence'] * 100)) + \
                                "% confident you are talking about schedules\n"
            """
            entity = nlp_entities['schedule']
            for s in entity:
                if s['confidence'] > CONFIDENCE_THRESH:
                    schedule.append(s['value'].lower().strip())

        if ('datetime' in nlp_entities):
            """
            response_message += "I am " + str(round(nlp_entities['datetime'][0]['confidence'] * 100)) + \
                                "% confident you are talking about date and time\n"
            """
            entity = nlp_entities['datetime']
            for t in entity:
                if 'confidence' in t and t['confidence'] > CONFIDENCE_THRESH and 'value' in t:
                    time_input.append(t['value'])

        if ('serveries' in nlp_entities):
            #response_message += "I am " + str(round(nlp_entities['serveries'][0]['confidence'] * 100)) + \
            #                    "% confident you are talking about serveries\n"

            entity = nlp_entities['serveries']
            serveries = []
            serveries_mentioned = True
            for s in entity:
                if s['confidence'] > CONFIDENCE_THRESH:
                    servery = s['value'].lower().strip()

                    if servery == "sammys":
                        servery = "sammy's"
                    elif servery == "sid richardson":
                        servery = "sid"
                    elif servery == "duncan":
                        servery = "west"
                    elif servery == "mcmurtry":
                        servery = "west"
                    elif servery == "martel":
                        servery = "north"
                    elif servery == "jones":
                        servery = "north"
                    elif servery == "brown":
                        servery = "north"
                    elif servery == "will rice":
                        servery = "seibel"
                    elif servery == "lovett":
                        servery = "seibel"
                    elif servery == "hanszen":
                        servery = "south"
                    elif servery == "weiss":
                        servery = "south"

                    if servery in EATERIES:
                        serveries.append(servery)

        if ('mealtype' in nlp_entities):
            """
            response_message += "I am " + str(round(nlp_entities['mealtype'][0]['confidence'] * 100)) + \
                                "% confident you are talking about meals\n"
            """

            entity = nlp_entities['mealtype']
            for m in entity:
                if m['confidence'] > CONFIDENCE_THRESH:
                    mealtype_input.append(m['value'])


        if ('foodtype' in nlp_entities):
            """
            response_message += "I am " + str(round(nlp_entities['foodtype'][0]['confidence'] * 100)) + \
                                "% confident you are talking about foods\n"
            """
            entity = nlp_entities['foodtype']
            for f in entity:
                if f['confidence'] > CONFIDENCE_THRESH:
                    foodtype_input.append(f['value'])

        if ('dietary' in nlp_entities):
            """
            response_message += "I am " + str(round(nlp_entities['dietary'][0]['confidence'] * 100)) + \
                                "% confident you are talking about dietary restrictions\n"
            """
            entity = nlp_entities['dietary']
            for d in entity:
                if d['confidence'] > CONFIDENCE_THRESH:
                    diet_input.append(d['value'])


        ##### CREATING THE MESSAGE #####
        if diet_input or foodtype_input:
            # Determine whether we should look for foods or exclude foods
            inclusion = False
            
            diets = foodtype_input[:]

            if diet_input:
                if "vegetarian" in diet_input:
                    inclusion = True
                    diets.append("vegetarian")

                if "vegan" in diet_input:
                    inclusion = True
                    diets.append("vegan")
            else:
                inclusion = True

            # If no specific servery has been specified, look in them all
            if not serveries:
                for diet in diets:
                    found_serveries_all = []
                    if inclusion:
                        found_serveries_all = servery_food_find(diet, dining_data)
                    else:
                        found_serveries_all = servery_food_exclude(diet, dining_data)

                    found_serveries = []
                    for serv in found_serveries_all:
                        if is_open(serv, dining_data):
                            found_serveries.append(serv)

                    for serv in range(len(found_serveries)):
                        response_message += found_serveries[serv].capitalize()
                        if serv < len(found_serveries) - 2:
                            response_message += ", "
                        elif serv == len(found_serveries) - 2:
                            response_message += " and "

                    if len(found_serveries) > 0:
                        if len(found_serveries) > 1:
                            response_message += " have "
                        else:
                            response_message += " has "

                        response_message += diet

                        if not inclusion:
                            response_message += " free"

                        response_message += " options today.\n \n"

                    # No food found
                    else:
                        response_message += "There are no " + diet

                        if not inclusion:
                            response_message += " free"

                        response_message += " options today.\n \n"

            # If serveries have been specified
            else:
                for servery in serveries:
                    if is_open(servery, dining_data):
                        for diet in diets:
                            found_meals = []
                            if inclusion:
                                found_meals = single_servery_food_find(diet, servery, dining_data)
                            else:
                                found_meals = single_servery_food_exclude(diet, servery, dining_data)

                            num_meals = len(found_meals)
                            if num_meals > 0:
                                response_message += servery.capitalize() + " is serving"
                                if num_meals > 1:
                                    response_message += " these "
                                else:
                                    response_message += " this "

                                response_message += diet

                                if not inclusion:
                                    response_message += " free"
                                response_message += " foods today: "

                                for m in range(num_meals):
                                    response_message += found_meals[m]
                                    if m < num_meals - 2:
                                        response_message += ", "
                                    elif m == num_meals - 2:
                                        response_message += " and "

                                response_message += "\n \n"

                            else: # The servery has no options of this diet
                                response_message += servery.capitalize() + " is not serving any " + diet
                                if not inclusion:
                                    response_message += " free"
                                response_message += " food today.\n \n"

                    else:
                        response_message += servery.capitalize() + " is closed today.\n \n"


        elif (serveries_mentioned):
            if serveries:
                for servery in serveries:
                    if is_open(servery, dining_data):
                        menu_text = print_menu(servery, dining_data)
                        if menu_text:
                            response_message += menu_text + " today.\n"
                        else:
                            response_message += "We don't know the menu for " + servery.capitalize() + " right now.\n \n"

                    # If the servery is closed
                    else:
                        response_message += servery.capitalize() + " is closed today.\n \n"

            # If the eatery is unrecognized
            elif len(nlp_entities) == 1 or (len(nlp_entities) == 2 and "eating" in nlp_entities):
                response_message += "It seems like you're interested in serveries. " + help_statement() + "\n"

        # General statement regarding eating
        elif (eating and len(nlp_entities) == 1):
            response_message = "It seems like you're interested in eating. " + help_statement()


    if not response_message:
        response_message = "I don't understand that statement. " + help_statement()

    return response_message

# Checks whether the first entitiy is 'name' or not
def firstEntity(nlp):
    if nlp and 'entities' in nlp:
        return nlp['entities']
    else:
        return False

## Send text message to recipient
def send_message(recipient_id, response):
    bot.send_text_message(recipient_id, response) ## Sends the 'response' parameter to the user
    return "Message sent"

## This endpoint will receive messages 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    ## Handle GET requests
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token") ## Facebook requires a verify token when receiving messages
        return verify_fb_token(token_sent)

    ## Handle POST requests
    else: 
        output = request.get_json() ## get whatever message a user sent the bot

        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    recipient_id = message['sender']['id'] ## Facebook Messenger ID for user so we know where to send response back to

                    response_text = get_response_text(message['message'])
                    send_message(recipient_id, response_text)

        return "Message Processed"

## Ensures that the below code is only evaluated when the file is executed, and ignored if the file is imported
if __name__ == "__main__": 
    app.run() ## Runs application
