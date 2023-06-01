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
- На основании информации о пользователе (пол, возраст, город) выполняется поиск партнёра противоположного пола с диапазоном плюс-минус 1 год от возраста пользователя, после отправки в чат текста **`Поиск`** (или нажатия соответствующей кнопки) или **`Search`**
- Запись 30 найденных результатов в таблицу `vk_users` БД PostgreSQL
- Отправка информации о рандомном пользователе (Фамилия, Имя, ссылка на страницу в VK) из списка + 5 ТОП фотографии со страницы пользователя на основании количества лайков и комментариев под фото
- При отправке в чат команты **`Следующие`** (или нажатии соответствующей кнопки) или повторной отправки команды **`Поиск`** выполняется выдача следующего радомного пользователя из списка
- При отправке команды **`Пока`** или **`Buy`** пользователю в чат отправляется уведомление о том что результаты поиска будут очищены, таблица `found_users` удаляется
- Дебаг логирование в папку с местоположением кода бота - ***vkinder_log***, файл ***debug.log***
- Добавлены функцинальные кнопки, для упрощения взаимодействия с ботом. Код кнопок перенесён в файл **main.py**
- Смещение значения OFFSET на 30 при каждом запуске функции поиска пользователей

## Не реализовано:
- ~~Показ функциональных REPLY кнопок, для упрощения взаимодействия с ботом~~ **(РЕАЛИЗОВАНО)**
- Дополнительные условия выполнения дипломного проекта

## Найденные баги:
- ~~Взаимодействие с ботом **всегда** начинается с отправки приветственного сообщения **`Привет`**. В случае отправки в чат другой команды, выполнение кода падает с ошибкой (**Такова логика работы бота**, можно подумать в будущем как изменить)~~ (**FIX IT**)
- ~~После удаления таблицы `found_users` и повторении выполнения действий по поиску партнёра, выдаются те же результаты поиска, в той же последовательности.~~ (**FIX IT**)
- Функциональные баги связанные с однопользователським режимом работы бота. Например: При одновременном подключении 2ух пользователей, пользователю 2 будут выдаваться результаты поиска по параметрам пользователя 1. (Для того чтоб пофиксить, необходимо переписать код бота используя асинхронные библиотеки, например ***asyncio***) 
___
Скачать данный репозиторий можно выполнив команду `git clone https://github.com/vanieljekoek/Netology_Vkinder_Bot` у себя на компьютере
