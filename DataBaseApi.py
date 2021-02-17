# -*- coding: utf-8 -*-
import traceback

import redis
import os
import Floppas
import json
import random
import time


class DataBase:
    FEED_ONCE_VALUE = 25
    HUNGRY_ONCE_VALUE = 10

    def __init__(self):
        self.db = redis.from_url(os.environ['REDIS_URL'])

    def get_floppa_types(self):
        types_length = self.db.llen('FLOPPA_TYPES_LIST:types')
        types = []
        for i in range(types_length):
            types.append(self.db.lindex('FLOPPA_TYPES_LIST:types', i))

        floppas = []
        for ftype in types:
            floppa = {}
            fields = self.db.hkeys(b'FLOPPA_TYPES_LIST:' + ftype)
            for field in fields:
                value = self.db.hget(b'FLOPPA_TYPES_LIST:' + ftype, field)
                if field == b'rarity':
                    floppa['rarity'] = bytes.decode(value)
                elif field == b'photo_url':
                    floppa['photo_url'] = bytes.decode(value)
            floppas.append(floppa)

        return floppas

    def get_chats(self):
        chats_length = self.db.llen('Profiles:chats')
        chats = []
        for i in range(chats_length):
            chats.append(bytes.decode(self.db.lindex('Profiles:chats', i)))
        return chats

    def init_new_profiles(self, profiles, chat_id):
        if not str(chat_id) in self.get_chats():
            self.db.lpush('Profiles:chats', str(chat_id))
        for profile in profiles:
            self.db.hset('Profiles:'+str(chat_id), profile,
                         '{"floppas": [], "inventory": [], "can_gacha": true, "saved_floppa": 0}')

    def init_new_profile(self, chat_id, user_id):
        if not str(chat_id) in self.get_chats():
            self.db.lpush('Profiles:chats', str(chat_id))
        self.db.hset('Profiles:' + str(chat_id), user_id,
                     '{"floppas": [], "inventory": [], "can_gacha": true, "saved_floppa": 0}')

    def get_user_floppas(self, chat_id, user_id):
        try:
            user = bytes.decode(self.db.hget('Profiles:'+str(chat_id), user_id))
            parsed = json.loads(user)
            floppas = parsed['floppas']
            result = []
            for floppa in floppas:
                result.append(Floppas.Floppa(
                    floppa['hungry'],
                    floppa['petted'],
                    floppa['damage'],
                    floppa['flopping'],
                    floppa['hiss'],
                    floppa['size'],
                    floppa['name'],
                    floppa['rarity'],
                    floppa['photo_url'],
                    floppa['feed_time']
                ))
            return result
        except:
            print('Ошибка: ', traceback.format_exc())
            return False

    def get_user_inventory(self, chat_id, user_id):
        try:
            user = bytes.decode(self.db.hget('Profiles:'+str(chat_id), user_id))
            parsed = json.loads(user)
            inventory = parsed['inventory']
            return inventory
        except:
            print('Ошибка: ', traceback.format_exc())
            return False

    def floppa_spawn(self, chat_id, user_id, floppa):
        try:
            print(chat_id)
            print(str(floppa.rarity))
            print(self.db.hget('FLOPPA_TYPES_LIST:rarity_types', str(floppa.rarity)))

            rarity_types = bytes.decode(self.db.hget('FLOPPA_TYPES_LIST:rarity_types', str(floppa.rarity))).split(' ')
            random_floppa = rarity_types[random.randint(0, len(rarity_types) - 1)]
            floppa.photo_url = bytes.decode(self.db.hget('FLOPPA_TYPES_LIST:'+random_floppa, 'photo_url'))
            user_info = json.loads(bytes.decode(self.db.hget('Profiles:'+str(chat_id), str(user_id))))
            if user_info['can_gacha']:
                user_info['can_gacha'] = False
                self.db.hset('Profiles:'+str(chat_id), str(user_id), json.dumps(user_info))
            else:
                return None
            return floppa
        except:
            print('Ошибка: ', traceback.format_exc())
            return False

    def add_floppa(self, chat_id, user_id, floppa):
        try:
            user_info = json.loads(bytes.decode(self.db.hget('Profiles:' + str(chat_id), str(user_id))))
            user_info['floppas'].append(floppa.convert_to_json())
            user_info['can_gacha'] = True
            self.db.hset('Profiles:' + str(chat_id), str(user_id), json.dumps(user_info))
            return True
        except:
            print('Ошибка: ', traceback.format_exc())
            return False

    def save_floppa(self, chat_id, user_id, floppa):
        try:
            user_info = json.loads(bytes.decode(self.db.hget('Profiles:' + str(chat_id), str(user_id))))
            user_info['saved_floppa'] = floppa.convert_to_json()
            self.db.hset('Profiles:' + str(chat_id), str(user_id), json.dumps(user_info))
        except:
            print('Ошибка: ', traceback.format_exc())
            return False

    def exchange_floppa(self, chat_id, user_id, squad_index):
        try:
            user_info = json.loads(bytes.decode(self.db.hget('Profiles:' + str(chat_id), str(user_id))))
            floppa = user_info['saved_floppa']
            if type(floppa) != int:
                user_info['floppas'][squad_index] = floppa
                user_info['can_gacha'] = True
                user_info['saved_floppa'] = 0
                self.db.hset('Profiles:' + str(chat_id), str(user_id), json.dumps(user_info))
                return True
            return False
        except:
            print('Ошибка: ', traceback.format_exc())
            return False

    def rename_floppa(self, chat_id, user_id, flop_index, name):
        try:
            user_info = json.loads(bytes.decode(self.db.hget('Profiles:' + str(chat_id), str(user_id))))
            user_info['floppas'][flop_index]['name'] = name
            self.db.hset('Profiles:' + str(chat_id), str(user_id), json.dumps(user_info))
            return True
        except:
            print('Ошибка: ', traceback.format_exc())
            return False

    def feed_floppa(self, chat_id, user_id, flop_index):
        try:
            user_info = json.loads(bytes.decode(self.db.hget('Profiles:' + str(chat_id), str(user_id))))
            feed_diff = (time.time() - user_info['floppas'][flop_index]['feed_time'])/3600
            if feed_diff < 5:
                return 5 - round(feed_diff, 2)
            if user_info['floppas'][flop_index]['hungry'] + DataBase.FEED_ONCE_VALUE <= 100:
                user_info['floppas'][flop_index]['hungry'] += DataBase.FEED_ONCE_VALUE
                user_info['floppas'][flop_index]['feed_time'] = time.time()
                self.db.hset('Profiles:' + str(chat_id), str(user_id), json.dumps(user_info))
                return True
            else:
                return 'Can not feed'
        except:
            print('Ошибка: ', traceback.format_exc())
            return False

    def hungry_all_floppas(self):
        try:
            chats = self.get_chats()
            for chat in chats:
                keys = self.db.hkeys('Profiles:'+chat)
                for key in keys:
                    print(chat, key)
                    user_info = json.loads(bytes.decode(self.db.hget('Profiles:' + chat, bytes.decode(key))))
                    for floppa in user_info['floppas']:
                        if floppa['hungry'] - DataBase.HUNGRY_ONCE_VALUE >= 0:
                            floppa['hungry'] -= DataBase.HUNGRY_ONCE_VALUE
                    self.db.hset('Profiles:' + chat, int(bytes.decode(key)), json.dumps(user_info))
        except:
            print('Ошибка: ', traceback.format_exc())
            return False

    def add_token(self, chat_id, user_id):
        try:
            user_info = json.loads(bytes.decode(self.db.hget('Profiles:' + str(chat_id), str(user_id))))
            rarity = user_info['saved_floppa']['rarity']
            has_any_token = False
            for stuff in user_info['inventory']:
                if isinstance(stuff, dict):
                    if 'token_'+str(rarity) in stuff.keys():
                        has_any_token = True
            if not has_any_token:
                user_info['inventory'].append({'token_'+str(rarity): 1})
            else:
                for stuff in user_info['inventory']:
                    if isinstance(stuff, dict):
                        if 'token_' + str(rarity) in stuff.keys():
                            stuff['token_'+str(rarity)] += 1
            user_info['can_gacha'] = True
            user_info['saved_floppa'] = 0
            self.db.hset('Profiles:' + str(chat_id), str(user_id), json.dumps(user_info))
            return True
        except:
            print('Ошибка: ', traceback.format_exc())
            return False

    def is_squad_full(self, chat_id, user_id):
        try:
            user_info = json.loads(bytes.decode(self.db.hget('Profiles:' + str(chat_id), str(user_id))))
            if len(user_info['floppas']) < 3:
                return False
            else:
                return True
        except:
            print('Ошибка: ', traceback.format_exc())
            return None

    def destroy_floppas(self, chat_id, user_id):
        try:
            user_info = json.loads(bytes.decode(self.db.hget('Profiles:' + str(chat_id), str(user_id))))
            user_info['floppas'].clear()
            self.db.hset('Profiles:' + str(chat_id), str(user_id), json.dumps(user_info))
            return True
        except:
            print('Ошибка: ', traceback.format_exc())
            return False
