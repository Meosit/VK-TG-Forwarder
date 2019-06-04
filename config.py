import yaml
import io


class Config:

    CONFIG_PATH = 'config.yaml'

    def __init__(self):
        self.config = self._load_config()

        self.access_token = self.config['access_token']
        self.group_ids = self.config['group_ids']

        self.telegram_token = self.config['telegram_token']
        self.telegram_chat_id = self.config['telegram_chat_id']

        self.for_last_mins = self.config['for_last_mins']
        pass

    @staticmethod
    def _load_config():
        with open(Config.CONFIG_PATH, 'r') as stream:
            data = yaml.load(stream)
            return data

    def save_config(self):
        with io.open(Config.CONFIG_PATH, 'w', encoding='utf8') as outfile:
            yaml.dump(self.config, outfile, default_flow_style=False, allow_unicode=True)