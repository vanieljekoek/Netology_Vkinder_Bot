import os
import logging
import vk_api
import random
import json
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from backend import VkTools
from database import DatabaseConnection
from dotenv import load_dotenv

load_dotenv()

# Import environment variables
community_token = os.getenv('c_token')
access_token = os.getenv('a_token')

# Set the log level
log_dir = os.path.join(os.path.dirname(__file__), 'vkinder_Log')

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(filename=os.path.join(log_dir, 'debug.log'), level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Initializing the bot
class BotInterface:
    def __init__(self, community_token, access_token):
        self.interface = vk_api.VkApi(token=community_token)
        self.api = VkTools(access_token)
        self.params = None
        self.keyboard = None
        print('VKinder Bot is Working')

    # Keyboard Add
    def message_send(self, user_id, message, attachment=None, keyboard=None):
        if keyboard is None:
            keyboard = {
                "one_time": False,
                "buttons": [[
                    {
                        "action": {
                            "type": "text",
                            "payload": "{\"button\": \"search\"}",
                            "label": "Поиск"
                        },
                        # White button
                        "color": "primary"
                    },
                    {
                        "action": {
                            "type": "text",
                            "payload": "{\"button\": \"next\"}",
                            "label": "Следующие"
                        },
                        # Green button
                        "color": "positive"
                    },
                    {
                        "action": {
                            "type": "text",
                            "payload": "{\"button\": \"bye\"}",
                            "label": "Пока"
                        },
                        # Red button
                        "color": "negative"
                    }
                ]],
            }

        self.interface.method('messages.send', {
            'user_id': user_id,
            'message': message,
            'attachment': attachment,
            'random_id': get_random_id(),
            'keyboard': json.dumps(keyboard)
        })

    # Event handler
    def event_handler(self):
        longpoll = VkLongPoll(self.interface)
        # Many featured users
        shown_users = set()

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                if command in ('привет', 'приветик', 'hello', 'шалом', 'салам', 'hi'):
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'''Приветствую тебя, {self.params["name"]}!\nЯ - бот знакомств в социальной сети ВК.
Готов помочь тебе найти интересных людей и, возможно, новых друзей или даже вторую половинку.\n\nДавай начнем!
Просто напиши мне "Поиск", чтобы увидеть первых 10 пользователей, соответствующих твоим предпочтениям.
Если тебе понравится кто-то из них, я смогу предоставить тебе ссылку на страницу пользователя и даже некоторые фотографии.\n
С уважением,
Бот знакомств Vkinder \U0001F498''')

                elif command in ('поиск', 'search', 'следующие', 'next', 'go', 'давай', 'далее', 'поехали', 'ещё'):
                    connection = DatabaseConnection.connect_to_database()
                    DatabaseConnection.create_table_found_users(connection)
                    users = random.sample(self.api.search_users(self.params), 10)
                    num_user = 0

                    while users and num_user < 10:
                        user = users.pop()
                        vk_id = str(user["id"])
                        if vk_id not in shown_users:
                            shown_users.add(vk_id)
                            num_user += 1
                            # Checking if a user exists in the DB
                            if DatabaseConnection.check_found_users(connection, vk_id):
                                self.message_send(event.user_id, f"{user['name']} уже есть в базе данных.")
                            else:
                                # Adding new users to the DB
                                DatabaseConnection.insert_data_found_users(connection, vk_id, 0)
                                photos_user = self.api.get_photos(user['id'])
                                attachment = ''
                                for num, photo in enumerate(photos_user):
                                    attachment += f'photo{photo["owner_id"]}_{photo["id"]},'
                                    if num == 2:
                                        break
                                self.message_send(event.user_id,
                                                  f'''Знакомься, это - {user["name"]} \n
А вот ссылочка на страницу пользователя: https://vk.com/id{user["id"]}''',
                                                  attachment=attachment
                                                  )
                    DatabaseConnection.disconnect_from_database(connection)
                
                elif command in ('пока', 'bye'):
                    self.message_send(event.user_id, 'Мне очень жаль, но результаты поиска будут очищены\nДо новых встреч\U0001F44B')
                    connection = DatabaseConnection.connect_to_database()
                    DatabaseConnection.remove_table_found_users(connection)
                    DatabaseConnection.disconnect_from_database(connection)
                else:
                    self.message_send(event.user_id, 'Неверная команда')

if __name__ == '__main__':
    bot = BotInterface(community_token, access_token)
    bot.event_handler()