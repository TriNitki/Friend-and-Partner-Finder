import telebot
import sqlite3
import os
import json
from dotenv import load_dotenv

load_dotenv()

#bot
bot_token = os.getenv("bot_token")
bot = telebot.TeleBot(bot_token)

import models
from func import delete_user, check_city, year_type

'''========BOT==COMMANDS========'''
"New user greet"
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Привет, {message.chat.username}👋!\
                    \nДобро пожаловать в "DetectlyBot"! Этот бот создан для поиска друзей и бизнес партнеров.')
    bot.send_message(message.chat.id, 'Для начала регистрации введите команду /reg. Для полного списка возможностей введите /help.')

"Send full list of available commands"
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,    'Список комманд:')
    bot.send_message(message.chat.id,    '/start - меню приветствия\
                                        \n/help - полный список доступных команд\
                                        \n/reg - начать регистрацию\
                                        \n/delete - удаление пользователя\
                                        \n/me - приветствие зарегистрированного пользователя\
                                        ')

"Commands that require db access"
@bot.message_handler(commands=['reg', 'delete', 'me', 'edit'])
def db_req_com(message):
    global connect, cursor, user
    connect = sqlite3.connect('users.sqlite3', check_same_thread=False)
    cursor = connect.cursor()
    user = models.User(message.chat.id) # Define user

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
        cursor.execute(f"SELECT id, first_name, second_name, age, sex, city, region, interests FROM login_id WHERE id = {message.chat.id}")
        id, f_name, s_name, age, sex, city, region, interests = cursor.fetchone()
        user = models.User(id, f_name, s_name, age, sex, city, region, interests)

    if message.text == "/reg":
        #register user if it isn't exist
        if data == None:
            reg_user(message)
        else:
            bot.send_message(message.chat.id, 'Данный пользователь уже зарегестрирован.')
    elif message.text == "/delete":
        #delete user if it is exist
        if data == None:
            bot.send_message(message.chat.id, 'Пользователь еще не создан.\nДля регистрации воспользуйтесь командой /reg.')
        else:
            delete_user(message.chat.id)
            bot.send_message(message.chat.id, 'Пользователь был удален.\nДля повторной регистрации воспользуйтесь командой /reg.')
    elif message.text == "/me":
        #greet user if it is exist
        if data == None:
            bot.send_message(message.chat.id, 'Пользователь еще не создан.\nДля регистрации воспользуйтесь командой /reg')
        else:
            greet_user(message)
    elif message.text == "/edit":
        if data == None:
            bot.send_message(message.chat.id, 'Пользователь еще не создан.\nДля регистрации воспользуйтесь командой /reg')
        else:
            bot.send_message(message.chat.id, 'Напишите что хотите отредактировать:')
            bot.send_message(message.chat.id, 'И - Имя\nФ - Фамилия\nВ - Возраст\nП - Пол\nГ - Город\nИ - Интересы\nВсе - Изменить все\nН - ничего, я передумал')
            bot.register_next_step_handler(message, edit_profile)

"Default bot reply"
@bot.message_handler(content_types=['text'])
def non_com(message):
    bot.reply_to(message, '🤨')
    bot.send_message(message.chat.id, 'Не понял.\nДля начала регистрации введите команду /start.')
'''=============================='''


'''=========Registration========='''
def greet_user(message):
    cursor.execute(f"SELECT id, first_name, second_name, age, sex, city, region, interests FROM login_id WHERE id = {message.chat.id}")
    id, f_name, s_name, age, sex, city, region, interests = cursor.fetchone()
    user = models.User(id, f_name, s_name, age, sex, city, region, interests)
    real_sex = {"m": "мужской", "w": "женский", "undef": "секретный"}[user.sex]

    'Greet'
    bot.send_message(message.chat.id, f'Привет, {user.second_name} {user.first_name}. Тебе {user.age} {year_type(user.age)}.')
    if user.city != 'undef':
        bot.send_message(message.chat.id, f'Твой пол - {real_sex}. Ты живешь в городе {user.city}, {user.region}')
    else:
        bot.send_message(message.chat.id, f'Твой пол - {real_sex}.')
    bot.send_message(message.chat.id, f'Твои интересы: {", ".join(json.loads(user.interests))}.')

def reg_user(message):
    bot.send_message(message.chat.id, "Какое у тебя будет имя?")
    bot.register_next_step_handler(message, get_first_name)

def get_first_name(message):
    user.first_name = message.text
    bot.send_message(message.chat.id, 'Какая у тебя будет фамилия?')
    bot.register_next_step_handler(message, get_second_name) 

def get_second_name(message):
    user.second_name = message.text
    bot.send_message(message.chat.id, 'Сколько тебе лет?')
    bot.register_next_step_handler(message, get_age)
    
def get_age(message):
    if user.age == None:
        try:
            user.age = int(message.text)
        except:
            bot.reply_to(message, 'Может лучше цифрами введешь?')
            bot.register_next_step_handler(message, get_age)
            return
    bot.send_message(message.chat.id, 'Какого ты пола?')
    bot.register_next_step_handler(message, get_sex)

