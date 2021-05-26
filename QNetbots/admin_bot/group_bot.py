# -*- coding: utf-8 -*-

import os
import os.path
import traceback
import sys
from random import randrange
import subprocess
import sqlite3
import json

os.path.dirname(os.path.abspath(__file__)+'/../../')

from QNetbots.core_bot_api.bot import Bot
from QNetbots.core_bot_api.mregex_handler import MRegexHandler

class GroupSyncBot(Bot):

    def __init__(self, username, password, server, admins, home):
        super(GroupSyncBot, self).__init__(username, password, "https://%s"%server)
        self.server = server
        self.admins = admins
        print("admins:",self.admins)
        
        #json file for storing tree of rooms
        self.grptreefile = "grptree.json"

        self.grptree = {}
        if os.path.exists(self.grptreefile):
            with open(self.grptreefile) as f:
                self.grptree = json.load(f)

        # Add sync and dontSync regex handler
        self.sync_from_command = "!sync:"
        self.add_handler( MRegexHandler(self.sync_from_command, self.process_sync_command))

        self.dontsync_from_command = "!dontsync:"
        self.add_handler( MRegexHandler(self.dontsync_from_command, self.process_dontsync_command))

        self.import_from_command = "!import:"
        self.add_handler( MRegexHandler(self.import_from_command, self.process_import_command))

        
        self.group_state_command = "!groupstate:"
        self.add_handler( MRegexHandler(self.group_state_command, self.process_state_command))

        # Add general listener for new user and removing users from target rooms
        self.add_general_listener(self.general_listener)

        self.admins = admins
        self.synapse_home = home

    def run(self):
        self.start_polling()


    #Dumping group tree to file
    def dumpgrptree(self):
        #print(self.grptree)
        with open(self.grptreefile,'+w') as f:
            json.dump(self.grptree,f)


    #General listener for checking insertion and removal
    def general_listener(self, room, event):
        #Who Do the action
        sender = event['sender']
        roomid = event['room_id']
        if sender == "@groupsyncbot:quranic.network":
            return
        try:
            if 'state_key' in event:
                uid = event['state_key']
                # if event is joining room
                if event['type']=='m.room.member' and event['content']['membership']=='join':
                    # check if this join is after a system call ignore it
                    if roomid in self.grptree and uid in self.grptree[roomid]['inviting']:
                        print("remove wait for joining %s to %s"%(uid,roomid))
                        self.grptree[roomid]['inviting'].remove(uid)
                        self.dumpgrptree()
