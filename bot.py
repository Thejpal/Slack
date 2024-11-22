import os
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

slack_app = App(token = os.environ["SLACK_BOT_USER_OAUTH_TOKEN"], signing_secret = os.environ["SLACK_SIGNING_SECRET"])

flask_app = Flask(__name__)

handler = SlackRequestHandler(app = slack_app)

SLACK_BOT_USER_ID = os.environ["SLACK_BOT_USER_ID"]

def get_bot_user_id():
    try:
        client = WebClient(token = os.environ["SLACK_BOT_USER_OAUTH_TOKEN"])
        response = client.auth_test()
        return response["user_id"]
    except SlackApiError as e:
        print(f"Error {e}")

@slack_app.event("app_mention")
def handle_mention_event(payload, say):
    print("payload from mention event")
    print(payload)
    if payload.get("files") is not None:
        files = payload["files"]
        file_urls = []
        for file in files:
            file_url = file["url_private"]
            file_urls.append(file_url)
        print(file_urls)
    channel = payload["channel"]
    user = payload["user"]
    prompt = payload["text"]
    profile = slack_app.client.users_profile_get(user = user, include_labels = False)
    user_name = profile["profile"]["real_name"]
    say(f"Hi {user_name} from {channel}. Messaging from mention event. Thanks for the following message {prompt}")

@slack_app.event("message")
def handle_message_event(payload, say):
    print("payload from message event")
    print(payload)
    channel = payload["channel"]
    user = payload["user"]
    say(f"Hi {user} from {channel}. Messaging from message event")

@slack_app.message("boo")
def handle_messages(message, say):
    say(f"Ahhhhhhhh. Dont scare me with {message}")

@slack_app.command("/upload")
def upload_command(ack, payload, logger):
    slack_app.client.files_list()
    ack()
    print(payload)
    logger.info(payload)

@flask_app.route("/slack/events", methods = ["POST"])
def handle_slack():
    return handler.handle(request)

if __name__ == "__main__":
    flask_app.run(debug = True)