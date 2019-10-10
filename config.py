import yaml
import io


class Config:

    CONFIG_PATH = 'config.yaml'

    def __init__(self):
        self.config = self._load_config()

        self.vk_group_ids = self.config['vk_group_ids']
        self.vk_access_token = self.config['vk_access_token']

        self.telegram_chat_id = self.config['telegram_chat_id']
        self.telegram_bot_token = self.config['telegram_bot_token']

        self.fetch_posts_count = self.config['fetch_posts_count']
        self.fetch_threshold_minutes = self.config['fetch_threshold_minutes']
        self.fetch_overlap_seconds = self.config['fetch_overlap_seconds']

    @staticmethod
    def _load_config():
        with open(Config.CONFIG_PATH, 'r') as stream:
            data = yaml.load(stream)
            return data

    def save_config(self):
        with io.open(Config.CONFIG_PATH, 'w', encoding='utf8') as outfile:
            yaml.dump(self.config, outfile, default_flow_style=False, allow_unicode=True)