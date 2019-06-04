# [START app]
import logging
import traceback
from config import Config
from sender import Sender
from loader import Loader

from flask import Flask

app = Flask(__name__)
config = Config()
loader = Loader(config)
sender = Sender(config)


@app.route('/bot/' + config.telegram_token)
def hello():
    try:
        logging.info("Requesting for groups: " + str(', '.join([str(o) for o in config.group_ids])))
        feed = loader.load_communities_feed(config.group_ids)
        sender.send_posts(feed)
        logging.info("Sent " + str(len(feed)) + " posts")
    except Exception as e:
        logging.warning('An error occurred during a request.', e)
        sender.send_text({'name': 'SERVICE MESSAGE', 'text': '```{}```'.format(traceback.format_exc())})
    return 'OK'


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
# [END app]