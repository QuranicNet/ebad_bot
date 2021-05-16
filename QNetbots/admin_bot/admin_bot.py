# -*- coding: utf-8 -*-

import os
import traceback
import sys
from random import randrange
import subprocess
import sqlite3

os.path.dirname(os.path.abspath(__file__)+'/../../')
#sys.path.append("/home/ebad/synapse/env/bin")

from QNetbots.core_bot_api.bot import Bot
from QNetbots.core_bot_api.mregex_handler import MRegexHandler

class AdminBot(Bot):

    def __init__(self, username, password, server, admins, home):
        super(AdminBot, self).__init__(username, password, "https://%s"%server)
        self.server = server
        
        # Add arabic regex handler
        self.new_user_command = "!کاربر جدید:"
        message_handler = MRegexHandler(self.new_user_command, self.process_command)
        self.add_handler(message_handler)

        self.change_pass_command = "!گذرواژه:"
        self.add_handler(MRegexHandler(self.change_pass_command,self.change_pass))
        self.admins = admins
        self.synapse_home = home

    def run(self):
        self.start_polling()

    def change_pass(self,room,event):
        sender = event['sender']
        text = event['content']['body'].strip()
        tparts = text.split(':')
        name = tparts[1].strip()	

        try:
#        if True:
            if sender in self.admins:
                room.send_text("تغییر گذرواژه")
                #name = text[len(self.new_user_command):]
                passw = randrange(100000,999999)
                commands = ["hash_password", "-p", "%d"%passw]
                hashed = subprocess.check_output(commands).strip()
                
                con = sqlite3.connect('%s/homeserver.db'%self.synapse_home)
                cur = con.cursor()
                sql = "UPDATE users SET password_hash=\"%s\" WHERE name='@%s:%s';"%(hashed,name,self.server)  
                cur.execute(sql)
                con.commit()
                con.close()
                room.send_text("سلام علیکم\nگذرواژه شما تغییر کرد:\n%s"%passw)
        except Exception as e: room.send_text(str(e))

    def process_command(self, room, event):
        sender = event['sender']
        text = event['content']['body'].strip()
        tparts = text.split(':')
        name = tparts[1].strip()	

        try:
#        if True:
            if sender in self.admins:
                room.send_text("کاربر جدید")
                #name = text[len(self.new_user_command):]
                passw = randrange(100000,999999)
                commands = ["register_new_matrix_user","-u",name, "-p", "%d"%passw, "-c%s/homeserver.yaml"%self.synapse_home ,"--no-admin", "https://%s"%self.server]
                #room.send_text(" ".join(commands))
                print(subprocess.check_output(commands))
                room.send_text("""سلام علیکم،
                نام کاربری شما:
%s

گذرواژه شما:
%d

آدرس دانلود نرم افزار:
element.io/get-started

آدرس سرور برای کپی هنگام لاگین در نرم افزار:
%s"""%(name,passw,self.server))
        except Exception as e: 
            traceback.print_exc()
            room.send_text(str(e))



