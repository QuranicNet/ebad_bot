from QNetbots.bots_simple.simple_bot import SimpleBot
from QNetbots.admin_bot.admin_bot import AdminBot
from QNetbots.admin_bot.group_bot import GroupSyncBot

import configparser

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')

    if len(config['mybot']['user'].strip())>0:
        simplebot = SimpleBot(config['mybot']['user'],config['mybot']['password'],config['mybot']['server'])
        simplebot.run()

    # Infinitely read stdin to stall main thread while the bot runs in other threads
    while True:
        input()
