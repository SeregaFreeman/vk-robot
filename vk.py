import vk_api
from random import randint, choice


def main():
    """ Пример отправки Jsony Stathomy рандомное сообщенько и возврата id друзей профиля"""

    login = input('Введи логин: ')
    password = input('Введи пароль: ')
    vk_session = vk_api.VkApi(login, password, api_version='5.53')

    try:
        vk_session.authorization()
    except vk_api.AuthorizationError as error_msg:
        print(error_msg)
        return

    """
    Примеры можно посмотреть здесь: https://github.com/python273/vk_api/tree/master/examples
    VK API - здесь: https://new.vk.com/dev.php?method=methods
    """
    vk = vk_session.get_api()

    user = vk.users.get()[-1]

    print(user)

    '''Просто способ работы с api
    '''

    vk.messages.send(user_id='376365095', message='HI LOLKA')
    print(vk.friends.get(user_id=user['id'])['items'])

    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

    '''Далее рабочий код, но он работает после подправки файла vk_tools.py (259 строка):
    for x in range(len(response)):
                if self.one_param:
                    if response[x] is False:
                        self.one_param['return'][cur_pool[x]] = {'_error': True}
                    else:
                        self.one_param['return'][cur_pool[x]] = response[x]
                else:
                    if response[x] is False:
                        self.pool[i + x][2].update({'_error': True})
                    elif type(response[x]) is list:
                        self.pool[i + x][2].update({'list': response[x]})
                    else:
                        if type(response[0]) is int:
                            self.pool[i + x][2].update()
                        else:
                            self.pool[i + x][2].update(response[x])
    '''

    with vk_api.VkRequestsPool(vk_session) as pool:
        message = ''
        for i in range(randint(1, 10)):
            message += choice(['Syka', 'bliat', 'соси кирпичь', 'улыбашка', 'ti', 'жОпа', 'mamky ipal'])\
                    + choice([' ', ', '])

        pool.method('messages.send', {'oauth': '1', 'user_id': '376365095', 'message': message})

    with vk_api.VkRequestsPool(vk_session) as pool:
        friends = pool.method('friends.get', {'user_id': user['id']})

    if friends['items']:
        print(friends['items'])
    else:
        print('Ti odinokaia sychka')

if __name__ == '__main__':
    main()