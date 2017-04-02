import os
import sys
import json
import pickle

import requests
from flask import Flask, request

app = Flask(__name__)

sender_db = pickle.load(open('database.db', 'rb'))

def execute(msg, sender):
    msg = msg.split()
    print msg
    if (msg[0][0] in 'ABCDE') and (msg[1][0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']):
        sender_db[sender] = {section: msg[0], group: msg[1]}
    if sender in sender_db.keys():
        section = sender_db[sender][section]
        group = sender_db[sender][group]

        return "You are in section", section, 'and practical group', group

    else:
        return "Enter section and group in this format: \"S G\""


@app.route('/', methods=['GET'])
def verify():
    return request.args["hub.challenge"], 200

@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    send_message(sender_id, execute(message_text, sender_id))

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
