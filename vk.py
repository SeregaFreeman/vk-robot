import vk_api
from time import sleep
from random import randint, choice


def main():
    """ Пример отправки Jsony Stathomy рандомное сообщенько """

    login, password = 'login', 'password'
    vk_session = vk_api.VkApi(login, password)

    try:
        vk_session.authorization()
    except vk_api.AuthorizationError as error_msg:
        print(error_msg)
        return

    """
    Примеры можно посмотреть здесь: https://github.com/python273/vk_api/tree/master/examples
    VK API - здесь: https://new.vk.com/dev.php?method=methods
    """

    with vk_api.VkRequestsPool(vk_session) as pool:
        message = ''
        for i in range(randint(1, 10)):
            message += choice(['Syka', 'bliat', 'соси кирпичь', 'улыбашка', 'ti', 'жОпа', 'mamky ipal'])\
                    + choice([' ', ', '])

        pool.method('messages.send', {'oauth': '1', 'user_id': '376365095', 'message': message})

    with vk_api.VkRequestsPool(vk_session) as pool:
        json_friend = pool.method('friends.get', {'user_id': '376365095'})

    print(json_friend)

    if json_friend['items']:
        print(json_friend['items'])
    else:
        print('Ti odinokaia sychka')

if __name__ == '__main__':
    main()