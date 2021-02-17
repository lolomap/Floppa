# -*- coding: utf-8 -*-

import json
import os
import random

import requests

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def create_session():
    api = vk_api.VkApi(token=os.environ['TOKEN'])
    longpoll = VkBotLongPoll(api, os.environ['GROUP_ID'])
    session = api.get_api()
    print('session created')
    return {'session': session, 'longpoll': longpoll}


def get_photo_to_send(url, session, event):
    photo_file = session.photos.getMessagesUploadServer(peer_id=event.obj.message['peer_id'])
    r_data = {'photo': (str(random.randint(10, 100000)) + '.jpg', requests.get(url).content)}
    photo_data = requests.post(photo_file['upload_url'], files=r_data).json()
    photo = session.photos.saveMessagesPhoto(server=photo_data['server'],
                                             photo=photo_data['photo'],
                                             hash=photo_data['hash'])[0]
    return photo


def get_chat_users(msg, session):
    users = session.messages.getConversationMembers(peer_id=msg['peer_id'])
    profiles = []
    for user in users['profiles']:
        profiles.append(user['id'])
    return profiles


def send_floppa_info(floppa_msg, session, event):
    if floppa_msg is None:
        session.messages.send(peer_id=event.obj.message['peer_id'],
                              message='У [id' + str(event.obj.message['from_id']) + '|тебя] нет флопп :(',
                              random_id=random.randint(100000, 999999))
        return

    photo = get_photo_to_send(floppa_msg['photo_url'], session, event)
    session.messages.send(peer_id=event.obj.message['peer_id'],
                          message='[id' + str(event.obj.message['from_id']) + '|Твоя флоппа]\n\n' + floppa_msg['text'],
                          attachment='photo' + str(photo['owner_id']) + '_' + str(photo['id']),
                          random_id=random.randint(100000, 999999))


def send_inventory(inv_dict, session, event):
    inv_str = ''
    for item_dict in inv_dict:
        item = [list(item_dict.keys())[0], list(item_dict.values())[0]]
        if item[0] == 'token_1':
            inv_str += '📓 Шлёпки (1★): ' + str(item[1]) + '\n'
        elif item[0] == 'token_2':
            inv_str += '📘 Шлёпки (2★): ' + str(item[1]) + '\n'
        elif item[0] == 'token_3':
            inv_str += '📗 Шлёпки (3★): ' + str(item[1]) + '\n'
        elif item[0] == 'token_4':
            inv_str += '📔 Шлёпки (4★): ' + str(item[1]) + '\n'
        elif item[0] == 'token_5':
            inv_str += '📙 Шлёпки (5★): ' + str(item[1]) + '\n'
        elif item[0] == 'token_10':
            inv_str += '📕 Шлёпки (10★): ' + str(item[1]) + '\n'

    session.messages.send(peer_id=event.obj.message['peer_id'],
                          message='[id' + str(event.obj.message['from_id']) + '|Твой] инвентарь:\n\n' + inv_str,
                          random_id=random.randint(100000, 999999))


def send_exchange_menu(session, event):

    keyboard = VkKeyboard(inline=True)
    keyboard.add_button('1я', VkKeyboardColor.NEGATIVE, payload=json.dumps({'fid': 1}))
    keyboard.add_button('2я', VkKeyboardColor.POSITIVE, payload=json.dumps({'fid': 2}))
    keyboard.add_button('3я', VkKeyboardColor.PRIMARY, payload=json.dumps({'fid': 3}))
    keyboard.add_button('Запечатать', VkKeyboardColor.SECONDARY, payload=json.dumps({'to_token': True}))
    session.messages.send(peer_id=event.obj.message['peer_id'],
                          message='Ваш сквад полон! Выберете какую флоппу заменить',
                          random_id=random.randint(100000, 999999),
                          keyboard=keyboard.get_keyboard())


def request_feed(session, event):
    keyboard = VkKeyboard(inline=True)
    keyboard.add_button('1я', VkKeyboardColor.NEGATIVE, payload=json.dumps({'feed': 1}))
    keyboard.add_button('2я', VkKeyboardColor.POSITIVE, payload=json.dumps({'feed': 2}))
    keyboard.add_button('3я', VkKeyboardColor.PRIMARY, payload=json.dumps({'feed': 3}))
    session.messages.send(peer_id=event.obj.message['peer_id'],
                          message='Какую флоппу покормить?',
                          random_id=random.randint(100000, 999999),
                          keyboard=keyboard.get_keyboard())


def send_message(msg, session, event):
    session.messages.send(peer_id=event.obj.message['peer_id'],
                          message=msg,
                          random_id=random.randint(100000, 999999))


def is_event_message(event):
    if event == VkBotEventType.MESSAGE_NEW:
        return True
    else:
        return False
