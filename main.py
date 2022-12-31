import json
from random import randint, choice, shuffle
import pymorphy2
# api википедии
import wikipedia
# преобразование текста в аудио
from gtts import gTTS
import requests
from vk_api import VkApi
import datetime as dt
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import time


def photo(user_id, photo_cart):
    # отправляет фото в лс человеку
    vk.messages.send(
        user_id=user_id,
        random_id=randint(0, 1000000000),
        attachment=photo_cart
    )


def send_message_user(user_id, message):
    # отправка сообщений ботом в личные сообщения, прилагая кнопки
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Ещё карту", color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button("Достаточно!", color=VkKeyboardColor.POSITIVE)
    vk.messages.send(
        user_id=user_id,
        message=message,
        random_id=randint(0, 1000000000),
        keyboard=keyboard.get_keyboard(),
    )


# перевод из секунд в дату
def from_second_to_date(ts):
    return dt.datetime.utcfromtimestamp(ts)


# отправляет API запрос для погоды и преобразует его в удобную форму
def get_weather_days(num):
    api_key = '52d406bba24fd0df794d9978adcfc392'
    url = 'https://api.openweathermap.org/data/' \
          '2.5/onecall?lat=57.656520&lon=39.835397&lang=ru&exclude' \
          '=current&appid=' + api_key
    response = requests.get(url)
    weather = response.json()
    res_weather = {}
    for n in range(num):
        res_weather[str(n) + 'temp_evening'] = int(weather['daily'][n]['temp']['eve'] - 273.15)
        res_weather[str(n) + 'temp_morning'] = int(weather['daily'][n]['temp']['morn'] - 273.15)
        res_weather[str(n) + 'temp_night'] = int(weather['daily'][n]['temp']['night'] - 273.15)
        res_weather[str(n) + 'temp_afternoon'] = int(weather['daily'][n]['temp']['day'] - 273.15)
        res_weather[str(n) + 'feels_temp_evening'] = int(
            weather['daily'][n]['feels_like']['eve'] - 273.15)
        res_weather[str(n) + 'feels_temp_morning'] = int(
            weather['daily'][n]['feels_like']['morn'] - 273.15)
        res_weather[str(n) + 'feels_temp_night'] = int(
            weather['daily'][n]['feels_like']['night'] - 273.15)
        res_weather[str(n) + 'feels_temp_afternoon'] = int(
            weather['daily'][n]['feels_like']['day'] - 273.15)
        res_weather[str(n) + 'wind_speed'] = int(weather['daily'][n]['wind_speed'])
        res_weather[str(n) + 'date'] = int(weather['daily'][n]['dt'])
        res_weather[str(n) + 'id'] = weather['daily'][0]['weather'][0]['icon']
        res_weather[str(n) + 'clouds'] = weather['daily'][n]['weather'][0]['description']
    return res_weather


