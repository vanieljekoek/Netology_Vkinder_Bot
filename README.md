# Netology_Vkinder_Bot
#### *Дипломный модуль профессии Python-разработка для начинающих по проекту «Цифровые профессии»*
___
## Задание:
### Входные данные

Имя пользователя или его id в ВК, для которого мы ищем пару.
если информации недостаточно нужно дополнительно спросить её у пользователя.

### Требования к сервису:

- Код программы удовлетворяет `PEP8`.
Получать токен от пользователя с нужными правами.
- Программа декомпозирована на функции/классы/модули/пакеты.
- Результат программы записывать в БД.
- Люди не должны повторяться при повторном поиске.
- Не запрещается использовать внешние библиотеки для vk.
### Дополнительные требования (не обязательны для получения диплома):

- В vk максимальная выдача при поиске 1000 человек. Подумать как это ограничение можно обойти.
- Добавить возможность ставить/убирать лайк, выбранной фотографии.
- Можно усложнить поиск добавив поиск по интересам. Разбор похожих интересов(группы, книги, музыка, интересы) нужно будет провести с помощью анализа текста.
- У каждого критерия поиска должны быть свои веса. То есть совпадение по возрасту должны быть важнее общих групп. Интересы по музыке важнее книг. Наличие общих друзей важнее возраста. И так далее.
- Добавлять человека в избранный список, используя БД.
- Добавлять человека в черный список чтобы он больше не попадался при поиске, используя БД.
- К списку фотографий из аватарок добавлять список фотографий, где отмечен пользователь.
---
## Реализовано:
- На основании информации о пользователе (пол, возраст, город) поиск партнёра противоположного пола с диапазоном +-5 лет от года рождения пользователя после отправки в чат текста **`Поиск`** или **`Search`**
- Запись 1000 найденных результатов в таблицу `found_users` БД PostgreSQL
- Отправка рандомных 10 варинтов из списка + 3 ТОП фотографии со страницы пользователя на основании количества лайков и комментариев под фото
- При отправке в чат команты **`Следующие`** или **`Next`** выполняется повторный поиск пользователей со смещением в 1000 результатов
- При отправке команды **`Пока`** или **`Buy`** пользователю в чат отправляется уведомление о том что результаты поиска будут очищены, таблица `found_users` удаляется
- Дебаг логирование в папку с местоположением кода бота - ***vkinder_log***, файл ***debug.log***

## Не реализовано:
- Показ функциональных REPLY кнопок, для упрощения взаимодействия с ботом
- Дополнительные условия выполнения дипломного проекта

## Найденные баги:
- Взаимодействие с ботом **всегда** начинается с отправки приветственного сообщения **`Привет`**. В случае отправки в чат другой команды, выполнение кода падает с ошибкой
- Мелкие функциональные баги
___
Скачать данный репозиторий можно выполнив команду `git clone https://github.com/vanieljekoek/Netology_Vkinder_Bot` у себя на компьютере
