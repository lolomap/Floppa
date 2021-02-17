# -*- coding: utf-8 -*-

import random
import time


class Floppa:
    def __init__(self, hungry, petted, damage, flopping, hiss, size, name, rarity, photo_url,  feed_time=None):
        self.hungry = hungry
        self.petted = petted
        self.damage = damage
        self.flopping = flopping
        self.hiss = hiss
        self.size = size
        self.name = name
        self.rarity = rarity
        self.photo_url = photo_url
        if feed_time is None:
            self.feed_time = time.time()
        else:
            self.feed_time = feed_time

    def rarity_star(self):
        result = '★' * self.rarity
        return result

    def rename(self, name):
        self.name = name

    def convert_to_message(self):
        result = {'text': self.rarity_star() + '\n'
                  + 'Имя: ' + self.name + '\n'
                  + 'Сытость:' + str(self.hungry) + '\n'
                  + 'Поглаженность: ' + str(self.petted) + '\n'
                  + 'Сила укуса: ' + str(self.damage) + '\n'
                  + 'Скорость Flopping: ' + str(self.flopping) + '\n'
                  + 'Толстость: ' + str(self.size) + '\n'
                  + 'Громкость шипения: ' + str(self.hiss) + '\n'
                  + 'Была покормленна ' + str(round((time.time() - self.feed_time)/3600, 2)) + ' часов назад',
                  'photo_url': self.photo_url}
        return result

    def convert_to_json(self):
        result =\
            {
                'hungry': self.hungry,
                'petted': self.petted,
                'damage': self.damage,
                'flopping': self.flopping,
                'hiss': self.hiss,
                'size': self.size,
                'name': self.name,
                'rarity': self.rarity,
                'photo_url': self.photo_url,
                'feed_time': self.feed_time
            }
        return result

    @staticmethod
    def gacha_roll():
        damage = 0
        flopping = 0
        hiss = 0
        size = 0
        rarity = random.randint(1, 101)

        if rarity == 1:
            rarity = 5
        elif rarity <= 5:
            rarity = 4
        elif rarity <= 20:
            rarity = 3
        elif rarity <= 50:
            rarity = 2
        elif rarity > 50:
            rarity = 1

        if random.randint(0, 1000000) == 1:
            rarity = 10

        if rarity == 1:
            damage = random.randint(5, 15)
            flopping = random.randint(8, 15)
            hiss = random.randint(5, 15)
            size = random.randint(12, 25)
        elif rarity == 2:
            damage = random.randint(12, 25)
            flopping = random.randint(10, 20)
            hiss = random.randint(15, 35)
            size = random.randint(18, 25)
        elif rarity == 3:
            damage = random.randint(23, 35)
            flopping = random.randint(18, 43)
            hiss = random.randint(20, 35)
            size = random.randint(20, 35)
        elif rarity == 4:
            damage = random.randint(35, 50)
            flopping = random.randint(35, 45)
            hiss = random.randint(35, 45)
            size = random.randint(35, 45)
        elif rarity == 5:
            damage = random.randint(55, 70)
            flopping = random.randint(55, 70)
            hiss = random.randint(55, 70)
            size = random.randint(55, 70)
        elif rarity == 10:
            damage = 1000
            flopping = 1000
            hiss = 1000
            size = 1000

        floppa = Floppa(100, 100, damage, flopping, hiss, size, "Флоппа", rarity, "")

        return floppa
