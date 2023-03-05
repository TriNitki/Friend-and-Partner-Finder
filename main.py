import os
import json

import telebot
import sqlite3
import models

from dotenv import load_dotenv
from telebot import types

from func import delete_user, check_city, year_type, define_user


load_dotenv()


#bot
bot_token = os.getenv("bot_token")
bot = telebot.TeleBot(bot_token)

user = models.User()



'''=========MSG==HANDLER========='''
"New user greet"
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Меню 🏠")
    markup.add(item1)
    bot.send_message(message.chat.id, f'Привет, {message.chat.username}👋!\
                    \nДобро пожаловать в "DetectlyBot"! Этот бот создан для поиска друзей и бизнес партнеров.', reply_markup=markup)

"Commands that require db access"
@bot.message_handler(content_types=['text'])
def db_req_com(message):
    global connect, cursor, user
    connect = sqlite3.connect('users.sqlite3', check_same_thread=False)
    cursor = connect.cursor()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    # Create new db if it isn't exist
    cursor.execute("""CREATE TABLE IF NOT EXISTS login_id(
        id          INTEGER,
        first_name  STRING,
        second_name STRING,
        age         INTEGER,
        sex         STRING,
        city        STRING,
        region      STRING,
        interests   STRING
    )""")
    connect.commit()

    cursor.execute(f"SELECT id FROM login_id WHERE id = {message.chat.id}")
    data = cursor.fetchone()
    if data != None:
        user = define_user(message)

    if message.text.lower() in ["/reg", "регистрация ✏"]:
        #register user if it isn't exist
        if data == None:
            reg_user(message)
        else:
            bot.send_message(message.chat.id, 'Данный пользователь уже зарегестрирован.')
    elif message.text.lower() in ["/delete", "удаление 🚫"]:
        #delete user if it is exist
        if data == None:
            bot.send_message(message.chat.id, 'Пользователь еще не создан.\nДля регистрации воспользуйтесь командой /reg.')
        else:
            markup = get_menu(message, type="alert")
            bot.send_message(message.chat.id, 'Вы действительно хотите удалить Вашу анкету?', reply_markup=markup)
            bot.register_next_step_handler(message, alert_delete)
    elif message.text.lower() in ["/me", "моя анкета 👤"]:
        #greet user if it is exist
        if data == None:
            bot.send_message(message.chat.id, 'Пользователь еще не создан.\nДля регистрации воспользуйтесь командой /reg')
        else:
            greet_user(message)
    elif message.text.lower() in ["/help", "помощь 🆘"]:
        help(message)
    elif message.text.lower() in ["/main", "меню 🏠"]:
        main_menu(message)
    elif message.text.lower() in ["/edit", "редактирование 🛠"]:
        if data == None:
            bot.send_message(message.chat.id, 'Пользователь еще не создан.\nДля регистрации воспользуйтесь командой /reg')
        else:
            markup = get_menu(message, "edit")
            bot.send_message(message.chat.id, 'Что Вы хотите отредактировать?', reply_markup=markup)
            bot.register_next_step_handler(message, edit_profile)
    else:
        bot.reply_to(message, '🤨')
        bot.send_message(message.chat.id, 'Не понял.\nДля начала регистрации введите команду /start.')

'''=============================='''


def greet_user(message):
    markup = get_menu(message, type = "main")

    real_sex = {"m": "мужской", "w": "женский", "undef": "секретный"}[user.sex]

    'Greet'
    bot.send_message(message.chat.id, f'Привет, {user.second_name} {user.first_name}. Тебе {user.age} {year_type(user.age)}.')
    if user.city != 'undef':
        bot.send_message(message.chat.id, f'Твой пол - {real_sex}. Ты живешь в городе {user.city}, {user.region}')
    else:
        bot.send_message(message.chat.id, f'Твой пол - {real_sex}.')
    bot.send_message(message.chat.id, f'Твои интересы: {", ".join(json.loads(user.interests))}.', reply_markup=markup)

def help(message):
    markup = get_menu(message, type="help")
    bot.send_message(message.chat.id,   '/help - Список доступных команд\
                                        \n/main - Главное меню\
                                        \n/reg - Регистрация анкеты\
                                        \n/edit - Редактирование анкеты\
                                        \n/delete - Удаление анкеты\
                                        \n/me - Демонстрация анкеты', reply_markup=markup)

def main_menu(message):
    markup = get_menu(message, type="main")
    bot.send_message(message.chat.id, 'Добро пожаловать в Главное Меню!', reply_markup=markup)