# noinspection PyBroadException
class Bot:
    def __init__(self, peer_id, message, from_id, photos):
        # id беседы
        self.peer_id = peer_id
        # текст сообщения
        self.message = message
        # id отправителя
        self.from_id = from_id
        # attachment фото
        self.photos = photos
        self.default_21 = {
            "players": {"id": [0, 0], "name": ["", ""], "score": [0, 0], "attempts": [0, 0]},
            "in_game": False,
            "check_player_end": False,
            "cards": [["57", 4], ["58", 11], ["59", 6], ["60", 7],
                      ["61", 8], ["62", 9], ["63", 10], ["64", 2],
                      ["65", 3], ["66", 4], ["67", 11], ["68", 6],
                      ["69", 7], ["70", 8], ["71", 9], ["72", 10],
                      ["73", 2], ["74", 3], ["75", 4], ["76", 11],
                      ["77", 6], ["78", 7], ["79", 8], ["80", 9],
                      ["81", 10], ["82", 2], ["83", 3], ["84", 11],
                      ["85", 6], ["86", 7], ["87", 8], ["88", 9],
                      ["89", 10], ["90", 2], ["91", 3], ["92", 4]]}
        # начальные проверки беседы
        try:
            if len(str(peer_id)) == 10:
                self.new()
                self.check_people()
                self.check_for_static()
            self.check_message()
        except Exception:
            self.send_message('Пожалуйста, сделайте бота админом')

    # сортировка сообщений на функции
    def check_message(self):
        if self.message[0:17:] == 'рандомный символ ':
            self.random_char()
        elif self.message == 'подписаны ли на группу' or self.message == "лень писат":
            self.ismember()
        elif self.message == 'команды':
            self.send_message('Команды бота доступны на стене по ссылке:\nhttps://vk.com/godofnatural ')
        elif self.message == 'рандом':
            self.random_user()
        elif self.message == 'статистика':
            self.get_static()
        elif '+ник' in self.message:
            self.change_nik_from()
        elif 'new_title:' in self.message:
            self.change_title()
        elif '+setting ' in self.message:
            self.change_settings()
        elif self.message == 'создатель' or self.message \
                == 'создатель этого бота' or self.message == 'создатель бота' in self.message:
            self.send_message('Создатель этого прекрасного (нет) бота:\n'
                              '[id202073373|Владислав Селезнёв],\n'
                              'Вопросы, пожелания и баги посылать [id202073373|'
                              'ему]\n'
                              'Бот хостится на pythonanywhere.com, хостинг очень'
                              ' слабый и если вы хотите помочь,'
                              ' то напишите [id202073373|'
                              'ему]')
        elif 'add_homework' in self.message:
            self.add_homework()
        elif 'игра ' == self.message[0:5]:
            self.zeros_playing()
        elif 'вызов' in self.message:
            self.message_for_game()
        elif 'принять' == self.message or self.message == '@godofnatural принять':
            self.agree_game()
        elif self.message == 'игра отмена':
            self.cancel_played()
        elif 'погода на' in self.message or self.message == 'погода':
            self.get_weather()
        elif '+setting ' in self.message:
            self.change_settings()
        elif 'add_subject' in self.message:
            self.add_subject()
        elif 'дз ' == self.message[0:3]:
            self.call_subject()
        elif self.message[:10:] == 'википедия ':
            self.send_message("Ищу " + self.message[10:])
            self.get_wikipedia()
        elif self.message[:4] == 'бан ':
            self.delete_user()
        elif self.message[:15] == 'русская рулетка':
            self.russian_roulette()
        elif self.message[:5] == "21 с ":
            self.offer()
        elif self.message == "[club196697372|@godofnatural] не хочу":
            self.decline_offer()
        elif self.message == "[club196697372|@godofnatural] принять":
            self.accept_offer()
        elif self.message == "достаточно!":
            self.final_game()
        elif self.message == "ещё карту":
            self.new_card()
        elif self.message == "отмена 21":
            self.end_21game()
        elif self.message == "правила21":
            self.rules()

    def rules(self):
        # отправляет правила игры 21 в личные сообщения
        self.send_message("Бот сдает каждому игроку по две карты, все карты дают игроку определенное "
                          "количество очков, туз - 11 очков, король - 4 очка, дама - 3 очка, валет - 2 очка, "
                          "остальные карты по своему номиналу. Цель игрока - собрать 21 очко или наиболее "
                          "близкое к нему число, после того, как игрок получил две карты, он может попросить "
                          "еще, как уже было сказано, нужно собрать 21 или как можно ближе, но если собрать "
                          "больше - это автоматическое поражение. Когда бот выдал игрокам столько карт, "
                          "сколько они просили, игроки вскрываются и показывают карты, побеждает тот, "
                          "кто собрал наиболее близкое количество очков к 21 или 21, но не больше.\n"
                          'Для вызова пиши: "21 с @/.../"(пример "21 c @rollbollvlad"), '
                          'чтобы принять, достаточно нажать на кнопку', )

    # функция подсчета сообщений
    def check_for_static(self):
        peer_id = str(self.peer_id)
        from_id = str(self.from_id)
        with open('conversations.json') as f:
            sl = json.load(f)

        sl[peer_id]['static_for_messages'][from_id] += 1
        with open('conversations.json', "w") as f:
            f.write(json.dumps(sl, ensure_ascii=False))

    # обработка финала игры 21 очко
    def final_game(self):
        with open('conversations.json') as f:
            sl = json.load(f)
        peer_id = sl["cur_conversation"]
        if sl[peer_id]["21_game"]["in_game"] \
                and self.from_id in sl[peer_id]["21_game"]["players"]["id"]:
            if not sl[peer_id]["21_game"]["check_player_end"]:
                sl[peer_id]["21_game"]["check_player_end"] = True
                with open('conversations.json', "w") as f:
                    f.write(json.dumps(sl, ensure_ascii=False))
            else:
                score_f = sl[peer_id]["21_game"]["players"]["score"][0]
                score_s = sl[peer_id]["21_game"]["players"]["score"][1]
                self.peer_id = peer_id
                if score_f > 21 and score_s > 21 or score_s == score_f:
                    self.send_message("Увы, победителей нет(\nИгра окончена")
                elif score_s < score_f <= 21 or score_f <= 21 and score_s > 21:
                    self.send_message("У нас есть победитель!!!\nИгра окончена")
                    self.send_message("Победил [id" + str(sl[peer_id]["21_game"]["players"]["id"][0])
                                      + "|" + sl[peer_id]["21_game"]["players"]["name"][0] + "]")

                elif score_f < score_s <= 21 or score_s <= 21 and score_f > 21:
                    self.send_message("У нас есть победитель!!!\nИгра окончена")
                    self.send_message("Победил [id" + str(sl[peer_id]["21_game"]["players"]["id"][1])
                                      + "|" + sl[peer_id]["21_game"]["players"]["name"][1] + "]")
                for i in range(2):
                    self.send_message("[id" + str(sl[peer_id]["21_game"]["players"]["id"][i])
                                      + "|" + sl[peer_id]["21_game"]["players"]["name"][i] + "] Набрал "
                                      + str(sl[peer_id]["21_game"]["players"]["score"][i]) + " очков")
                self.end_21game()

    # получение новой карты
    def new_card(self):
        with open('conversations.json') as f:
            sl = json.load(f)
        peer_id = sl["cur_conversation"]
        if sl[peer_id]["21_game"]["in_game"] \
                and self.from_id in sl[peer_id]["21_game"]["players"]["id"]:
            card = sl[peer_id]["21_game"]["cards"].pop()
            photo(self.from_id, "photo-197213529_4572390" + card[0])
            index_player = sl[peer_id]["21_game"]["players"]["id"].index(self.from_id)
            sl[peer_id]["21_game"]["players"]["score"][index_player] += card[1]
            send_message_user(self.from_id,
                              "Ваши текущие очки - "
                              + str(sl[peer_id]["21_game"]["players"]["score"][index_player]))
        with open('conversations.json', "w") as f:
            f.write(json.dumps(sl, ensure_ascii=False))

    # отправка запроса на игру
    def accept_offer(self):
        peer_id = str(self.peer_id)
        with open('conversations.json') as f:
            sl = json.load(f)
        if self.from_id != sl[peer_id]["21_game"]["players"]["id"][1]:
            self.send_message("Предложение было отправленно не вам")
        elif sl[peer_id]["21_game"]["in_game"]:
            self.send_message("игра уже идет")
        else:
            self.send_message("Игра начинается, чек лс")
            sl[peer_id]["21_game"]["in_game"] = True
            sl["cur_conversation"] = peer_id
            for _ in range(2):
                cards = [sl[peer_id]["21_game"]["cards"].pop(), sl[peer_id]["21_game"]["cards"].pop()]
                for k in range(2):
                    photo(sl[peer_id]["21_game"]["players"]["id"][k], "photo-197213529_4572390" + cards[k][0])
                    sl[peer_id]["21_game"]["players"]["score"][k] += cards[k][1]
                    send_message_user(sl[peer_id]["21_game"]["players"]["id"][k],
                                      "Ваши текущие очки - "
                                      + str(sl[peer_id]["21_game"]["players"]["score"][k]))
            with open('conversations.json', "w") as f:
                f.write(json.dumps(sl, ensure_ascii=False))

    # обработка завершения игры, очищение бд
    def end_21game(self):
        with open('conversations.json') as f:
            sl = json.load(f)
        if sl[str(self.peer_id)]["21_game"]["in_game"]:
            sl[str(self.peer_id)]["21_game"] = self.default_21
            with open('conversations.json', "w") as f:
                f.write(json.dumps(sl, ensure_ascii=False))

    # отказ от предложения играть
    def decline_offer(self):
        peer_id = str(self.peer_id)
        with open('conversations.json') as f:
            sl = json.load(f)
        if self.from_id != sl[peer_id]["21_game"]["players"]["id"][1] and not sl[peer_id]["21_game"]["in_game"]:
            self.send_message("Предложение было отправленно не вам или игра уже идет")
        else:
            self.send_message("Принято")
            self.end_21game()

    # отправляет предложение о игре в беседу, прилагая кнопки на сообщении
    def offer(self):
        with open('conversations.json') as f:
            sl = json.load(f)
        if sl[self.peer_id]["21_game"]["in_game"]:
            self.send_message(
                'Подождите окончания игры!'
                ' Или если вы являетесь участником, напишите "отмена 21"')
        else:
            try:
                self.end_21game()
                # получение имени, фамилии
                f = vk.users.get(user_ids=self.from_id)[0]
                s = vk.users.get(user_ids=self.message[8:17])[0]
                sl[self.peer_id]["21_game"]["players"]["id"] = [self.from_id, int(self.message[8:17])]
                sl[self.peer_id]["21_game"]["players"]["name"] = [f['first_name'] + ' ' + f['last_name'],
                                                                  s['first_name'] + ' ' + s['last_name']]
                shuffle(sl[self.peer_id]["21_game"]["cards"])
                keyboard = VkKeyboard(inline=True)
                keyboard.add_button("Принять", color=VkKeyboardColor.POSITIVE)
                keyboard.add_button("Не хочу", color=VkKeyboardColor.NEGATIVE)
                vk.messages.send(
                    peer_id=self.peer_id,
                    message="Ожидание подтверждения",
                    random_id=randint(0, 1000000000),
                    keyboard=keyboard.get_keyboard(),
                )
                with open('conversations.json', "w") as f:
                    f.write(json.dumps(sl, ensure_ascii=False))
            except Exception:
                self.send_message("Неверный формат ввода данных")

    # отправка сообщения
    def send_message(self, message):
        self.peer_id = int(self.peer_id)
        vk.messages.send(
            peer_id=self.peer_id,
            message=message,
            random_id=randint(0, 1000000000),
        )

    # функция удаление человека из беседы
    def delete_user(self, member=0):
        peer_id = int(self.peer_id)
        try:
            if member:
                member_id = member
            else:
                member_id = int(self.message.split("[")[1][2:].split("|")[0])
            vk.messages.removeChatUser(
                chat_id=peer_id - 2000000000,
                member_id=member_id,
            )
        except Exception as e:
            if "[15]" in str(e):
                self.send_message('Вы не можете забанить администратора')
            elif "[935]" in str(e):
                self.send_message('Этого участника нет в беседе')
            else:
                self.send_message('Неверный ввод данных')

    # русская рулетка на исключение человека
    def russian_roulette(self):
        from_id = int(self.from_id)
        message = self.message.split()
        bullet = randint(0, 9)
        num = -1
        try:
            num = int(message[2:][0])
            if not 0 <= num <= 9:
                raise Exception
        except IndexError:
            print('Неверный ввод данных')
        if bullet == num:
            self.delete_user(member=from_id)
            return 0
        self.send_message('Тебе повезло...')

    # функция выводящая рандомные символы(до 500)
    def random_char(self):
        num = str(self.message.split()[2])
        if not num.isdigit():
            return 0
        num = int(num)
        if num <= 0 or num > 501:
            return 0
        text = ''
        for i in range(num):
            text += chr(randint(1, 10000))
        self.send_message(text)

    # проверка на наличие беседы в бд
    def new(self):
        self.peer_id = str(self.peer_id)
        # заполнение первичных данных в бд
        list_of_people = vk.messages.getConversationMembers(peer_id=self.peer_id)
        with open('list_of_conversations.json') as f:
            sp = json.load(f)
        # если такая беседа уже была, то ничего не делается
        if self.peer_id in sp:
            return 0
        # если этой беседы ещё не было, то создаётся json файл со словарём
        sp.append(self.peer_id)
        with open('list_of_conversations.json', 'w') as f:
            f.write(json.dumps(sp, ensure_ascii=False))
        sl = {'names': {}, 'can_send_weather': True, 'can_send_random': True,
              'can_change_nik': True, 'static_for_random': {},
              'static_for_messages': {}, 'list_id': [],
              'title': 'натуралом', 'subjects': {},
              'play_in_zeros': {}, 'waiting_for_confirmation': {},
              'plaing_in_zeros': {}, 'in_zeros': {}, "21_game": self.default_21}
        for people in list_of_people['profiles']:
            sl['list_id'].append(str(people['id']))
            sl['names'][str(people['id'])] = people['first_name'] + " " + people['last_name']
            sl['play_in_zeros'][str(people['id'])] = 0
            sl['static_for_random'][str(people['id'])] = 0
            sl['static_for_messages'][str(people['id'])] = 0
        with open('conversations.json') as f:
            sp228 = json.load(f)
        sp228[self.peer_id] = sl
        sp228["cur_conversation"] = 0
        with open('conversations.json', 'w') as f:
            f.write(json.dumps(sp228, ensure_ascii=False))

    # смена ника, отображаемого при использовании
    def change_nik(self, user_id, new_name):
        self.peer_id = str(self.peer_id)
        user_id = str(user_id)
        with open('conversations.json') as f:
            sl = json.load(f)
        if not sl[self.peer_id]['can_change_nik']:
            self.send_message('Смена ника в беседе запрещена')
        sl[self.peer_id]['names'][user_id] = new_name
        self.send_message('Ok')
        with open('conversations.json', 'w') as f:
            f.write(json.dumps(sl, ensure_ascii=False))

    # проверка был ли человек в это беседе и раньше
    def check_people(self):
        peer_id = str(self.peer_id)
        user_id = str(self.from_id)
        with open('conversations.json') as f:
            sl = json.load(f)
        new_sl = {}
        try:
            if user_id not in sl[peer_id]['list_id']:
                sl[peer_id]['list_id'].append(user_id)
                list_of_people = vk.messages.getConversationMembers(peer_id=peer_id)
                for people in list_of_people['profiles']:
                    if str(people['id']) in sl[peer_id]['names']:
                        new_sl[str(people['id'])] = sl[peer_id]['names'][str(people['id'])]
                    else:
                        new_sl[str(people['id'])] = people['first_name'] + " " + people['last_name']
                        sl[peer_id]['static_for_random'][str(people['id'])] = 0
                        sl[peer_id]['list_id'].append(str(people['id']))
                        sl[peer_id]['play_in_zeros'][str(people['id'])] = 0
                sl[peer_id]['names'] = new_sl
            with open('conversations.json', 'w') as f:
                f.write(json.dumps(sl, ensure_ascii=False))
        except Exception:
            pass

    # функция для рандомного выбора человека
    def random_user(self):
        peer_id = str(self.peer_id)
        with open('conversations.json') as f:
            sl = json.load(f)
        if sl[peer_id]['can_send_random']:
            random_id = str(choice(sl[peer_id]['list_id']))
            sl[peer_id]['static_for_random'][random_id] += 1
            self.send_message('Сегодня ' + sl[peer_id]['title']
                              + ' становится: [id' + random_id + '|' +
                              sl[peer_id]['names'][random_id] + ']')
        else:
            self.send_message('Команда в этой беседе запрещена')
        with open('conversations.json', 'w') as f:
            f.write(json.dumps(sl, ensure_ascii=False))

    # функция для выдачи статистики по титулам и сообщениям
    def get_static(self):
        peer_id = str(self.peer_id)
        with open('conversations.json') as f:
            sl = json.load(f)
        message = ''
        for user_id in sl[peer_id]['static_for_random']:
            message += '[id' + user_id + '|' + sl[peer_id]['names'][user_id] + ']: ' + str(
                sl[peer_id]['static_for_random'][user_id]) + '\n'
        self.send_message(message)
        users = sl[peer_id]['static_for_messages']
        users = sorted(users.items(), key=lambda item: item[1])
        self.send_message(
            f'Больше всего сообщений написал \
            [id{str(users[-1][0])}|{sl[peer_id]["names"][users[-1][0]]}]: {str(users[-1][1])}')

    # функция по смене ника
    def change_nik_from(self):
        peer_id = str(self.peer_id)
        with open('conversations.json') as f:
            sl = json.load(f)
        if not sl[peer_id]['can_change_nik']:
            self.send_message('Команда запрещена в этой беседе')
        elif len(self.message) > 54:
            self.send_message('Ограничение по длине - 50 символов')
        elif self.message[0:5] != '+ник ':
            return 0
        else:
            self.change_nik(self.from_id, self.message[5::])

    # отображение подписанных учатников
    def ismember(self):
        list_of_people = vk.messages.getConversationMembers(peer_id=self.peer_id)['profiles']
        list_ids = []
        for elem in list_of_people:
            list_ids.append(elem['id'])
        res = vk.groups.isMember(group_id=196697372, user_ids=list_ids)
        with open('conversations.json') as f:
            sl = json.load(f)
        text = ''
        for elem in res:
            text += '[id' + str(elem['user_id']) \
                    + '|' + sl[str(self.peer_id)]['names'][str(elem['user_id'])] + '] - '
            if elem['member']:
                text += 'подписан\n'
            else:
                text += 'не подписан\n'
        self.send_message(text)

    # обрабатывает изменение настроек в бд
    def change_settings(self):
        peer_id = str(self.peer_id)
        message = self.message.split()
        if message[0] == '+setting' and len(message) > 2:
            try:
                with open('conversations.json') as f:
                    sl = json.load(f)
                if message[1] == 'send_weather':
                    if message[2] == 'вкл':
                        sl[peer_id]['can_send_weather'] = True
                    elif message[2] == 'выкл':
                        sl[peer_id]['can_send_weather'] = False
                    else:
                        self.send_message('не правильный формат ввода')
                elif message[1] == 'change_nik':
                    if message[2] == 'вкл':
                        sl[peer_id]['can_change_nik'] = True
                    elif message[2] == 'выкл':
                        sl[peer_id]['can_change_nik'] = False
                    else:
                        self.send_message('не правильный формат ввода')
                elif message[1] == 'send_random':
                    if message[2] == 'вкл':
                        sl[peer_id]['can_send_random'] = True
                    elif message[2] == 'выкл':
                        sl[peer_id]['can_send_random'] = False
                    else:
                        self.send_message('не правильный формат ввода')
                elif message[1] == 'add_new_subject':
                    if message[2] in sl['subjects']:
                        self.send_message('этот предмет уже зарегистрирован')
                        return 0
                    sl[peer_id]['subjects'][message[2]] = []

                else:
                    self.send_message('не правильный формат ввода')
                with open('conversations.json', 'w') as f:
                    f.write(json.dumps(sl, ensure_ascii=False))
            except Exception:
                self.send_message('Произошла ошибка, скорее всего'
                                  ' бот не администратор или не правильный формат ввода')
        else:
            self.send_message('Не правильный формат смены настроек')

    # смена титула
    def change_title(self):
        peer_id = str(self.peer_id)
        message = self.message.split()
        if message[0] != 'new_title:' or len(message) != 2:
            self.send_message('Не правильный формат ввода')
            return 0
        morph = pymorphy2.MorphAnalyzer()
        word = morph.parse(message[1])[0]
        if str(word.tag) == 'LATN':
            self.send_message('Введите титул на русском языке')
            return 0
        if str(word.tag) == 'UNKN':
            self.send_message('Введите титул без знаков препинания')
            return 0
        if str(word.tag.POS) != 'NOUN':
            self.send_message('Введённый титул должен быть существительным')
            return 0
        new_title = word.inflect({'ablt', 'sing'})
        if new_title is None:
            self.send_message('Произошла ошибка. Скорее всего это слово слишком редко случается.'
                              ' Если вам действительно'
                              ' надо поставить такой титул напишите @rollbollvlad')
            return 0
        with open('conversations.json') as f:
            sl = json.load(f)
        sl[peer_id]['title'] = new_title.word
        with open('conversations.json', 'w') as f:
            f.write(json.dumps(sl, ensure_ascii=False))
        self.send_message('Разыгрываемый титул изменён на "' + new_title.word +
                          '". Если форма слова образована неправильно напишите @rollbollvlad')

    # добавление предмета
    def add_subject(self):
        peer_id = str(self.peer_id)
        message = self.message.split()
        if message[0] == 'add_subject' and len(message) == 2:
            with open('conversations.json') as f:
                sl = json.load(f)

            sl[peer_id]['subjects'][message[1]] = []
            with open('conversations.json', 'w') as f:
                f.write(json.dumps(sl, ensure_ascii=False))
        self.send_message('Предмет добавлен')

    # обработка даты
    def transformation_date(self, last_date):
        if '.' not in last_date:
            self.send_message('Введите дату в формате DD.MM')
            return 0
        new_date = last_date.split('.')
        mm = str(new_date[1])
        dd = str(new_date[0])
        if mm.isdigit() and dd.isdigit():
            if int(mm) < 1 or int(mm) > 12:
                self.send_message('Колличество месяцев должено укладываться в рамки года')
                return 0
            if int(dd) < 1 or int(dd) > 31:
                self.send_message('Колличество дней должно укладываться в рамки месяца')
                return 0
            date = dd + '.' + mm
            return date
        self.send_message('Дата и месяц длжны быть числами')
        return 0

    # добавление домашнего задания
    def add_homework(self):
        peer_id = str(self.peer_id)
        message = self.message.split()
        if message[0] != 'add_homework':
            self.send_message('Не правильный формат ввода')
            return 0
        if 'на' in message:
            message.remove('на')
        if len(message) < 4:
            self.send_message('Не правильный формат ввода')
            return 0
        lesson = message[1]
        homework = ''
        date = self.transformation_date(message[2])
        if date == 0:
            return 0
        for elem in message[3::]:
            homework += elem + " "
        with open('conversations.json') as f:
            sl = json.load(f)
        if lesson not in sl[peer_id]['subjects']:
            self.send_message('вы ввели не зарегистрированный предмет')
            return 0
        homework += '\nПрикреплённые фото: '
        for elem in self.photos:
            homework += elem
            homework += ' '
        sl[peer_id]['subjects'][lesson].append([date, homework])
        with open('conversations.json', 'w') as f:
            f.write(json.dumps(sl, ensure_ascii=False))
        self.send_message("Успешно")

    # обработка вызова с дз
    def call_subject(self):
        message = self.message.split()
        peer_id = str(self.peer_id)
        if message[0] == 'дз' and len(message) >= 2:
            if message[1] == 'по':
                message.remove(message[1])
                n = str(dt.datetime.now()).split(' ')[0].split('-')
                now = int(n[1]) * 100 + int(n[2])
                if message[-1] == 'все':
                    message.remove('все')
                    now = -1
                if len(message) == 2:
                    subject = message[1]
                    with open('conversations.json') as f:
                        sl = json.load(f)
                    if subject in sl[peer_id]['subjects']:
                        message_ = ''
                        for (date, homework) in sl[peer_id]['subjects'][subject]:
                            d, m = map(int, date.split('.'))
                            if now <= m * 100 + d:
                                message_ += ('Дз на ' + date + ':\n' + homework + '\n\n')
                        self.send_message(message_)
            if message[1] == 'на':
                data = message[2]
                with open('conversations.json') as f:
                    sl = json.load(f)
                    message_ = 'Дз на ' + data + '\n'
                    for subject in sl[peer_id]['subjects']:
                        for (date, homework) in sl[peer_id]['subjects'][subject]:
                            if date == data:
                                message_ += 'Дз по ' + subject + '\n' + homework + '\n\n'
                self.send_message(message_)

    # обработка вызова на игру крестики нолики
    def message_for_game(self):
        peer_id = str(self.peer_id)
        from_id = str(self.from_id)
        message = self.message.split()
        if len(message) != 2 or message[0] != 'вызов':
            return 0
        message = message[1].split('|')
        if message[0][0:3] != '[id':
            return 0
        id_ = message[0][3::]
        with open('conversations.json') as f:
            sl = json.load(f)
        if sl[peer_id]['play_in_zeros'][id_] == 1:
            self.send_message('Игроку уже брошен вызов')
            return 0
        if sl[peer_id]['play_in_zeros'][id_] == 2:
            self.send_message('Игрок уже играет с кем-то')
            return 0
        if sl[peer_id]['play_in_zeros'][from_id] == 1:
            self.send_message('Вам уже брошен вызов')
            return 0
        if sl[peer_id]['play_in_zeros'][from_id] == 2:
            self.send_message('Вы уже играете с кем-то')
            return 0
        sl[peer_id]['play_in_zeros'][id_] = 1
        sl[peer_id]['play_in_zeros'][from_id] = 1
        sl[peer_id]['waiting_for_confirmation'][id_] = from_id
        self.send_message('[id' + id_ + '|' + sl[peer_id]['names'][id_]
                          + '] вам бросил вызов ' + '[id' + from_id
                          + '|' + sl[peer_id]['names'][from_id] + ']')
        with open('conversations.json', 'w') as f:
            f.write(json.dumps(sl, ensure_ascii=False))

    # обработка соглашения игры
    def agree_game(self):
        peer_id = str(self.peer_id)
        from_id = str(self.from_id)
        with open('conversations.json') as f:
            sl = json.load(f)
        if from_id not in sl[peer_id]['waiting_for_confirmation']:
            self.send_message('Вам не поступало вызовов')
            return 0
        if sl[peer_id]['play_in_zeros'][from_id] != 1:
            self.send_message('Вам не поступало вызовов, либо вы уже играете с кем-то')
            return 0
        id_ = sl[peer_id]['waiting_for_confirmation'][from_id]
        ids = sorted([id_, from_id])
        ids_for_sl = ids[0] + ids[1]
        who_move = choice([0, 1])
        # первичные данные в крестиках-ноликах
        sl[peer_id]['plaing_in_zeros'][id_] = from_id
        sl[peer_id]['plaing_in_zeros'][from_id] = id_
        sl[peer_id]['in_zeros'][ids_for_sl] = {}
        field = ['1 ', ' 2 ', ' 3', '4 ', ' 5 ', ' 6', '7 ', ' 8 ', ' 9']
        sl[peer_id]['in_zeros'][ids_for_sl]['field'] = field
        sl[peer_id]['in_zeros'][ids_for_sl]['who_move'] = who_move
        sl[peer_id]['in_zeros'][ids_for_sl]['first_player'] = ids[who_move]
        sl[peer_id]['play_in_zeros'][id_] = 2
        sl[peer_id]['play_in_zeros'][from_id] = 2
        self.send_message('Первым ходит [id' + ids[who_move]
                          + '|' + sl[peer_id]['names'][ids[who_move]] + ']')
        self.send_message('{} | {} | {}\n'
                          '---------------\n'
                          '{} | {} | {}\n'
                          '---------------\n'
                          '{} | {} | {}'.format(field[0], field[1], field[2], field[3],
                                                field[4], field[5],
                                                field[6], field[7], field[8]))
        with open('conversations.json', 'w') as f:
            f.write(json.dumps(sl, ensure_ascii=False))

    # обработка хода и исхода игры
    def zeros_playing(self):
        peer_id = str(self.peer_id)
        from_id = str(self.from_id)

        def make_a_move(field_, id_, played):
            if played == 1:
                played = 'X'
            else:
                played = 'O'
            if field_[id_] == "X" or field_[id_] == "O":
                return field_, 0
            field[id_] = played
            a = [0, 0, 1, 2, 3, 6, 0, 2]
            b = [1, 3, 4, 5, 4, 7, 4, 4]
            c = [2, 6, 7, 8, 5, 8, 8, 6]
            count = 0
            for i in range(8):
                if field_[a[i]] == field_[b[i]] == field_[c[i]] != " ":
                    if field_[a[i]] == 'X':
                        return field_, 1
                    elif field_[a[i]] == 'O':
                        return field, 2
            for i in range(9):
                if field_[i] == 'X' or field_[i] == 'O':
                    count += 1
            if count == 9:
                return field_, 4
            return field_, 3

        with open('conversations.json') as f:
            sl = json.load(f)
        message = self.message.split()
        if len(message) != 2 or not message[1].isdigit():
            return 0
        if sl[peer_id]['play_in_zeros'][from_id] != 2:
            self.send_message('Вам не поступало вызовов, либо вы ещё не согласились')
            return 0
        if int(message[1]) < 1 or int(message[1]) > 9:
            self.send_message('Не правильные границы ввода')
            return 0
        user_id = sl[peer_id]['plaing_in_zeros'][from_id]
        ids = sorted([from_id, user_id])
        ids_for_sl = ids[0] + ids[1]
        who_move = sl[peer_id]['in_zeros'][ids_for_sl]['who_move']
        field = sl[peer_id]['in_zeros'][ids_for_sl]['field']
        if ids[who_move] != from_id:
            self.send_message('Сейчас не ваша очередь ходить')
            return 0
        field, code = make_a_move(field, int(message[1]) - 1,
                                  sl[peer_id]['in_zeros'][ids_for_sl]['first_player'] == ids[who_move])
        if code == 0:
            self.send_message('Эта клетка уже занята')
            return 0
        elif code == 4:
            sl[peer_id]['play_in_zeros'][from_id] = 0
            sl[peer_id]['play_in_zeros'][user_id] = 0
            self.send_message('Ничья')
        elif code == 2:
            sl[peer_id]['play_in_zeros'][from_id] = 0
            sl[peer_id]['play_in_zeros'][user_id] = 0
            if sl[peer_id]['in_zeros'][ids_for_sl]['first_player'] != from_id:
                self.send_message('Выиграл [id' + ids[who_move]
                                  + '|' + sl[peer_id]['names'][ids[who_move]] + ']')
            else:
                self.send_message(
                    'Выиграл [id' + ids[1 - who_move]
                    + '|' + sl[peer_id]['names'][ids[1 - who_move]] + ']')
        elif code == 1:
            sl[peer_id]['play_in_zeros'][from_id] = 0
            sl[peer_id]['play_in_zeros'][user_id] = 0
            if sl[peer_id]['in_zeros'][ids_for_sl]['first_player'] == from_id:
                self.send_message('Выиграл [id' + ids[who_move]
                                  + '|' + sl[peer_id]['names'][ids[who_move]] + ']')
            else:
                self.send_message(
                    'Выиграл [id' + ids[1 - who_move]
                    + '|' + sl[peer_id]['names'][ids[1 - who_move]] + ']')
        elif code == 3:
            self.send_message('Продолжаем играть')
        sl[peer_id]['in_zeros'][ids_for_sl]['who_move'] = 1 - who_move
        self.send_message('{} | {} | {}\n'
                          '------------\n'
                          '{} | {} | {}\n'
                          '------------\n'
                          '{} | {} | {}'.format(field[0], field[1], field[2], field[3],
                                                field[4], field[5],
                                                field[6], field[7], field[8]))
        with open('conversations.json', 'w') as f:
            f.write(json.dumps(sl, ensure_ascii=False))

    # отказ от игры
    def cancel_played(self):
        peer_id = str(self.peer_id)
        from_id = str(self.from_id)
        with open('conversations.json') as f:
            sl = json.load(f)
        sl[peer_id]['play_in_zeros'][from_id] = 0
        if from_id in sl[peer_id]['play_in_zeros']:
            sl[peer_id]['play_in_zeros'][sl[peer_id]['plaing_in_zeros'][from_id]] = 0
        self.send_message('Ok')
        with open('conversations.json', 'w') as f:
            f.write(json.dumps(sl, ensure_ascii=False))

    # эта функция обрабатывает сообщение с погодой и вызывает различные функции
    def get_weather(self):
        peer_id = str(self.peer_id)
        message = self.message
        with open('conversations.json') as f:
            sl = json.load(f)
        if not sl[peer_id]['can_send_weather']:
            self.send_message('Команда в этой беседе запрещена')
            return 0
        if message == 'погода' or message == 'Погода на сегодня':
            self.get_weather_to_some_days(1)
            return 0
        elif message == 'погода на завтра':
            self.get_weather_to_tomorrow()
            return 0
        message = message.split()
        if len(message) > 2:
            if message[2].isdigit():
                num = int(message[2])
                if num > 8:
                    self.send_message('Слишком большое количество дней')
                elif num < 1:
                    self.send_message('Слишком маленькое количество дней')
                else:
                    self.get_weather_to_some_days(num)
            else:
                self.send_message('Не правильный формат ввода')
        else:
            self.send_message('Ошибка')

    # возращает сообщение с погодой на завтра
    def get_weather_to_tomorrow(self):
        weather = get_weather_days(2)
        i = 1
        date = str(from_second_to_date(weather[str(i) + 'date']))[:-8]
        message_ = ''
        message_ += 'Погода на {}\n\n' \
                    'Днём {}°, ощущается как {}°\n' \
                    'Ночью {}°, ощущается как {}°\n' \
                    'Будет {}\n' \
                    'Ветер {} М/С\n\n\n'.format(date,
                                                weather[
                                                    str(i) + 'temp_afternoon'],
                                                weather[str(
                                                    i) + 'feels_temp_afternoon'],
                                                weather[str(i) + 'temp_night'],
                                                weather[str(
                                                    i) + 'feels_temp_night'],
                                                weather[str(i) + 'clouds'],
                                                weather[str(i) + 'wind_speed'])
        self.send_message(message_)

    # возращает сообщение с погодой на определённое число дней
    def get_weather_to_some_days(self, num):
        message_ = ''
        weather = get_weather_days(num)
        for i in range(num):
            date = str(from_second_to_date(weather[str(i) + 'date']))[:-8]
            message_ += 'Погода на {}\n\n' \
                        'Днём {}°, ощущается как {}°\n' \
                        'Ночью {}°, ощущается как {}°\n' \
                        'Будет {}\n' \
                        'Ветер {} М/С\n\n\n'.format(date,
                                                    weather[
                                                        str(i) + 'temp_afternoon'],
                                                    weather[str(
                                                        i) + 'feels_temp_afternoon'],
                                                    weather[str(i) + 'temp_night'],
                                                    weather[str(
                                                        i) + 'feels_temp_night'],
                                                    weather[str(i) + 'clouds'],
                                                    weather[str(i) + 'wind_speed'])
        self.send_message(message_)

    # получение данных с википедии
    def get_wikipedia(self):
        start_time = time.perf_counter()
        peer_id = self.peer_id
        message = self.message[10::]

        # получение текста с страницы
        def get_text_wikipedia(message2):
            wikipedia.set_lang('ru')
            r = wikipedia.search(message2)
            return wikipedia.page(r[0]).content

        try:
            text = get_text_wikipedia(message).split("\n")[0]
            # text = text.split("\n")[0]
            # print(imgs)
            myobj = gTTS(text=text, lang='ru', slow=False)
            myobj.save("voice1.mp3")
            a = vk.docs.getMessagesUploadServer(type='audio_message', peer_id=peer_id)
            b = requests.post(a['upload_url'], files={
                'file': open("D:\\python\\vkbotremake3\\voice1.mp3",
                             'rb')}).json()
            # vk.method("messages.send",
            # {"peer_id": s, "message": "Ваша картинка", "attachment": d, "random_id": 0})
            c = vk.docs.save(file=b["file"])['audio_message']
            d = 'audio{}_{}'.format(c['owner_id'], c['id'])
            self.send_message(text)
            vk.messages.send(
                peer_id=peer_id,
                attachment=d,
                message='Здесь должна быть прикреплина аудиозапись с этой ссылкой ' + c['link_mp3'],
                random_id=randint(1, 100000000)
            )
            vk.messages.send(
                peer_id=peer_id,
                message='Запрос выполнялся ' + str
                (time.perf_counter() - start_time),
                random_id=randint(1, 100000000)
            )
            return 0
        except Exception:
            pass


# основной цикл программы
def main():
    while True:
        for event in VkBotLongPoll.listen():
            if 'message' not in event.object:
                continue
            peer_id = event.object['message']['peer_id']
            message = (event.object['message']['text']).lower() if (
                event.object['message']['text']).lower() else " "
            from_id = event.object['message']['from_id']
            photos = [elem['photo']['sizes'][-1]['url']
                      for elem in event.object['message']['attachments']
                      if elem['type'] == 'photo']
            Bot(peer_id, message, from_id, photos)


# основные данные
token = "ffe517a0e394b9d6df6d624d16dd58102ad0de99c8c8f08468628085d7e11e5d08953b42d69e553fccc64"
vkBotSession = VkApi(token=token)
groupId = 196697372
VkBotLongPoll = VkBotLongPoll(vkBotSession, groupId)
vk = vkBotSession.get_api()
main()