def get_sex(message):
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
        bot.register_next_step_handler(message, get_sex)
        return

    bot.send_message(message.chat.id, 'В каком городе ты живешь?')
    bot.register_next_step_handler(message, get_city)

def get_city(message):
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

    bot.send_message(message.chat.id, 'Перечисли свои интересы через запятую.')
    bot.register_next_step_handler(message, get_interests)

def get_interests(message):
    interests = [item.strip() for item in message.text.lower().split(',')]
    user.interests = json.dumps(interests, indent=4, ensure_ascii=False)
    cursor.execute("INSERT INTO login_id VALUES(?, ?, ?, ?, ?, ?, ?, ?);", user.get_data())
    connect.commit()
    greet_user(message)
'''=============================='''


'''=============Edit============='''
def edit_profile(message):
    cursor.execute(f"SELECT id, first_name, second_name, age, sex, city, region, interests FROM login_id WHERE id = {message.chat.id}")
    id, f_name, s_name, age, sex, city, region, interests = cursor.fetchone()
    user = models.User(id, f_name, s_name, age, sex, city, region, interests)

    if message.text.lower() in ["и", "имя", "ф", "фамилия", "в", "возраст", "п", "пол", "г", "город", "и", "интересы", "все", "всё", "н", "ничего"]:
        if message.text.lower() in ["и", "имя"]:
            user.first_name = None
            bot.send_message(message.chat.id, "Какое у тебя будет имя?")
            bot.register_next_step_handler(message, edit_first_name)
        elif message.text.lower() in ["ф", "фамилия"]:
            user.second_name = None
            bot.send_message(message.chat.id, 'Какая у тебя будет фамилия?')
            bot.register_next_step_handler(message, edit_second_name)
        elif message.text.lower() in ["в", "возраст"]:
            user.age = None
            bot.send_message(message.chat.id, 'Сколько тебе лет?')
            bot.register_next_step_handler(message, edit_age)
        elif message.text.lower() in ["п", "пол"]:
            user.sex = None
            bot.send_message(message.chat.id, 'Какого ты пола?')
            bot.register_next_step_handler(message, edit_sex)
        elif message.text.lower() in ["г", "город"]:
            user.city = None
            user.region = None
            bot.send_message(message.chat.id, 'В каком городе ты живешь?')
            bot.register_next_step_handler(message, edit_city)
        elif message.text.lower() in ["и", "интересы"]:
            user.interests = None
            bot.register_next_step_handler(message, edit_interests)
        elif message.text.lower() in ["все", "всё"]:
            user = models.User(message.chat.id)
            bot.register_next_step_handler(message, reg_user)
        elif message.text.lower() in ["н", "ничего"]:
            greet_user(message)
            return
    else:
        bot.reply_to(message, "Такого я не знаю.")
        bot.send_message(message.chat.id, 'Напишите что хотите отредактировать.')
        bot.send_message(message.chat.id, 'И - Имя\nФ - Фамилия\nВ - Возраст\nП - Пол\nГ - Город\nИ - Интересы\nВсе - Изменить все\nН - ничего, я передумал')

def edit_first_name(message):
    user.first_name = message.text
    delete_user(message.chat.id)
    cursor.execute("INSERT INTO login_id VALUES(?, ?, ?, ?, ?, ?, ?, ?);", user.get_data())
    connect.commit()
    bot.reply_to(message, 'Понял!')
    back_to_edit(message)

def edit_second_name(message):
    user.second_name = message.text
    delete_user(message.chat.id)
    cursor.execute("INSERT INTO login_id VALUES(?, ?, ?, ?, ?, ?, ?, ?);", user.get_data())
    connect.commit()
    bot.reply_to(message, 'Понял!')
    back_to_edit(message)

def edit_age(message):
    if user.age == None:
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
        bot.register_next_step_handler(message, get_city)
        return
    delete_user(message.chat.id)
    cursor.execute("INSERT INTO login_id VALUES(?, ?, ?, ?, ?, ?, ?, ?);", user.get_data())
    connect.commit()
    bot.reply_to(message, 'Понял!')
    back_to_edit(message)

def edit_interests(message):
    interests = [item.strip() for item in message.text.lower().split(',')]
    user.interests = json.dumps(interests, indent=4, ensure_ascii=False)
    delete_user(message.chat.id)
    cursor.execute("INSERT INTO login_id VALUES(?, ?, ?, ?, ?, ?, ?, ?);", user.get_data())
    connect.commit()
    bot.reply_to(message, 'Понял!')
    back_to_edit(message)

def back_to_edit(message):
    bot.send_message(message.chat.id, 'Хотите еще что-нибудь отредактировать?')
    bot.send_message(message.chat.id, 'И - Имя\nФ - Фамилия\nВ - Возраст\nП - Пол\nГ - Город\nИ - Интересы\nВсе - Изменить все\nН - ничего, я передумал')
    bot.register_next_step_handler(message, edit_profile)
'''=============================='''

bot.polling()