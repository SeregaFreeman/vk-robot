# -*- coding: utf-8 -*-

import vk_api
from random import shuffle, choice, randint
from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing as mp
import cpt
from time import sleep


"""
Примеры можно посмотреть здесь: https://github.com/python273/vk_api/tree/master/examples
VK API - здесь: https://new.vk.com/dev.php?method=methods
"""


login, password = '+375292082080', '1J2345S6789o0Pacan123N45s6t7A8h9A0m'

db = open('db.log', 'a+')
log = open('log.log', 'a')

tmp = ''
for i in db:
    tmp += i

people_in_db = tmp.rsplit('|')

def captcha_handler(captcha):

    print(u'         Словил каптчу'.encode('utf-8'), file=log)
    url = captcha.get_url()
    cpt.captcha_save(url)
    # key = input("Enter Captcha {0}: ".format(url)).strip()

    ask_for_help = choice(['Взломайте каптчу, плиз', 'Тут это... ваша помощь нужна', 'Взломайте, только побыстрее',
                           'Докажите, что вы лучше китайцев', 'А это смогёшь взломать?', 'Коооооооооть', 'Ну пазязя',
                           'Без тебя никак не обойтись', 'Купи слона',
                           'Эй, ребят, хватит трахаться, помогите взломать каптчу', 'Потом ипацца будите! Долг зовет!'])

    vk.messages.send(chat_id=4, message=ask_for_help)
    vk.messages.send(chat_id=4, message=url.replace('api.', ''))
    last_message_id = vk.messages.get(count=1, bool=0, offset=0)['items'][0]['id']
    print(u'         Отправил сообщенько'.encode('utf-8'), file=log)

    answer = choice(['Спасибо, бро', 'Да пребудет с тобой сила', 'А она точно правильная?', 'Жизнь за Нерзула',
                     'Почему так долго? Лучше бы у китайцев попросил!', 'Не дано тебе разгадывать каптчи',
                     'А ты точно продюсер?', 'С меня поцелуй в щёчку', 'Век тебя не забуду... Ладно, шучу, забуду!'])

    while True:
        message = vk.messages.get(count=1, bool=0, offset=0)['items'][0]
        if message['id'] != last_message_id:
            vk.messages.send(chat_id=4, message=answer)
            break
        else:
            sleep(10)

    key = message['body']
    print(u'         Получил такой ключ: {}'.format(key).encode('utf-8'), file=log)
    return captcha.try_again(key)


vk_session = vk_api.VkApi(login, password, api_version='5.53', captcha_handler=captcha_handler)

try:
    vk_session.authorization()
except vk_api.AuthorizationError as error_msg:
    print(error_msg)


vk = vk_session.get_api()

while True:
    persons = vk.users.search(count=1000, country=3, city=282, sex=1, status=6, age_from=18, age_to=25,
                             online=1, has_photo=1)
    try:
        count = persons['count'] - 1
        person = persons['items'][randint(0, count)]
    except IndexError:
        continue
    if person['id'] not in people_in_db:
        print(str(person['id']).encode('utf-8'), end='|', file=db)
        vk.messages.send(chat_id=4, message='Сейчас буду траллить лалку: https://vk.com/id{}'.format(person['id']))
        print(u'Сейчас буду траллить лалку: https://vk.com/id{}'.format(person['id']).encode('utf-8'), file=log)
        break

with vk_api.VkRequestsPool(vk_session) as pool:
    # noinspection PyUnboundLocalVariable
    person_friends = pool.method_one_param('friends.get', key='user_id', values=[person['id']])

friends = list(set().union(*(i['items'] for i in person_friends.values())))
print(u'    Количество друганов: {}'.format(len(friends)).encode('utf-8'), file=log)

with vk_api.VkRequestsPool(vk_session) as pool:
    # noinspection PyUnboundLocalVariable
    person_photos = pool.method('photos.getAll', {'owner_id': person['id'], 'photo_sizes': 0, 'no_service_albums': 0,
                                'need_hidden': 0, 'skip_hidden': 0, 'count': 200})


person_photos = person_photos['items']

print(u'    Количество фоток, которые я пролайкаю: {}'.format(len(person_photos)).encode('utf-8'), file=log)

pool = ThreadPool(mp.cpu_count())
person_photos_ids = pool.map(lambda photo: photo['id'], person_photos)
pool.close()
pool.join()

def photo_for_log(owner_id, photo_id):
    photo = vk.photos.getById(photos='{}_{}'.format(owner_id, photo_id))[0]
    max_sixe = max([int(i[6:]) for i in photo if 'photo_' in i])
    return photo['photo_{}'.format(max_sixe)]



def like_last_post(owner_id):
    try:
        post = vk.wall.get(owner_id=owner_id, count=1)['items']
        if post:
            post_id = post[0]['id']
            if not vk.likes.isLiked(owner_id=owner_id, item_id=post_id, type='post')['liked']:
                vk.likes.add(owner_id=owner_id, item_id=post_id, type='post')
                print(u'        Поставил лайк юзеру {}'.format(owner_id).encode('utf-8'), file=log)
        else:
            print(u'        Нет записей у юзера {}'.format(owner_id).encode('utf-8'), file=log)
    except:
        print(u'        Юзер удалён'.encode('utf-8'), owner_id, file=log)

def like_all_photos(owner_id, photo_id):
    if not vk.likes.isLiked(owner_id=owner_id, item_id=photo_id, type='photo')['liked']:
        vk.likes.add(owner_id=owner_id, item_id=photo_id, type='photo')
        print(u'        Поставил лайк юзеру {}, на фотку {}'.format(owner_id,
                                                           photo_for_log(owner_id, photo_id)).encode('utf-8'), file=log)


shuffle(friends)

# pool = ThreadPool(mp.cpu_count())
# pool.map(like_last_post, friends)
# pool.close()
# pool.join()

vk.messages.send(chat_id=4, message='Начал лайкать фотки')
print(u'    Начал лайкать фотки'.encode('utf-8'), file=log)

for i in person_photos_ids:
    like_all_photos(person['id'], i)

vk.messages.send(chat_id=4, message='Начал лайкать посты')
print(u'    Начал лайкать посты'.encode('utf-8'), file=log)

for i in friends + [person['id']]:
    like_last_post(i)


vk.messages.send(chat_id=4, message='Затраллено')
print(u'Затраллено'.encode('utf-8'), file=log)

db.close()
log.close()