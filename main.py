import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from environs import Env


def vk_longpoll(vk_group_token):
    vk_session = vk_api.VkApi(token=vk_group_token)
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            print('Новое сообщение:')
            if event.to_me:
                print(f'Для меня от {event.user_id}')
            else:
                print(f'От меня для: {event.user_id}')
            print(f'Текст: {event.text}')


def main():
    env = Env()
    env.read_env()
    vk_group_token = env.str('VK_GROUP_TOKEN')
    vk_longpoll(vk_group_token)


if __name__ == "__main__":
    main()