def alert_delete(message):
    if message.text.lower() in ["да", "да ✅"]:
        delete_user(message.chat.id)
        markup = get_menu(message, type="main")
        bot.send_message(message.chat.id, 'Пользователь был удален.\nДля повторной регистрации воспользуйтесь командой /reg.', reply_markup=markup)
    elif message.text.lower() in ["нет", "нет ❌"]:
        bot.send_message(message.chat.id, 'Рад, что Вы передумали!')
    else:
        bot.reply_to(message.chat.id, 'Не понял.')
        bot.send_message(message.chat.id, 'Вы действительно хотите удалить Вашу анкету?')
        bot.register_next_step_handler(message, alert_delete)

def get_menu(message, type):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    item_reg = types.KeyboardButton("Регистрация ✏")
    item_me = types.KeyboardButton("Моя анкета 👤")
    item_edit = types.KeyboardButton("Редактирование 🛠")
    item_delete = types.KeyboardButton("Удаление 🚫")
    item_help = types.KeyboardButton("Помощь 🆘")
    item_main = types.KeyboardButton("Меню 🏠")

    item_yes = types.KeyboardButton("Да ✅")
    item_no = types.KeyboardButton("Нет ❌")

    item_man = types.KeyboardButton("Я парень 👨")
    item_woman = types.KeyboardButton("Я девушка 👩‍🦰")
    item_nosex = types.KeyboardButton("ATTACK HELICOPTER 🚁")

    item_fname = types.KeyboardButton("Имя 👋")
    item_sname = types.KeyboardButton("Фамилия 👨‍👩‍👧")
    item_age = types.KeyboardButton("Возраст 🔞")
    item_sex = types.KeyboardButton("Пол 🌝")
    item_city = types.KeyboardButton("Город 🏙")
    item_interests = types.KeyboardButton("Интересы 🌈")
    item_changeall = types.KeyboardButton("Изменить все ☠️")
    item_back = types.KeyboardButton("Назад ⬅️")

    cursor.execute(f"SELECT id FROM login_id WHERE id = {message.chat.id}")
    data = cursor.fetchone()
    
    if type == "alert":
        markup.add(item_yes, item_no)
    elif type == "help":
        if data==None:
            markup.add(item_reg, item_delete, item_me, item_edit, item_main, item_help)
        else:
            markup.add(item_delete, item_me, item_edit, item_help, item_main, item_reg)
    elif type == "edit":
        markup.add(item_fname, item_sname, item_age, item_sex, item_city, item_interests, item_changeall, item_back)
    elif type == "sex":
        markup.add(item_man, item_woman, item_nosex)
    else:
        if data==None:
            markup.add(item_reg)
        else:
            markup.add(item_delete, item_me, item_edit, item_help)
    
    return markup


'''=========Registration========='''
def reg_user(message):
    markup = types.ReplyKeyboardRemove()
    user.id = message.chat.id
    bot.send_message(message.chat.id, "Какое у тебя будет имя?", reply_markup=markup)
    bot.register_next_step_handler(message, get_first_name)

def get_first_name(message):
    try:
        user.first_name = message.text
    except:
        bot.reply_to(message, 'Неверное значение. Попробуйте ввести что-нибудь другое.')
        bot.send_message(message.chat.id, "Какое у тебя будет имя?")
        bot.register_next_step_handler(message, get_first_name)
        return

    bot.send_message(message.chat.id, 'Какая у тебя будет фамилия?')
    bot.register_next_step_handler(message, get_second_name)

def get_second_name(message):
    try:
        user.second_name = message.text
    except:
        bot.reply_to(message, 'Неверное значение. Попробуйте ввести что-нибудь другое.')
        bot.send_message(message.chat.id, "Какая у тебя будет фамилия?")
        bot.register_next_step_handler(message, get_age)
        return
    
    bot.send_message(message.chat.id, 'Сколько тебе лет?')
    bot.register_next_step_handler(message, get_age)

def get_age(message):
    try:
        user.age = int(message.text)
    except:
        bot.reply_to(message, 'Может лучше цифрами введешь?')
        bot.register_next_step_handler(message, get_age)
        return

    markup = get_menu(message, type = "sex")
    bot.send_message(message.chat.id, 'Какого ты пола?', reply_markup=markup)
    bot.register_next_step_handler(message, get_sex)

