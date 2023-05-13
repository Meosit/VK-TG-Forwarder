# [START app]
import logging
import time

from config import Config

from vk_wall_fetcher import VkWallFetcher
from tg_request_mapper import TgRequestMapper

import json

config = Config()
fetcher = VkWallFetcher(config)
request_mapper = TgRequestMapper(config)

logging.getLogger().setLevel(logging.INFO)


def update_feed(event, context):
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
        except:
            url, data = request_mapper.simple_text_request_info("Unable to send request, please check logs")
            request_mapper.post_request(url, data)
            logging.exception("Failed to process request with data: " + json.dumps(data))
    return {
        'statusCode': 200,
        'body': ''
    }
