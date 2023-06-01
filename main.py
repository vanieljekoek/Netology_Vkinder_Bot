# Импортируем необходимые библиотеки и модули
import os
import datetime
import json
import logging
import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from dotenv import load_dotenv
from database import DatabaseConnect

#Загружаем переменные среды исполнения
load_dotenv()

# Задаём уровень логов
log_dir = os.path.join(os.path.dirname(__file__), 'vkinder_Log')    # Указание названия папки с логами

if not os.path.exists(log_dir):
    os.makedirs(log_dir)    # Создание папки с логами рядом с основным исполняемым кодом

# Задаём уровень логов (Уровень DEBUG - максимально подробный лог)
logging.basicConfig(filename=os.path.join(log_dir, 'debug.log'), level=logging.DEBUG,
                    # Формат - Время, Дата, событие, сообщение)
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Инициализация работы бота
class VKinderBot:
    def __init__(self):
        self.group_auth = vk_api.VkApi(token=os.getenv('c_token'))
        self.user_auth = vk_api.VkApi(token=os.getenv('a_token'))
        self.longpoll = VkLongPoll(self.group_auth)
        # Добавляем клавиатуру
        self.keyboard = VkKeyboard(one_time=True)
        self.keyboard.add_button('Поиск', color=VkKeyboardColor.POSITIVE)
        self.keyboard.add_button('Следующие', color=VkKeyboardColor.SECONDARY)
        self.keyboard.add_button('Пока', color=VkKeyboardColor.NEGATIVE)
        self.database = DatabaseConnect(dbname=os.getenv('db_name'), user=os.getenv('user'), password=os.getenv('password'), host=os.getenv('host'), port=os.getenv('password'))
        self.search_offset = -1
    print('\U0001F916 "Vkinder" запущен!', 'Для прекращения работы бота нажмите CTRL + C', sep='\n')

    # Функция запуска бота
    def run(self):
        self.database.create_table()
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                command = event.text.lower()
                sender = event.user_id
                # Обработчик любой другой команды кроме ...
                if command not in ('привет', 'поиск', 'search', 'go', 'следующие', 'next', 'ещё'):
                    self.write_message(sender, 'Мне очень жаль, но результаты поиска будут очищены\nДо новых встреч\U0001F44B')
                    self.del_table()
                    os.system('python ' + os.path.realpath(__file__))
                    continue
                # Обработка команды "Привет"
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
                    # Отправка приветственного сообщения
                    self.write_message(sender, f'''Приветствую тебя, {user_info["first_name"]} {user_info["last_name"]}!\nЯ - бот знакомств в социальной сети ВК.
Готов помочь тебе найти интересных людей и, возможно, новых друзей или даже вторую половинку.\n\nДавай начнем!
Просто напиши мне "Поиск", чтобы увидеть первых 10 пользователей, соответствующих твоим предпочтениям.
Если тебе понравится кто-то из них, я смогу предоставить тебе ссылку на страницу пользователя и даже некоторые фотографии.\n
С уважением,
Бот знакомств Vkinder \U0001F498''', self.keyboard)
                # Обработка команды "Поиск" и вариаций   
                elif command in ('поиск', 'search', 'go'):
                    self.search_offset = 0
                    self.search_users(sender)
                # Обработка команды "Следующее" и вариаций    
                elif command in ('следующие', 'next', 'ещё'):
                    if self.search_offset < 0:
                        self.write_message(sender, 'Сперва воспользуйтесь поиском, нажав соответствующую кнопку или введя команду "Поиск"',
                                           self.keyboard)
                    else:
                        self.search_users(sender)

                # Алгоритм проверки пользователей по БД
                elif hasattr(event, 'payload') and event.payload:
                    payload = json.loads(event.payload)
                    if 'vk_id' in payload:
                        vk_id = payload['vk_id']
                        vk_url = payload['vk_url']
                        if not self.database.check_vk_users(vk_id):
                            self.database.save_vk_users(vk_id, vk_url)
                            self.write_message(event.user_id, f'Пользователь {vk_url} сохранен')
                        else:
                            self.write_message(event.user_id, f'Пользователь {vk_url} был показан Вам ранее')

    # Функция отправки Кандидатов пользователю
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
        try:
            search_params = {'user_ids': sender, 'fields': 'bdate, sex, city'}
            user_info = self.user_auth.method('users.get', search_params)
            user_info = user_info[0]

        # Отправка сообщения пользователю, в случае неполной информации в профиле
        except vk_api.exceptions.ApiError as e:
            self.write_message(sender, f'Произошла ошибка при получении информации о пользователе: {e}', self.keyboard)
            return
        # сообщение с просьбой указать дату рождения
        if 'bdate' not in user_info:
            self.write_message(sender, 'Не удалось получить дату рождения пользователя. Укажите дату рождения в настройках вашего профиля.')
            return
        # Сообщение с просьбой выбрать пол пользователя
        if 'sex' not in user_info:
            self.write_message(sender, 'Не удалось получить пол пользователя. Укажите пол в настройках вашего профиля.')
            return
        # Сообщение с просьбой указать город проживания пользователя
        if 'city' == "" in user_info:
            self.write_message(sender, 'Не удалось получить информацию о городе. Укажите ваш город в настройках профиля.')
            return

        user_age = self.calculate_age(user_info['bdate'])
        user_sex = user_info['sex']
        user_city = user_info['city']['id']

        try:
            search_response = self.user_auth.method('users.search',
                                                    {'count': 30,
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
            if not user_info[0]['is_closed']:
                if self.database.check_vk_users(vk_id): continue
                photos = self.get_top_photos(user)
                message = f'''Знакомься, это - {user_info[0]["first_name"]} {user_info[0]["last_name"]}
Ссылочка на страницу пользователя: {vk_url}\n
В последний раз пользователь был онлайн:    {datetime.datetime.fromtimestamp(user_info[0]["last_seen"]["time"]).strftime("%d-%m-%Y %H:%M")}\n\n
А вот лучшие фото со страницы \U0001f929'''
                self.write_message(sender, message, self.keyboard)
                
                attachment = []
                for photo in photos:
                    attachment.append('photo{}_{}'.format(photo['owner_id'], photo['id']))
                self.write_message(sender, '', self.keyboard, attachment=','.join(attachment))
                self.database.save_vk_users(vk_id, vk_url)
                break
            else:
                self.write_message(sender, f'{user_info[0]["first_name"]} {user_info[0]["last_name"]}\n'
                                           f'Страница: {vk_url}\nПрофиль данного пользователя закрыт.\nДля доступа к странице, отправьте заявку на добавление в друзья \U0001F91D', self.keyboard)
                break


        self.search_offset += 30
        
    # Функция вычисления возраста пользователя
    def calculate_age(self, bdate):
        if bdate:
            bdate = datetime.datetime.strptime(bdate, '%d.%m.%Y')
            age = datetime.datetime.now().year - bdate.year
            if datetime.datetime.now().month < bdate.month or (
                    datetime.datetime.now().month == bdate.month
                    and datetime.datetime.now().day < bdate.day):
                age -= 1
            return age
    # Функция получения ТОП5 Фото
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
    
    # Функция удаления таблицы с пользователями
    def del_table(self):
        self.database.delete_table()
        self.database.disconnect()

bot = VKinderBot()
bot.__init__()
bot.run()