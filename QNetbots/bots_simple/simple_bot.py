# -*- coding: utf-8 -*-

import os
os.path.dirname(os.path.abspath(__file__)+'/../../')

from QNetbots.core_bot_api.bot import Bot
from QNetbots.core_bot_api.mregex_handler import MRegexHandler

class SimpleBot(Bot):

    def __init__(self, username, password, server):
        super(SimpleBot, self).__init__(username, password, server)

        # Add arabic regex handler
        message_handler = MRegexHandler("@سلام", self.process_command)
        self.add_handler(message_handler)

    def run(self):
        self.start_polling()

    def process_command(self, room, event):

        text = event['content']['body']

        try:
            room.send_text("علیکم السلام")
        except:
            room.send_text("خطا");



