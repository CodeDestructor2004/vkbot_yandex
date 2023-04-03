# Импорт библиотек
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
import sqlite3
import datetime

# Токен группы. Для этого нужно включить API LongPoll в настройках группы
TOKEN = 'vk1.a.zznqAnSf5zEJJHzX6Y_5uMgrrzPghEFVfWmSL_SoYN2V9QqzxAmXe-18-1j9xOAYAFzG959KpwX6UGPRAVFWE6kwwJyskO3BDTfD6eo8aocXJ9yOZ6u_te5H5wci6PFLsNLybjY41UzodMBmorB8y-gVmBM47bEAsDQ1GSkecW2QDD9IbrsZMSiccZ52NtL8M0E_x5aBpmjlPa2h_6s-DQ'
# ID операторов бота. Эти люди имеют другой уровень доступа к функционалу бота.
OWNERS_IDS = ['267214029']
level = 0
data = []
# ВАЖНО! Проверьте, есть ли эта база данных в папке db. Запустите init_db.py для создания БД и таблицы.
con = sqlite3.connect('db/users.db')
cur = con.cursor()


# Функция перехода на другие уровни взаимодействия
def levels(act_id, message):
    global level
    global data
    if act_id == 0:
        if message.lower() == "оставить отзыв":
            level = 1
    elif act_id == 1:
        if message.isdigit():
            if 1 <= int(message) <= 10:
                level = 2
    elif act_id == 2:
        if message:
            level = 3


# Ввод-вывод данных в зависимости от уровня взаимодействия
def messages(act_id, message, vk, event):
    global level
    global data

    if act_id == 0:
        pass
    elif act_id == 1:
        if str(event.obj.message['from_id']) not in data:
            data.append(str(event.obj.message['from_id']))
        vk.messages.send(user_id=event.obj.message['from_id'],
                         message='Оцените качество контента от 1 до 10:',
                         random_id=random.randint(0, 2 ** 64))
    elif act_id == 2:
        if int(message) not in data:
            data.append(int(message))
        vk.messages.send(user_id=event.obj.message['from_id'],
                         message=f'Ваша оценка: {data[1]}',
                         random_id=random.randint(0, 2 ** 64))
        vk.messages.send(user_id=event.obj.message['from_id'],
                         message='Оставьте Ваши комментарии и пожелания к этой группе:',
                         random_id=random.randint(0, 2 ** 64))
    elif act_id == 3:
        data.append(message)
        vk.messages.send(user_id=event.obj.message['from_id'],
                         message=f'Ваш комментарий: {data[2]}',
                         random_id=random.randint(0, 2 ** 64))
        vk.messages.send(user_id=event.obj.message['from_id'],
                         message='Спасибо!',
                         random_id=random.randint(0, 2 ** 64))


# Основная программа
def main():
    global level
    global data
    # Подключение API
    vk_session = vk_api.VkApi(token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, 200364562)
    vk = vk_session.get_api()

    is_first_message = True
    # Цикл событий
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if str(event.obj.message['from_id']) in OWNERS_IDS:  # Если пользователь - оператор
                print(event)
                print('Новое сообщение:')
                print('Для меня от:', event.obj.message['from_id'])
                print('Текст:', event.obj.message['text'])
                if is_first_message is True:  # Если сообщение первое
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message='Привет! Вы являетесь одним из операторов этого бота. '
                                             '\nНапишите "Статистика" для получения статистики отзывов.'
                                             '\nНапишите "Отзыв <номер>" для получения информации об отзыве'
                                             'в хронологическом порядке (от нового к старому)',
                                     random_id=random.randint(0, 2 ** 64))
                    is_first_message = False
                else:  # Если сообщение не первое
                    if event.obj.message['text'].lower() == "статистика":  # Обработчик команды
                        rating_data = cur.execute("""SELECT rating FROM users""").fetchall()
                        length = len(rating_data)
                        mean = sum([int(i[0]) for i in rating_data]) / length
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message='Статистика:'
                                                 f'\nКоличество отзывов: {length}'
                                                 f'\nСредняя оценка: {mean}',
                                         random_id=random.randint(0, 2 ** 64))
                    if "отзыв" in event.obj.message['text'].lower():  # Обработчик команды
                        rating_data = cur.execute("""SELECT rating FROM users""").fetchall()
                        length = len(rating_data)
                        if len(event.obj.message['text'].split()) != 2:  # Проверки на корректность
                            pass
                        elif not event.obj.message['text'].split()[1].isdigit():
                            vk.messages.send(user_id=event.obj.message['from_id'],
                                             message='Неправильный формат команды',
                                             random_id=random.randint(0, 2 ** 64))
                        elif (int(event.obj.message['text'].split()[1]) < 1
                              or int(event.obj.message['text'].split()[1]) > length):
                            vk.messages.send(user_id=event.obj.message['from_id'],
                                             message='Неправильный формат команды',
                                             random_id=random.randint(0, 2 ** 64))
                        else:  # Если всё правильно введено
                            rating_data = cur.execute(f"""SELECT * FROM users
                                        LIMIT 1 OFFSET 
{int(event.obj.message['text'].split()[1]) - 1}""").fetchall()[0]
                            time = datetime.datetime.\
                                utcfromtimestamp(rating_data[3]).strftime("%Y-%m-%d %H:%M:%S")
                            vk.messages.send(user_id=event.obj.message['from_id'],
                                             message=f'id: @{rating_data[0]}'
                                                     f'\nОценка: {rating_data[1]}'
                                                     f'\nКомментарий: {rating_data[2]}'
                                                     f'\nВремя: {time} по МСК',
                                             random_id=random.randint(0, 2 ** 64))
            else:  # Если пользователь - не оператор
                print(event)
                print('Новое сообщение:')
                print('Для меня от:', event.obj.message['from_id'])
                print('Текст:', event.obj.message['text'])
                vk = vk_session.get_api()
                response = vk.users.get(user_id=event.obj.message['from_id'], fields=['first_name', 'city'])
                print(response)
                if is_first_message is True:  # Проверка на первое сообщение
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message='Привет! Оставить отзыв о контенте в '
                                             'этой группе можно, написав "Оставить отзыв".'
                                             'Его можно изменить, написав те же самые слова',
                                     random_id=random.randint(0, 2 ** 64))
                    user = cur.execute(f"""SELECT * FROM users
    WHERE user_id = {event.obj.message['from_id']}""").fetchall()  # Поиск пользователя в БД
                    if user:
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message='Вы уже оставляли свой отзыв. ',
                                         random_id=random.randint(0, 2 ** 64))
                    is_first_message = False
                else:  #
                    levels(level, event.obj.message['text'])  # Проверка ввода
                    print(level)
                    messages(level, event.obj.message['text'], vk, event)  # Ответ
                    if level == 3:  # Циклический сброс
                        obj = datetime.datetime.utcnow()
                        aware_obj = obj + datetime.timedelta(hours=3)
                        data.append(round(aware_obj.timestamp()))  # Получение времени по МСК в формате UNIX
                        data[2] = '"' + data[2] + '"'
                        print(data)
                        if user:  # Замена отзыва
                            cur.execute(f"""UPDATE users
    SET rating = {data[1]}, comment = {data[2]}, time = {data[3]}
    WHERE user_id = {data[0]}""").fetchall()
                        else:  # Добавление отзыва
                            cur.execute(f"INSERT INTO users VALUES(?, ?, ?, ?)", data)
                        con.commit()
                        is_first_message = True
                        data = []
                        level = 0


# Бесконечный цикл
if __name__ == '__main__':
    main()
# Закрытие БД после окончания сессии
con.close()
