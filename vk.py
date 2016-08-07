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

        self.err = None

        self.login, self.password = '+375292082080', '1J2345S6789o0Pacan123N45s6t7A8h9A0m'
    
        self.db = open('db.txt', 'a+')
        # self.log = open('log.log', 'a')

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
        if sys.exc_info()[0] is not None or self.err is not None:
            logger.debug('EXCEPTION INFO : [{}]'.format(sys.exc_info()[0] if sys.exc_info()[0] else self.err))
            logger.debug('[FAILED] [%s]' % self._testMethodName)
            self.vk.messages.send(chat_id=4, message='Ошибка: {}'.format(sys.exc_info()[0] if sys.exc_info()[0]
                                                                         else self.err))
        else:

            logger.debug('Zatralleno')
            logger.debug('[PASSED] [%s]' % self._testMethodName)
            logger.debug('#################### End %s' % self._testMethodName)
            self.vk.messages.send(chat_id=4, message='Затраллено')

        # print('Затраллено', file=self.log)

        self.db.close()
        # self.log.close()



    def captcha_handler(self, captcha):

        # print('         Словил каптчу', file=self.log)
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
        # print('         Отправил сообщенько', file=self.log)
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
        # print('         Получил такой ключ: {}'.format(key), file=self.log)
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
                self.vk.messages.send(chat_id=4, message='Сейчас буду траллить лалку: https://vk.com/id{}'.format(person['id']))
                logger.debug("Now I'm going to tralling lalka: https://vk.com/id{}".format(person['id']))
                # print('Сейчас буду траллить лалку: https://vk.com/id{}'.format(person['id']), file=self.log)
                break

        with vk_api.VkRequestsPool(self.vk_session) as pool:
            # noinspection PyUnboundLocalVariable
            person_friends = pool.method_one_param('friends.get', key='user_id', values=[person['id']])

        friends = list(set().union(*(i['items'] for i in person_friends.values())))
        logger.debug('Number of friends: {}'.format(len(friends)))
        # print('    Количество друганов: {}'.format(len(friends)), file=self.log)

        with vk_api.VkRequestsPool(self.vk_session) as pool:
            # noinspection PyUnboundLocalVariable
            person_photos = pool.method('photos.getAll', {'owner_id': person['id'], 'photo_sizes': 0, 'no_service_albums': 0,
                                        'need_hidden': 0, 'skip_hidden': 0, 'count': 200})


        person_photos = person_photos['items']

        logger.debug('Number of photos: {}'.format(len(person_photos)))
        # print('    Количество фоток, которые я пролайкаю: {}'.format(len(person_photos)), file=self.log)

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
                        logger.debug('Like post of user: {}'.format(owner_id))
                        # print('        Поставил лайк юзеру {}'.format(owner_id), file=self.log)
                else:
                    logger.debug('User does not have posts: {}'.format(owner_id))
                    # print('        Нет записей у юзера {}'.format(owner_id), file=self.log)
            except:
                logger.debug('User is deleted: {}'.format(owner_id))
                # print('        Юзер удалён', owner_id, file=self.log)

        def like_all_photos(owner_id, photo_id):
            try:
                if not self.vk.likes.isLiked(owner_id=owner_id, item_id=photo_id, type='photo')['liked']:
                    self.vk.likes.add(owner_id=owner_id, item_id=photo_id, type='photo')
                    logger.debug('Like photo: {}'.format(photo_for_log(owner_id, photo_id)))
                    # print('        Поставил лайк юзеру {}, на фотку {}'.format(owner_id,
                    #                                                    photo_for_log(owner_id, photo_id)), file=self.log)

            except vk_api.vk_api.ApiError as error_msg:
                logger.debug(error_msg)
                self.err = error_msg
                raise Exception(error_msg)


        shuffle(friends)

        # pool = ThreadPool(cpu_count())
        # pool.map(like_last_post, friends)
        # pool.close()
        # pool.join()

        self.vk.messages.send(chat_id=4, message='Начал лайкать фотки')
        logger.debug('Starting liking photos')
        # print('    Начал лайкать фотки', file=self.log)


        for i in person_photos_ids:
            like_all_photos(person['id'], i)



        self.vk.messages.send(chat_id=4, message='Начал лайкать посты')
        logger.debug('Starting liking posts')
        # print('    Начал лайкать посты', file=self.log)

        for i in friends + [person['id']]:
            like_last_post(i)

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
