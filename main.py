import random

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from environs import Env


def echo(event, vk_api):
    return vk_api.messages.send(
        user_id=event.user_id,
        message=event.message,
        random_id=random.randint(0, 1000)
    )


def vk_longpoll(vk_group_token):
    vk_session = vk.VkApi(token=vk_group_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            echo(event, vk_api)


def main():
    env = Env()
    env.read_env()
    vk_group_token = env.str('VK_GROUP_TOKEN')
    vk_longpoll(vk_group_token)


if __name__ == "__main__":
    main()