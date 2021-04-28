import os
os.path.dirname(os.path.abspath(__file__)+'/../../')
from QNetbots.core_bot_api.matrix_bot_api import MatrixBotAPI
from QNetbots.core_bot_api.mregex_handler import MRegexHandler
from QNetbots.core_bot_api.mcommand_handler import MCommandHandler



class Bot(object):
    def __init__(self, USERNAME,PASSWORD,SERVER):
        self.bot = MatrixBotAPI(USERNAME,PASSWORD,SERVER)

    def add_handler(self, handler):
        self.bot.add_handler(handler)

    def start_polling(self):
        self.bot.start_polling()

    def add_handlers(self, handlers):
        for handler in handlers:
            self.bot.add_handler(handler)

    @staticmethod
    def create_regex_base(regex, callback_f):
        return MRegexHandler(regex, callback_f)

    @staticmethod
    def create_command(command, callback_f):
        return MCommandHandler(command, callback_f)
