# -*- coding: utf-8 -*-

import vk_api
from random import shuffle, choice, randint
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count
import cpt
from time import sleep

import unittest
import sys

import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('main')


def excepthook(*args):
    logger.error('Uncaught exception:', exc_info=args)

"""
Примеры можно посмотреть здесь: https://github.com/python273/vk_api/tree/master/examples
VK API - здесь: https://new.vk.com/dev.php?method=methods
"""

class JsonStatham(unittest.TestCase):

    def setUp(self):

        self.login, self.password = '+375292082080', '1J2345S6789o0Pacan123N45s6t7A8h9A0m'
    
        self.db = open('db.txt', 'a+')

        tmp = ''
        for i in self.db:
            tmp += i
        self.people_in_db = tmp.rsplit('|')

        logger.debug('####################> Start %s' % self._testMethodName)
        self.vk_session = vk_api.VkApi(self.login, self.password, api_version='5.53', captcha_handler=self.captcha_handler)

        try:
            self.vk_session.authorization()
        except vk_api.AuthorizationError as error_msg:
            logger.debug(error_msg)
            self.err = error_msg
            raise Exception(error_msg)

        self.vk = self.vk_session.get_api()

    def tearDown(self):
        
        self.db.close()

    def run(self, result=None):

        unittest.TestCase.run(self, result)  # call superclass run method
        fail_method = [x[1].split('\n')[-2] for x in result.failures]
        error_method = [x[1].split('\n')[-2] for x in result.errors]
        print(error_method)
        if self._testMethodName in str(result.failures):
            logger.debug('EXCEPTION INFO : [{}]'.format(fail_method[-1]))
            logger.debug('[FAILED] [%s]' % self._testMethodName)
            self.vk.messages.send(chat_id=4, message='Ошибка: [{}]'.format(fail_method[-1]))
        elif self._testMethodName in str(result.errors):
            logger.debug('ERROR INFO : [{}]'.format(error_method[-1]))
            logger.debug('[ERROR] [%s]' % self._testMethodName)
            self.vk.messages.send(chat_id=4, message='Ошибка: {}'.format(error_method[-1]))
        else:
            logger.debug('[PASSED] [%s]' % self._testMethodName)
            logger.debug('Zatralleno')
            self.vk.messages.send(chat_id=4, message='Затраллено')

    def captcha_handler(self, captcha):
        logger.debug('Caught captcha')
        url = captcha.get_url()
        cpt.captcha_save(url)
        # key = input("Enter Captcha {0}: ".format(url)).strip()

        ask_for_help = choice(['Взломайте каптчу, плиз', 'Тут это... ваша помощь нужна', 'Взломайте, только побыстрее',
                               'Докажите, что вы лучше китайцев', 'А это смогёшь взломать?', 'Коооооооооть', 'Ну пазязя',
                               'Без тебя никак не обойтись', 'Купи слона',
                               'Эй, ребят, хватит трахаться, помогите взломать каптчу', 'Потом ипацца будите! Долг зовет!'])

        self.vk.messages.send(chat_id=4, message=ask_for_help)
        self.vk.messages.send(chat_id=4, message=url.replace('api.', ''))
        last_message_id = self.vk.messages.getHistory(count=1, offset=0, peer_id=2000000004)['items'][0]['id']
        logger.debug('Send message')
        answer = choice(['Спасибо, бро', 'Да пребудет с тобой сила', 'А она точно правильная?', 'Жизнь за Нерзула',
                         'Почему так долго? Лучше бы у китайцев попросил!', 'Не дано тебе разгадывать каптчи',
                         'А ты точно продюсер?', 'С меня поцелуй в щёчку', 'Век тебя не забуду... Ладно, шучу, забуду!'])

        while True:
            message = self.vk.messages.getHistory(count=1, offset=0, peer_id=2000000004)['items'][0]
            if message['id'] != last_message_id:
                self.vk.messages.send(chat_id=4, message=answer)
                break
            else:
                sleep(10)

        key = message['body']
        logger.debug('Get key: {}'.format(key))
        return captcha.try_again(key)


    def test_1_like_photos_and_posts(self):

        while True:
            persons = self.vk.users.search(count=1000, country=3, city=282, sex=1, status=6, age_from=18, age_to=25,
                                     online=1, has_photo=1)
            try:
                count = persons['count'] - 1
                person = persons['items'][randint(0, count)]
            except IndexError:
                continue
            if person['id'] not in self.people_in_db:
                self.vk.messages.send(chat_id=4, message='Сейчас буду траллить лалку: https://vk.com/id{}'
                                      .format(person['id']))
                logger.debug("Now I'm going to tralling lalka: https://vk.com/id{}".format(person['id']))
                break

        with vk_api.VkRequestsPool(self.vk_session) as pool:
            # noinspection PyUnboundLocalVariable
            person_friends = pool.method_one_param('friends.get', key='user_id', values=[person['id']])

        friends = list(set().union(*(i['items'] for i in person_friends.values())))
        logger.debug('Number of friends: {}'.format(len(friends)))

        with vk_api.VkRequestsPool(self.vk_session) as pool:
            # noinspection PyUnboundLocalVariable
            person_photos = pool.method('photos.getAll', {'owner_id': person['id'], 'photo_sizes': 0, 'no_service_albums': 0,
                                        'need_hidden': 0, 'skip_hidden': 0, 'count': 200})


        person_photos = person_photos['items']

        logger.debug('Number of photos: {}'.format(len(person_photos)))

        pool = ThreadPool(cpu_count())
        person_photos_ids = pool.map(lambda photo: photo['id'], person_photos)
        pool.close()
        pool.join()

        def photo_for_log(owner_id, photo_id):
            photo = self.vk.photos.getById(photos='{}_{}'.format(owner_id, photo_id))[0]
            max_sixe = max([int(i[6:]) for i in photo if 'photo_' in i])
            return photo['photo_{}'.format(max_sixe)]

        def like_last_post(owner_id):
            try:
                post = self.vk.wall.get(owner_id=owner_id, count=1)['items']
                if post:
                    post_id = post[0]['id']
                    if not self.vk.likes.isLiked(owner_id=owner_id, item_id=post_id, type='post')['liked']:
                        self.vk.likes.add(owner_id=owner_id, item_id=post_id, type='post')
                        logger.debug('Like post of user: https://vk.com/id{}'.format(owner_id))
                else:
                    logger.debug('User does not have posts: https://vk.com/id{}'.format(owner_id))
            except:
                if 'Flood' in sys.exc_info():
                    self.vk.messages.send(chat_id=4, message='Словил Flood. Попробую отправить пиздатую песню')
                    raise StopIteration
                else:
                    logger.debug('User is deleted: https://vk.com/id{}'.format(owner_id))

        def like_all_photos(owner_id, photo_id):
            if not self.vk.likes.isLiked(owner_id=owner_id, item_id=photo_id, type='photo')['liked']:
                self.vk.likes.add(owner_id=owner_id, item_id=photo_id, type='photo')
                logger.debug('Like photo: {}'.format(photo_for_log(owner_id, photo_id)))

        shuffle(friends)

        # pool = ThreadPool(cpu_count())
        # pool.map(like_last_post, friends)
        # pool.close()
        # pool.join()

        self.vk.messages.send(chat_id=4, message='Начал лайкать фотки')
        logger.debug('Starting liking photos')

        for i in person_photos_ids:
            like_all_photos(person['id'], i)

        self.vk.messages.send(chat_id=4, message='Начал лайкать посты')
        logger.debug('Starting liking posts')

        for i in [person['id']] + friends:
            try:
                like_last_post(i)
            except StopIteration:
                break

        song = self.vk.audio.search(q='Herr Антон – Одинокий мужчина в самом соку')['items'][0]

        try:
            self.vk.wall.post(owner_id=person['id'], from_group=0, attachments='audio{}_{}'.format(song['owner_id'],
                                                                                                   song['id']))
        except:
            logger.debug("Can't post song on the wall. Try to send message with song")
            self.vk.messages.send(chat_id=4, message='Доступ к стене закрыт. Попробую отправить песню сообщением')
            try:
                self.vk.messages.send(user_id=person['id'], attachment='audio{}_{}'.format(song['owner_id'],
                                                                                            song['id']))
            except:
                logger.debug("Can't send message with song. Sorry!")
                self.vk.messages.send(chat_id=4, message='Соррьки, но и сообщение с крутым треком данному пользователю'
                                                         ' я не могу отправить')

        print(person['id'], end='|', file=self.db)

if __name__ == "__main__":
    sys.excepthook = excepthook
    unittest.main(failfast=True)
