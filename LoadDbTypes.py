import vk_api
import os
import redis

api = vk_api.VkApi(token='0e06ae540e06ae540e06ae543a0e7306b900e060e06ae5451e1a78dd9dae5d24e3cb1e4')
session = api.get_api()
db = redis.from_url(os.environ['REDIS_URL'])

needed_count = os.environ['needed_count']

photos = session.photos.get(owner_id=-202071018, album_id=277017085, rev=1, count=needed_count)['items']

for photo in photos:
    db.hset('FLOPPA_TYPES_LIST:'+str(photo['id']), 'rarity', photo['text'])
    db.hset('FLOPPA_TYPES_LIST:' + str(photo['id']), 'photo_url', photo['sizes'][-1]['url'])
    print(photo['text'])
    r_t = bytes.decode(db.hget('FLOPPA_TYPES_LIST:rarity_types', photo['text']))
    db.hset('FLOPPA_TYPES_LIST:rarity_types', photo['text'], r_t+' '+str(photo['id']))
    db.lpush('FLOPPA_TYPES_LIST:types', str(photo['id']))
