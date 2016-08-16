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
        db = open('db.txt', 'a')
        db.close()
        self.db = open('db.txt', 'r+')

        tmp = ''
        for i in self.db:
            tmp += i
        self.people_in_db = [int(i) for i in tmp.replace('\n', '').rsplit('|')[:-1]]


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
        logger.debug('####################>  End  %s' % self._testMethodName)

    def run(self, result=None):

        unittest.TestCase.run(self, result)  # call superclass run method
        fail_method = [x[1].split('\n')[-2] for x in result.failures]
        error_method = [x[1].split('\n')[-2] for x in result.errors]
        if self._testMethodName in str(result.failures):
            print('@@@@@@@@@@@@@@@@@@', fail_method)
            logger.debug('EXCEPTION INFO : [{}]'.format(fail_method[-1]))
            logger.debug('[FAILED] [%s]' % self._testMethodName)
            self.vk.messages.send(chat_id=4, message='Ошибка: [{}]'.format(fail_method[-1]))
        elif self._testMethodName in str(result.errors):
            print('@@@@@@@@@@@@@@@@@@', error_method)
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
                sleep(5)

        key = message['body']
        logger.debug('Get key: {}'.format(key))
        return captcha.try_again(key)

    def like_last_post(self, owner_id):
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

    def photo_for_log(self, owner_id, photo_id):
        photo = self.vk.photos.getById(photos='{}_{}'.format(owner_id, photo_id))[0]
        max_size = max([int(i[6:]) for i in photo if 'photo_' in i])
        return photo['photo_{}'.format(max_size)]

    def like_all_photos(self, owner_id, photo_id):
        if not self.vk.likes.isLiked(owner_id=owner_id, item_id=photo_id, type='photo')['liked']:
            self.vk.likes.add(owner_id=owner_id, item_id=photo_id, type='photo')
            logger.debug('Like photo: {}'.format(self.photo_for_log(owner_id, photo_id)))


    def send_song(self, person_id, song_name='Herr Антон – Одинокий мужчина в самом соку', message=''):
        song = self.vk.audio.search(q=song_name)['items'][0]

        try:
            self.vk.wall.post(owner_id=person_id, from_group=0, attachments='audio{}_{}'.format(song['owner_id'],
                                                                                                   song['id']))
            if message:
                try:
                    self.vk.messages.send(user_id=person_id, message=message, sticker_id=21)
                except:
                    logger.debug("Post song on the wall. But can't send a message.")
                    self.vk.messages.send(chat_id=4, message='Кинул песню на стенку. Но не могу отправить сообщение')
        except:
            logger.debug("Can't post song on the wall. Try to send message with song")
            self.vk.messages.send(chat_id=4, message='Доступ к стене закрыт. Попробую отправить песню сообщением')
            try:
                self.vk.messages.send(user_id=person_id, attachment='audio{}_{}'.format(song['owner_id'], song['id']),
                                      message=message, sticker_id=21)
            except:
                logger.debug("Can't send message with song. Sorry!")
                self.vk.messages.send(chat_id=4, message='Соррьки, но и сообщение с крутым треком данному пользователю'
                                                         ' я не могу отправить')


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
        shuffle(friends)

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

        # pool = ThreadPool(cpu_count())
        # pool.map(like_last_post, friends)
        # pool.close()
        # pool.join()

        self.vk.messages.send(chat_id=4, message='Начал лайкать фотки')
        logger.debug('Starting liking photos')

        for i in person_photos_ids:
            self.like_all_photos(person['id'], i)

        self.vk.messages.send(chat_id=4, message='Начал лайкать посты')
        logger.debug('Starting liking posts')

        for i in [person['id']] + friends:
            try:
                self.like_last_post(i)
            except StopIteration:
                break

        self.send_song(person['id'])

        print(person['id'], end='|', file=self.db)

    def test_2_like_for_like(self):

        notifications = self.vk.notifications.get(filters='likes')['items']

        if notifications:
            persons = [self.vk.users.get(user_ids=notification['feedback']['items'][0]['from_id'], fields='sex')[0]
                       for notification in notifications
                       if self.vk.users.get(user_ids=notification['feedback']['items'][0]['from_id'],
                                            fields='sex')[0]['sex'] == 1]

            for per in persons:
                if per['id'] not in self.people_in_db:
                    person = per
                    self.vk.messages.send(chat_id=4, message='Лайк за лайк лалке: https://vk.com/id{}'
                                          .format(person['id']))
                    logger.debug("Like for like for lalka: https://vk.com/id{}".format(person['id']))
                    break
            else:
                person = None
                self.vk.messages.send(chat_id=4, message='Всле лалки заттраленны')
                logger.debug('All lalks were tralled')

            if person:

                with vk_api.VkRequestsPool(self.vk_session) as pool:
                    # noinspection PyUnboundLocalVariable
                    person_photos = pool.method('photos.getAll',
                                                {'owner_id': person['id'], 'photo_sizes': 0, 'no_service_albums': 0,
                                                 'need_hidden': 0, 'skip_hidden': 0, 'count': 200})

                person_photos = person_photos['items']

                logger.debug('Number of photos: {}'.format(len(person_photos)))

                pool = ThreadPool(cpu_count())
                person_photos_ids = pool.map(lambda photo: photo['id'], person_photos)
                pool.close()
                pool.join()

                self.vk.messages.send(chat_id=4, message='Начал лайкать фотки')
                logger.debug('Starting liking photos')

                for i in person_photos_ids:
                    self.like_all_photos(person['id'], i)

                self.send_song(person['id'], message='Приветик', song_name='Герр Антон (Herr Anton) – Лысый Бэби')

                print(person['id'], end='|', file=self.db)

        else:
            logger.debug('No new notifications')
            self.vk.messages.send(chat_id=4, message='Нет новых уведомлений')


if __name__ == "__main__":
    sys.excepthook = excepthook
    with open('testing.out', 'a+') as file:
        unittest.main(testRunner=unittest.TextTestRunner(file), failfast=True)
