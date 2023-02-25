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

'''BOT COMMANDS'''
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
@bot.message_handler(commands=['reg', 'delete', 'me'])
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
            cursor.execute(f"DELETE FROM login_id WHERE id = {message.chat.id}")
            connect.commit()
            bot.send_message(message.chat.id, 'Пользователь был удален.\nДля повторной регистрации воспользуйтесь командой /reg.')
    elif message.text == "/me":
        #greet user if it is exist
        if data == None:
            bot.send_message(message.chat.id, 'Пользователь еще не создан.\nДля регистрации воспользуйтесь командой /reg')
        else:
            greet_user(message)


"Default bot reply"
@bot.message_handler(content_types=['text'])
def non_com(message):
    bot.reply_to(message, '🤨')
    bot.send_message(message.chat.id, 'Не понял.\nДля начала регистрации введите команду /start.')


'''Functions Used'''
def greet_user(message):
    cursor.execute(f"SELECT id, first_name, second_name, age, sex, city, region, interests FROM login_id WHERE id = {message.chat.id}")
    id, f_name, s_name, age, sex, city, region, interests = cursor.fetchone()
    user = models.User(id, f_name, s_name, age, sex, city, region, interests)
    real_sex = {"m": "мужской", "w": "женский", "undef": "секретный"}[user.sex]
    bot.send_message(message.chat.id, f'Привет, {user.second_name} {user.first_name}. Тебе {user.age} {year_type(user.age)}.')
    if user.city != 'undef':
        bot.send_message(message.chat.id, f'Твой пол - {real_sex}. Ты живешь в городе {user.city}, {user.region}')
    else:
        bot.send_message(message.chat.id, f'Твой пол - {real_sex}.')
    bot.send_message(message.chat.id, f'Твои интересы: {", ".join(json.loads(user.interests))}.')

def reg_user(message):
    bot.send_message(message.chat.id, "Как тебя зовут?")
    bot.register_next_step_handler(message, get_first_name)

def get_first_name(message):
    user.first_name = message.text
    bot.send_message(message.chat.id, 'Какая у тебя фамилия?')
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
    if any([message.text.lower() == sex for sex in ['м', 'мужской', 'муж', 'мужик', 'm', 'man']]):
        user.sex = 'm'
    elif any([message.text.lower() == sex for sex in ['ж', 'женский', 'жен', 'девушка', 'женщина', 'w', 'woman']]):
        user.sex = 'w'
    elif any([message.text.lower() == sex for sex in ['п', 'пропустить', 'прапустить', 'не', 'нет', 'u', 'undef', 'undefined']]):
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

def check_city(new_city):
    with open ('russia.json', 'r', encoding='utf-8') as f:
        cities = json.loads(f.read())
    
    for city in cities:
        if city["city"] == new_city:
            return {'city': city["city"], 'region': city["region"]}
    return False

def year_type(age):
    if (age % 100 >= 11) and (age % 100 <= 14):
        return 'лет'
    elif age % 10 == 1:
        return 'год'
    elif age % 10 in [2, 3, 4]:
        return 'года'
    else:
        return 'лет'


bot.polling()