# -*- coding: utf-8 -*-

import VkApi
from DataBaseApi import DataBase
import Floppas
import json
import asyncio

redis_db = DataBase()


async def update_feed_petted():
    print('Hungry loop started')
    while True:
        await asyncio.sleep(3600*4)
        print('Hungry all floppas')
        redis_db.hungry_all_floppas()


async def process_message(session, event, chat_ide, user_ide):
    print('Processing message')
    msg_text = event.obj.message['text'].lower()
    if msg_text == 'запускайте флопп':
        users = VkApi.get_chat_users(event.obj.message, session)
        redis_db.init_new_profiles(users, event.obj.message['peer_id'])
        VkApi.send_message('Профили участников беседы сброшены', session, event)
    elif msg_text == 'мои флоппы' or msg_text == 'vjb akjggs':
        user_floppas = redis_db.get_user_floppas(chat_ide, user_ide)
        if not user_floppas:
            VkApi.send_floppa_info(None, session, event)
            return
        if len(user_floppas) == 0:
            VkApi.send_floppa_info(None, session, event)
        else:
            for user_floppa in user_floppas:
                VkApi.send_floppa_info(user_floppa.convert_to_message(), session, event)
    elif msg_text == 'крутить гачу' or msg_text == 'rhenbnm ufxe':
        floppa = Floppas.Floppa.gacha_roll()

        msg = redis_db.floppa_spawn(chat_ide, user_ide, floppa)
        if msg is None:
            VkApi.send_message('Вы еще не завершили прошлую прокрутку', session, event)
        elif msg:
            VkApi.send_floppa_info(msg.convert_to_message(),
                                   session, event)
            is_full = redis_db.is_squad_full(chat_ide, user_ide)
            if is_full is not None:
                if not is_full:
                    redis_db.add_floppa(chat_ide, user_ide, msg)
                else:
                    redis_db.save_floppa(chat_ide, user_ide, floppa)
                    VkApi.send_exchange_menu(session, event)
            else:
                VkApi.send_message('Вы еще не в клубе флопп', session, event)
        else:
            VkApi.send_message('Вы еще не в клубе флопп', session, event)
    elif 'я' in msg_text and msg_text.startswith('@flopbot'):
        if 'payload' not in event.obj.message.keys():
            return
        if 'fid' in json.loads(event.obj.message['payload']).keys():
            if redis_db.exchange_floppa(chat_ide, user_ide,
                                        int(json.loads(event.obj.message['payload'])['fid']) - 1):
                VkApi.send_message('Успешно', session, event)
            else:
                VkApi.send_message('Ошибка', session, event)
        elif 'feed' in json.loads(event.obj.message['payload']).keys():
            is_feeded = redis_db.feed_floppa(chat_ide, user_ide,
                                             int(json.loads(event.obj.message['payload'])['feed']) - 1)
            if is_feeded == 'Can not feed':
                VkApi.send_message('Эта флоппа сыта', session, event)
                return
            if type(is_feeded) == int or type(is_feeded) == float:
                VkApi.send_message('Вы сможете покормить флоппу через ' + str(is_feeded) + ' часов', session,
                                   event)
                return
            if is_feeded:
                VkApi.send_message('Успешно', session, event)
            else:
                VkApi.send_message('Ошибка', session, event)
        elif 'rename' in json.loads(event.obj.message['payload']).keys():
            if redis_db.rename_floppa(chat_ide, user_ide,
                                      int(json.loads(event.obj.message['payload'])['rename'][0]) - 1,
                                      json.loads(event.obj.message['payload'])['rename'][1]):
                VkApi.send_message('Успешно', session, event)
            else:
                VkApi.send_message('Ошибка', session, event)
    elif 'запечатать' in msg_text and msg_text.startswith('@flopbot'):
        if 'payload' not in event.obj.message.keys():
            return
        if json.loads(event.obj.message['payload'])['to_token']:
            if redis_db.add_token(chat_ide, user_ide):
                VkApi.send_message('Успешно', session, event)
            else:
                VkApi.send_message('Ошибка', session, event)
    elif msg_text == 'отпустить флопп':
        if redis_db.destroy_floppas(chat_ide, user_ide):
            VkApi.send_message('Флоппы ушли :(', session, event)
        else:
            VkApi.send_message('Вы еще не в клубе флопп', session, event)
    elif msg_text == 'покормить флопп' or msg_text == 'gjrjhvbnm akjgg':
        VkApi.request_feed(session, event)
        return
    elif 'дать имя флоппе:' in msg_text:
        VkApi.request_rename(session, event, event.obj.message['text'].split(':')[1])
        return
    elif msg_text == 'мой инвентарь' or msg_text == 'vjq bydtynfhm':
        inv = redis_db.get_user_inventory(chat_ide, user_ide)
        if inv:
            VkApi.send_inventory(inv, session, event)
        else:
            VkApi.send_message('Ошибка', session, event)
    elif msg_text == 'вступить в клуб флопп':
        redis_db.init_new_profile(chat_ide, user_ide)
        VkApi.send_message('Ваш профиль создан', session, event)
    elif msg_text.startswith('дуэль @'):
        data = event.obj.message['text'].split('@')[1]
        short_name = data.split(' ')[0]
        duel_user_id = VkApi.get_user_id(short_name, session)
        if redis_db.set_requested_duel(chat_ide, user_ide, duel_user_id, data.split(' ')[1]):
            VkApi.request_duel(session, event)
        else:
            VkApi.send_message('Ошибка', session, event)
    elif msg_text.startswith('дуэль принять '):
        flop_id = int(msg_text.split(' ')[2])
        winner = redis_db.accept_duel(chat_ide, user_ide, flop_id)
        if type(winner) == int:
            VkApi.send_duel_win(session, event, winner)
        elif winner == 'Draw':
            VkApi.send_message('Дуэль окончилась ничьей!', session, event)
        else:
            VkApi.send_message('Ошибка', session, event)
    elif msg_text == 'дуэль отклонить' or msg_text == 'le\'km jnrkjybnm':
        if redis_db.deny_duel(chat_ide, user_ide):
            VkApi.send_message('Дуэль отклоненна', session, user_ide)
        else:
            VkApi.send_message('Ошибка', session, event)


async def main():
    print('Bot started')
    vk = VkApi.create_session()
    session = vk['session']
    longpoll = vk['longpoll']
    for event in longpoll.listen():
        if VkApi.is_event_message(event.type) and event.from_chat:
            print('Message catched')
            chat_ide = event.obj.message['peer_id']
            user_ide = event.obj.message['from_id']
            await process_message(session, event, chat_ide, user_ide)


if __name__ == '__main__':
    while True:
        try:
            loop = asyncio.get_event_loop()
            asyncio.ensure_future(update_feed_petted())
            asyncio.ensure_future(main())
            loop.run_forever()
        except:
            pass
