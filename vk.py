import vk_api
from  random import shuffle
from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing as mp
from time import sleep

def captcha_handler(captcha):

    key = ' '
    # key = input("Enter Captcha {0}: ".format(captcha.get_url())).strip()
    print(key)

    return captcha.try_again(key)

people = [50264756, 9375156]

login, password = '+375292082080', '1J2345S6789o0Pacan123N45s6t7A8h9A0m'
vk_session = vk_api.VkApi(login, password, api_version='5.53', captcha_handler=captcha_handler)

try:
    vk_session.authorization()
except vk_api.AuthorizationError as error_msg:
    print(error_msg)


vk = vk_session.get_api()


with vk_api.VkRequestsPool(vk_session) as pool:
    person_friends = pool.method_one_param('friends.get', key='user_id', values=people)


friends = list(set().union(*(i['items'] for i in person_friends.values())))

def like_last_post(owner_id):
    try:
        post = vk.wall.get(owner_id=owner_id, count=1)['items']
        if post:
            post_id = post[0]['id']
            vk.likes.add(owner_id=owner_id, item_id=post_id, type='post')
            print('Поставил лайк юсеру {}'.format(owner_id))
        else:
            pass
            print('Нет записей у юсера {}'.format(owner_id))
    except:
        print('Капча или юхер удалён', owner_id)
        sleep(60)

shuffle(friends)

pool = ThreadPool(mp.cpu_count())
pool.map(like_last_post, friends)
pool.close()
pool.join()