def get_sex(message):
    markup = get_menu(message, type = "sex")
    try:
        if message.text.lower() in ['м', 'мужской', 'муж', 'мужик', 'm', 'man', 'я парень 👨']:
            user.sex = 'm'
        elif message.text.lower() in ['ж', 'женский', 'жен', 'девушка', 'женщина', 'w', 'woman', 'я девушка 👩‍🦰']:
            user.sex = 'w'
        elif message.text.lower() in ['п', 'пропустить', 'прапустить', 'не', 'нет', 'u', 'undef', 'undefined', "attack helicopter 🚁"]:
            user.sex = 'undef'
        else:
            bot.reply_to(message, 'Прости, но такого пола я не знаю. Вот какие я знаю:', reply_markup=markup)
            bot.send_message(message.chat.id, 'М - мужской\
                            \nЖ - женский\
                            \nП - пропустить этот вопрос')
            bot.register_next_step_handler(message, get_sex)
            return
    except:
        bot.reply_to(message, 'Неверное значение. Попробуйте ввести что-нибудь другое.')
        bot.send_message(message.chat.id, "Какого ты пола?", reply_markup=markup)
        bot.register_next_step_handler(message, get_sex)
        return
    
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, 'В каком городе ты живешь?', reply_markup=markup)
    bot.register_next_step_handler(message, get_city)

def get_city(message):
    try:
        new_city = check_city(message.text.title())
        if new_city:
            user.city = new_city["city"]
            user.region = new_city["region"]
        elif message.text.lower() == 'п':
            user.city = 'undef'
            user.region = 'undef'
        else:
            bot.reply_to(message, 'Прости, но такого города я не знаю.\nПопробуй ввести его еще раз или напиши "П" для пропуска вопроса.')
            bot.register_next_step_handler(message, get_city)
            return
    except:
        bot.reply_to(message, 'Неверное значение. Попробуйте ввести что-нибудь другое.')
        bot.send_message(message.chat.id, "В каком городе ты живешь?")
        bot.register_next_step_handler(message, get_city)
        return
    
    bot.send_message(message.chat.id, 'Перечисли свои интересы через запятую.')
    bot.register_next_step_handler(message, get_interests)

def get_interests(message):
    try:
        interests = [item.strip() for item in message.text.lower().split(',')]
        user.interests = json.dumps(interests, indent=4, ensure_ascii=False)
    except:
        bot.reply_to(message, 'Неверное значение. Попробуйте ввести что-нибудь другое.')
        bot.send_message(message.chat.id, "Перечисли свои интересы через запятую.")
        bot.register_next_step_handler(message, get_interests)
        return
    
    cursor.execute("INSERT INTO login_id VALUES(?, ?, ?, ?, ?, ?, ?, ?);", user.get_data())
    connect.commit()
    greet_user(message)
'''=============================='''


'''=============Edit============='''
def edit_profile(message):
    markup = types.ReplyKeyboardRemove()
    if message.text.lower() in ["и", "имя", "имя 👋"]:
        bot.send_message(message.chat.id, "Какое у тебя будет имя?", reply_markup=markup)
        bot.register_next_step_handler(message, edit_first_name)
    elif message.text.lower() in ["ф", "фамилия", "фамилия 👨‍👩‍👧"]:
        bot.send_message(message.chat.id, 'Какая у тебя будет фамилия?', reply_markup=markup)
        bot.register_next_step_handler(message, edit_second_name)
    elif message.text.lower() in ["в", "возраст", "возраст 🔞"]:
        bot.send_message(message.chat.id, 'Сколько тебе лет?', reply_markup=markup)
        bot.register_next_step_handler(message, edit_age)
    elif message.text.lower() in ["п", "пол", "пол 🌝"]:
        bot.send_message(message.chat.id, 'Какого ты пола?', reply_markup=markup)
        bot.register_next_step_handler(message, edit_sex)
    elif message.text.lower() in ["г", "город", "город 🏙"]:
        bot.send_message(message.chat.id, 'В каком городе ты живешь?', reply_markup=markup)
        bot.register_next_step_handler(message, edit_city)
    elif message.text.lower() in ["ин", "интересы", "интересы 🌈"]:
        bot.send_message(message.chat.id, 'Перечисли интересы через запятую.', reply_markup=markup)
        bot.register_next_step_handler(message, edit_interests)
    elif message.text.lower() in ["все", "всё", "изменить все", "изменить все ☠️"]:
        delete_user(message.chat.id)
        reg_user(message)
    elif message.text.lower() in ["н", "ничего", "назад", "назад ⬅️"]:
        greet_user(message)
        return
    else:
        bot.reply_to(message, "Такого я не знаю.")
        markup = get_menu(message, "edit")
        bot.send_message(message.chat.id, 'Что Вы хотите отредактировать?', reply_markup=markup)

