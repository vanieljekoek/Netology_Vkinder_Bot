import os
import datetime
import json
import logging
import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id
from dotenv import load_dotenv
from utils.database import DatabaseConnect
from utils.buttons import create_keyboard

load_dotenv()

# Задаём уровень логов
log_dir = os.path.join(os.path.dirname(__file__), 'vkinder_Log')

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(filename=os.path.join(log_dir, 'debug.log'), level=logging.DEBUG,
                    # Формат - Время, Дата, событие, сообщение)
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

class VKinderBot:
    def __init__(self):
        self.group_auth = vk_api.VkApi(token=os.getenv('c_token'))
        self.user_auth = vk_api.VkApi(token=os.getenv('a_token'))
        self.longpoll = VkLongPoll(self.group_auth)
        # Добавляем клавиатуру
        self.keyboard = create_keyboard()
        self.database = DatabaseConnect(dbname=os.getenv('db_name'), user=os.getenv('user'), password=os.getenv('password'), host=os.getenv('host'), port=os.getenv('password'))
        self.search_offset = -1
    print('\U0001F916 "Vkinder" запущен!', 'Для прекращения работы бота нажмите CTRL + C', sep='\n')

    def run(self):
        self.database.create_table()
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                command = event.text.lower()
                sender = event.user_id
                # Ранний выход из функции. Обработчик любой другой команды кроме перечисленных
                if command not in ('привет', 'поиск', 'search', 'go', 'следующие', 'next', 'ещё'):
                    self.write_message(sender, 'Мне очень жаль, но результаты поиска будут очищены\nДо новых встреч\U0001F44B')
                    self.database.delete_table()
                    os.system('python ' + os.path.realpath(__file__))
                    continue

                elif command == 'привет':
                    # Процесс получения данных со страницы пользователя
                    info = self.user_auth.method('users.get', {'user_ids': sender, 'fields': 'first_name,last_name,sex,city,bdate'})
                    user_info = {
                        'id': info[0]['id'],
                        'first_name': info[0]['first_name'],
                        'last_name': info[0]['last_name'],
                        'sex': info[0]['sex'],
                        'city': info[0]['city'],
                        'bdate': info[0]['bdate'],
                    }
                    if user_info["city"] is None:
                        self.write_message(sender, f'Приветствую тебя, {user_info["first_name"]} {user_info["last_name"]}\n'
                                           f'Для продолжения работы с ботом, требуется указать свой город')
                        command = user_info["city"]
                    elif user_info["sex"] is None:
                        self.write_message(sender, f'Приветствую тебя, {user_info["first_name"]} {user_info["last_name"]}\n'
                                           f'Для продолжения работы с ботом, требуется уточнить Ваш пол.\n'
                                           f'направьте мне сообщение в формате "муж"  или "жен"')
                        if command != 'муж': user_info["sex"] = 1
                        user_info["sex"] = 2
                    elif user_info["bdate"] is None:
                        self.write_message(sender, f'Приветствую тебя, {user_info["first_name"]} {user_info["last_name"]}\n'
                                           f'Для продолжения работы с ботом, требуется указать дату Вашего рождения в формате DD.MM.YYYY')
                        command = user_info["bdate"]
                    else:
                        self.write_message(sender, f'Приветствую тебя, {user_info["first_name"]} {user_info["last_name"]}!\n'
                                           f'Я - бот знакомств в социальной сети ВК.\n'
                                           f'Готов помочь тебе найти интересных людей и, возможно, новых друзей или даже вторую половинку.\n\n'
                                           f'Давай начнем!\nПросто напиши мне "Поиск", чтобы увидеть первый результат, соответствующий твоим '
                                           f'предпочтениям.\nЕсли тебе понравится кто-то из них, я смогу предоставить тебе ссылку на страницу '
                                           f'пользователя и даже некоторые фотографии.\nС уважением,\nБот знакомств Vkinder \U0001F498', self.keyboard)

                # Обработка команды "Поиск" и вариаций   
                elif command in ('поиск', 'search', 'go'):
                    self.search_offset = 0
                    self.search_users(sender)
                # Обработка команды "Следующее" и вариаций    
                elif command in ('следующие', 'next', 'ещё'):
                    if self.search_offset > 0: self.search_users(sender)
                    self.write_message(sender,
                                        'Сперва воспользуйтесь поиском, нажав соответствующую кнопку или введя команду "Поиск"',
                                        self.keyboard)                      

                # Алгоритм проверки пользователей по БД
                elif hasattr(event, 'payload') and event.payload:
                    payload = json.loads(event.payload)
                    if 'vk_id' not in payload: self.write_message(event.user_id, f'Пользователь {vk_url} был показан Вам ранее')
                    vk_id = payload['vk_id']
                    vk_url = payload['vk_url']
                    if not self.database.check_vk_users(vk_id):
                        self.database.save_vk_users(vk_id, vk_url)
                        self.write_message(event.user_id, f'Пользователь {vk_url} сохранен')
                            
    # Отправки Кандидатов пользователю
    def write_message(self, sender, message, keyboard=None, attachment=None):
        try:
            keyboard_data = keyboard.get_keyboard()
        except AttributeError:
            keyboard_data = None
        self.group_auth.method('messages.send',
                               {'user_id': sender, 'message': message, 'random_id': get_random_id(),
                                'keyboard': keyboard_data, 'attachment': attachment})
        
    # Функция поиска пользователей
    def search_users(self, sender):
        search_params = {'user_ids': sender, 'fields': 'bdate, sex, city'}
        user_info = self.user_auth.method('users.get', search_params)
        user_info = user_info[0]
        user_age = self.calculate_age(user_info['bdate'])
        user_sex = user_info['sex']
        user_city = user_info['city']['id']

        try:
            search_response = self.user_auth.method(
                'users.search',
                {'count': 1000,
                'city': user_city,
                'sex': 1 if user_sex == 2 else 2,
                'status': 0,
                'status_list': [1, 6],
                'age_from': user_age,
                'age_to': user_age,
                'has_photo': 1,
                'fields': 'photo_max_orig, screen_name',
                'offset': self.search_offset})

        except vk_api.exceptions.ApiError as e:
            self.write_message(sender, f'Произошла ошибка при поиске пользователей: {e}', self.keyboard)
            return

        for user in search_response['items']:
            vk_id = user['id']
            vk_url = f'https://vk.com/{user["screen_name"]}'
            user_info = self.user_auth.method('users.get', {'user_ids': vk_id, 'fields': 'is_closed, first_name, last_name, online, last_seen'})
            if not user_info: continue
            if user_info[0]['is_closed']: continue
            if self.database.check_vk_users(vk_id):continue
            photos = self.get_top_photos(user)
            message = (f'Знакомься, это - {user_info[0]["first_name"]} {user_info[0]["last_name"]}\nСсылочка на страницу пользователя: {vk_url}\n'
            f'В последний раз пользователь был онлайн: {datetime.datetime.fromtimestamp(user_info[0]["last_seen"]["time"]).strftime("%d-%m-%Yг. в %H:%M")}'
            f'\n\nА вот лучшие фото со страницы \U0001f929')
            self.write_message(sender, message, self.keyboard)
                
            attachment = []
            for photo in photos:
                attachment.append(f"photo{photo['owner_id']}_{photo['id']}")
            self.write_message(sender, '', self.keyboard, attachment=','.join(attachment))
            self.database.save_vk_users(vk_id, vk_url)
            break
        self.search_offset+=10
        
    def calculate_age(self, bdate):
        if bdate:
            bdate = datetime.datetime.strptime(bdate, '%d.%m.%Y')
            how_old = datetime.datetime.now().year - bdate.year
            if datetime.datetime.now().month < bdate.month or (
                    datetime.datetime.now().month == bdate.month
                    and datetime.datetime.now().day < bdate.day):
                age = min(max(how_old - 1, how_old - 1), how_old + 1)
            return age
    # Функция получения ТОП5 Фото со страницы кандидата по количеству лайков и комментариев
    def get_top_photos(self, user):
        photos_response = self.user_auth.method('photos.get', {'owner_id': user['id'], 'album_id': 'profile', 'rev': 1,
                                                               'count': 5, 'extended': 1, 'photo_sizes': 1})
        photos_data = []
        for photo in photos_response['items']:
            sizes = photo['sizes']
            likes = photo['likes']['count']
            comments = photo['comments']['count']
            photo_data = {'sizes': sizes, 'likes': likes, 'comments': comments, 'owner_id': photo['owner_id'],
                          'id': photo['id']}
            photos_data.append(photo_data)
        photos_data = sorted(photos_data, key=lambda x: (x['likes'], x['comments']), reverse=True)[:5]
        return photos_data

    def del_table(self):
        self.database.delete_table()
        self.database.disconnect()

bot = VKinderBot()
bot.run()