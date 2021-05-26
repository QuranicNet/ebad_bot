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

    if len(config['adminbot']['user'].strip())>0:
        adminbot = AdminBot(config['adminbot']['user'],config['adminbot']['password'],config['adminbot']['server'],config['adminbot']['admins'].split(","),config['adminbot']['synapse_home'])
        adminbot.run()
    
    if len(config['grpbot']['user'].strip())>0:
        groupsyncbot = GroupSyncBot(config['grpbot']['user'],config['grpbot']['password'],config['grpbot']['server'],config['grpbot']['admins'].split(","),config['grpbot']['synapse_home'])
        groupsyncbot.run()
    # Infinitely read stdin to stall main thread while the bot runs in other threads
    while True:
        input()