def edit_first_name(message):
    try:
        user.first_name = message.text
    except:
        bot.reply_to(message, 'Неверное значение. Попробуйте ввести что-нибудь другое.')
        bot.send_message(message.chat.id, "Какое у тебя будет имя?")
        bot.register_next_step_handler(message, edit_first_name)
        return
    delete_user(message.chat.id)
    cursor.execute("INSERT INTO login_id VALUES(?, ?, ?, ?, ?, ?, ?, ?);", user.get_data())
    connect.commit()
    bot.reply_to(message, 'Понял!')
    back_to_edit(message)

def edit_second_name(message):
    try:
        user.second_name = message.text
    except:
        bot.reply_to(message, 'Неверное значение. Попробуйте ввести что-нибудь другое.')
        bot.send_message(message.chat.id, 'Какая у тебя будет фамилия?')
        bot.register_next_step_handler(message, edit_second_name)
        return
    delete_user(message.chat.id)
    cursor.execute("INSERT INTO login_id VALUES(?, ?, ?, ?, ?, ?, ?, ?);", user.get_data())
    connect.commit()
    bot.reply_to(message, 'Понял!')
    back_to_edit(message)

def edit_age(message):
    try:
        user.age = int(message.text)
    except:
        bot.reply_to(message, 'Может лучше цифрами введешь?')
        bot.register_next_step_handler(message, edit_age)
        return
    delete_user(message.chat.id)
    cursor.execute("INSERT INTO login_id VALUES(?, ?, ?, ?, ?, ?, ?, ?);", user.get_data())
    connect.commit()
    bot.reply_to(message, 'Понял!')
    back_to_edit(message)

def edit_sex(message):
    if message.text.lower() in ['м', 'мужской', 'муж', 'мужик', 'm', 'man']:
        user.sex = 'm'
    elif message.text.lower() in ['ж', 'женский', 'жен', 'девушка', 'женщина', 'w', 'woman']:
        user.sex = 'w'
    elif message.text.lower() in ['п', 'пропустить', 'прапустить', 'не', 'нет', 'u', 'undef', 'undefined']:
        user.sex = 'undef'
    else:
        bot.reply_to(message, 'Прости, но такого пола я не знаю. Вот какие я знаю:')
        bot.send_message(message.chat.id, 'М - мужской\
                         \nЖ - женский\
                         \nП - пропустить этот вопрос')
        bot.register_next_step_handler(message, edit_sex)
        return
    delete_user(message.chat.id)
    cursor.execute("INSERT INTO login_id VALUES(?, ?, ?, ?, ?, ?, ?, ?);", user.get_data())
    connect.commit()
    bot.reply_to(message, 'Понял!')
    back_to_edit(message)

def edit_city(message):
    new_city = check_city(message.text.title())
    if new_city:
        user.city = new_city["city"]
        user.region = new_city["region"]
    elif message.text.lower() == 'п':
        user.city = 'undef'
        user.region = 'undef'
    else:
        bot.reply_to(message, 'Прости, но такого города я не знаю.\nПопробуй ввести его еще раз или напиши "П" для пропуска вопроса.')
        bot.register_next_step_handler(message, edit_city)
        return
    delete_user(message.chat.id)
    cursor.execute("INSERT INTO login_id VALUES(?, ?, ?, ?, ?, ?, ?, ?);", user.get_data())
    connect.commit()
    bot.reply_to(message, 'Понял!')
    back_to_edit(message)

def edit_interests(message):
    try:
        interests = [item.strip() for item in message.text.lower().split(',')]
        user.interests = json.dumps(interests, indent=4, ensure_ascii=False)
    except:
        bot.reply_to(message, 'Неверное значение. Попробуйте ввести что-нибудь другое.')
        bot.send_message(message.chat.id, 'Перечисли интересы через запятую.')
        bot.register_next_step_handler(message, edit_interests)
        return
    delete_user(message.chat.id)
    cursor.execute("INSERT INTO login_id VALUES(?, ?, ?, ?, ?, ?, ?, ?);", user.get_data())
    connect.commit()
    bot.reply_to(message, 'Понял!')
    back_to_edit(message)

def back_to_edit(message):
    markup = get_menu(message, "edit")
    bot.send_message(message.chat.id, 'Что Вы хотите отредактировать?', reply_markup=markup)
    bot.register_next_step_handler(message, edit_profile)
'''=============================='''



bot.polling()