#                        return

                    # if this is manual join then this user should added to manual users of grptree
                    if roomid in self.grptree and uid not in self.grptree[roomid]['users']:
                        self.grptree[roomid]['users'].append(uid)
                        self.dumpgrptree()

                    # check if this person joind to one of target rooms(x)
                    for key in self.grptree:
                        if roomid in self.grptree[key]['rooms']:
                            #check what is y room
                            for proom in self.bot.rooms:
                                if proom.room_id == key:
                                    name = ''
                                    #get user name
                                    for u in room.get_joined_members():
                                        if event['state_key'] == u.user_id:
                                            name = u.get_display_name()

                                    #add this user to wait for come and invite
                                    self.grptree[key]['inviting'].append(event['state_key'])
                                    if event['state_key'] in self.grptree[key]['kicking']:self.grptree[key]['kicking'].remove(event['state_key'])
                                    proom.invite_user(event['state_key'])
                                    room.send_text(name+ ' دعوت شد به  '+proom.display_name)
                    self.dumpgrptree()
                #if event is leaving room
                if event['type']=='m.room.member' and event['content']['membership']=='leave':
                    #check if this leave is after a system call ignore it
                    if roomid in self.grptree and uid in self.grptree[roomid]['kicking']:
                        print("remove wait for kicking %s to %s"%(uid,roomid))
                        self.grptree[roomid]['kicking'].remove(uid)
                        self.dumpgrptree()
                        #return
                    
                    #if this is manual remove from users of manual
                    if roomid in self.grptree and uid in self.grptree[roomid]['users']:
                        self.grptree[roomid]['users'].remove(uid)

                    for key in self.grptree:
                        if roomid in self.grptree[key]['rooms']:
                            for proom in self.bot.rooms:
                                if proom.room_id == key:
                                    if event['state_key'] in self.grptree[key]['inviting']:self.grptree[key]['inviting'].remove(event['state_key'])
                                    self.grptree[key]['kicking'].append(event['state_key'])
                                    proom.kick_user(event['state_key'])
                                    room.send_text(event['state_key']+" خداحافظی کرد از"+proom.display_name)
                    self.dumpgrptree()

        except Exception as e: 
            traceback.print_exc()
            room.send_text(str(e))
        
    def process_state_command(self, room, event):
        sender = event['sender']
        roomid = event["room_id"]
        try:
            # print current synced rooms if !sync:
            if roomid in self.grptree:
                for proom in self.grptree[roomid]['rooms']:
                    for troom in self.bot.rooms:
                        if troom.room_id == proom:
                            room.send_text("به روز کردن کاربران از: " + troom.display_name)
                for tuser in self.grptree[roomid]['users']:
                    for u in room.get_joined_members():
                        if u.user_id == tuser:
                            room.send_text("کاربر ثابت:"+u.get_display_name())
            for proom in self.grptree:
                if roomid in self.grptree[proom]['rooms']:
                    for troom in self.bot.rooms:
                        if troom.room_id == proom:
                            room.send_text("به روز کننده کاربران در: "+troom.display_name)
        except Exception as e: 
            traceback.print_exc()
            room.send_text(str(e))

    def process_import_command(self, room, event):
        sender = event['sender']
        text = ":".join(event['content']['body'].strip().split(":")[1:])
        roomid = event["room_id"]
        target_room = None
        target_user = None
        try:
            permitted = 0
            if sender in self.admins:
                permitted = 2
            name = ''
            # check if requester is in room!!!
            for u in room.get_joined_members():
                if sender == u.user_id:
                    name = u.get_display_name()
                    permitted += 1


            # check if requester is in target room!!!
            for proom in self.bot.rooms:
                if proom.room_id == text:
                    target_room = proom
                    for u in proom.get_joined_members():
                        target_user = u
                        if sender == u.user_id:
                            permitted += 1
            if permitted>=2:
                room.send_text("دعوت به گروه از"+target_room.display_name)

                for u in target_room.get_joined_members():
                    add = True
                    for tu in room.get_joined_members():
                        if u.user_id == tu.user_id:
                            add = False
                    if add:
                        room.invite_user(u.user_id)
            else:
                room.send_text('شما دسترسی به اتاق هدف را ندارید')
                
        except Exception as e: 
            traceback.print_exc()
            room.send_text(str(e))


    def process_sync_command(self, room, event):
        sender = event['sender']
        text = ":".join(event['content']['body'].strip().split(":")[1:])
        roomid = event["room_id"]
        target_room = None
        target_user = None
        try:
            permitted = 0
            if sender in self.admins:
                permitted = 2
            name = ''
            # check if requester is in room!!!
            for u in room.get_joined_members():
                if sender == u.user_id:
                    name = u.get_display_name()
                    permitted += 1


            # check if requester is in target room!!!
            for proom in self.bot.rooms:
                if proom.room_id == text:
                    target_room = proom
                    for u in proom.get_joined_members():
                        target_user = u
                        if sender == u.user_id:
                            permitted += 1
            if permitted>=2:
                room.send_text("همسان سازی گروه از"+target_room.display_name)
                if roomid not in self.grptree:
                    self.grptree[roomid]={'users':[],'rooms':[],'inviting':[],'kicking':[]}
                    for u in room.get_joined_members():
                        self.grptree[roomid]['users'].append(u.user_id) 
                self.grptree[roomid]['rooms'].append(text)
                self.dumpgrptree()
                

                for u in target_room.get_joined_members():
                    add = True
                    for tu in room.get_joined_members():
                        if u.user_id == tu.user_id:
                            add = False
                    if add:
                        self.grptree[roomid]['inviting'].append(u.user_id)
                        if u.user_id in  self.grptree[roomid]['kicking']: self.grptree[roomid]['kicking'].remove(u.user_id)
                        room.invite_user(u.user_id)
                        #room.send_text("دعوت "+u.get_display_name())
                self.dumpgrptree()
            
            else:
                room.send_text('شما دسترسی به اتاق هدف را ندارید')
                
        except Exception as e: 
            traceback.print_exc()
            room.send_text(str(e))

    def process_dontsync_command(self, room, event):
        sender = event['sender']
        text = ":".join(event['content']['body'].strip().split(":")[1:])
        roomid = event["room_id"]

        target_room = None
        target_user = None
        try:
            permitted = 0
            if sender in self.admins:
                permitted = 2
            name = ''
            for u in room.get_joined_members():
                if sender == u.user_id:
                    name = u.get_display_name()
                    permitted += 1

            for proom in self.bot.rooms:
                if proom.room_id == text:
                    target_room = proom
                    for u in proom.get_joined_members():
                        if sender == u.user_id:
                            target_user = u
                            permitted += 1
            if permitted>=2:
                room.send_text("ناهمسان سازی گروه از"+text)
                if roomid in self.grptree:
                    if text in self.grptree[roomid]['rooms']:self.grptree[roomid]['rooms'].remove(text)
                    self.dumpgrptree()
                
                for u in target_room.get_joined_members():
                    if u.user_id == "@groupsyncbot:quranic.network" or u.user_id in self.admins:
                        continue
                    remove = len(self.grptree[roomid]['rooms'])>0
                    for otherroom in self.grptree[roomid]['rooms']: 
                        if otherroom is not target_room.room_id:
                            for otherroomobj in self.bot.rooms:
                                if otherroomobj.room_id == otherroom:
                                    for tu in otherroomobj.get_joined_members():
                                        if tu.user_id == u.user_id:
                                            remove = False
                                            break
                    if remove:
                        self.grptree[roomid]['kicking'].append(u.user_id)
                        if u.user_id in  self.grptree[roomid]['inviting']:self.grptree[roomid]['inviting'].remove(u.user_id)
                        room.kick_user(u.user_id)
                        #room.send_text("خداحافظی با "+u.get_display_name())
                        self.dumpgrptree()
            else:
                room.send_text("شما دسترسی لازم برای این کار را ندارید")
        except Exception as e: 
            traceback.print_exc()
            room.send_text(str(e))


