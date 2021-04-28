from QNetbots.bots_simple.simple_bot import SimpleBot

import configparser

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    simplebot = SimpleBot(config['mybot']['user'],config['mybot']['password'],config['mybot']['server'])
    simplebot.run()

    # Infinitely read stdin to stall main thread while the bot runs in other threads
    while True:
        input()
