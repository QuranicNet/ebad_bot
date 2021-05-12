from QNetbots.bots_simple.simple_bot import SimpleBot
from QNetbots.admin_bot.admin_bot import AdminBot

import configparser

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    #simplebot = SimpleBot(config['mybot']['user'],config['mybot']['password'],config['mybot']['server'])
    #simplebot.run()

    adminbot = AdminBot(config['mybot']['user'],config['mybot']['password'],config['mybot']['server'],config['mybot']['admins'].split(","),config['mybot']['synapse_home'])
    adminbot.run()
    # Infinitely read stdin to stall main thread while the bot runs in other threads
    while True:
        input()
