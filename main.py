# [START app]
import logging
import time
from httplib import HTTPException

from google.appengine.api import urlfetch
from config import Config
from flask import Flask

from vk_wall_fetcher import VkWallFetcher
from tg_request_mapper import TgRequestMapper

app = Flask(__name__)
config = Config()
fetcher = VkWallFetcher(config)
request_mapper = TgRequestMapper(config)


@app.route('/bot/' + config.telegram_bot_token)
def update_feed():
    urlfetch.set_default_fetch_deadline(20)
    fetch_threshold_date = int(time.time()) - config.fetch_threshold_minutes * 60 - config.fetch_overlap_seconds
    logging.info("Threshold is " + str(fetch_threshold_date) + ", now is " + str(time.time()))

    request_info = []
    for group_id in config.vk_group_ids:
        logging.info("Loading from " + str(group_id))
        posts = fetcher.fetch_wall_posts(group_id, fetch_threshold_date)
        for post in posts:
            request_info.append(request_mapper.convert_to_telegram_request_info(post))

    # natural order within whole feed
    request_list = [request_data
                    for request_info in sorted(request_info, key=lambda r: r['date'])
                    for request_data in request_info['requests']]

    for url, data in request_list:
        try:
            request_mapper.post_request(url, data)
        except HTTPException as e:
            if 'Deadline exceeded while waiting for HTTP response' in str(e):
                logging.info("Deadline exceeded error captured for " + str(data))
            else:
                logging.exception("Error while sending post to the telegram")
                logging.error(str(data))
                url, data = request_mapper.simple_text_request_info("Unable to send request, please check logs")
                request_mapper.post_request(url, data)
    return 'OK'


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
# [END app]


if __name__ == '__main__':
    update_feed()