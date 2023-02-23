import telebot
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
#bot
bot_token = os.getenv("bot_token")
bot = telebot.TeleBot(bot_token)

class User:
    def __init__(self, id, first_name = None, second_name = None, age = None, sex = None) -> None:
        self.id = id
        self.first_name = first_name
        self.second_name = second_name
        self.age = age
        self.sex = sex
    
    def get_data(self):
        return self.id, self.first_name, self.second_name, self.age, self.sex


@bot.message_handler(content_types=['text'])
def start(message):
    connect = sqlite3.connect('users.sqlite3', check_same_thread=False)
    cursor = connect.cursor()
    user = User(message.chat.id)
    cursor.execute("""CREATE TABLE IF NOT EXISTS login_id(
        id          INTEGER,
        first_name  STRING,
        second_name STRING,
        age         INTEGER,
        sex         STRING
    )""")
    connect.commit()

    def greet_user():
        cursor.execute(f"SELECT * FROM login_id")
        users_data = list(cursor.fetchone())
        user = User(users_data[0], users_data[1], users_data[2], users_data[3], users_data[4])
        bot.send_message(message.chat.id, f'Привет, {user.second_name} {user.first_name}. Тебе {user.age} {year_type(user.age)}.')
    
    def fill_form(message):
        bot.send_message(message.chat.id, "Как тебя зовут?")
        bot.register_next_step_handler(message, first_name)

    def first_name(message):
        user.first_name = message.text
        bot.send_message(message.chat.id, 'Какая у тебя фамилия?')
        bot.register_next_step_handler(message, second_name) 

    def second_name(message):
        user.second_name = message.text
        bot.send_message(message.chat.id, 'Сколько тебе лет?')
        bot.register_next_step_handler(message, age)
    
    def age(message):
        if user.age == None:
            try:
                user.age = int(message.text)
            except:
                bot.reply_to(message, 'Может лучше цифрами введешь?')
                bot.register_next_step_handler(message, age)
                return
        cursor.execute("INSERT INTO login_id VALUES(?, ?, ?, ?, ?);", user.get_data())
        connect.commit()
        greet_user()


    if message.text == "/start":
        bot.send_message(message.chat.id, f'Привет, {message.chat.username}👋!\
                         \nДобро пожаловать в "DetectyBot"! Этот бот создан для поиска друзей и бизнес партнеров.')
        bot.send_message(message.chat.id, 'Для начала регистрации введите команду /reg. Для полного списка возможностей введите /help.')
    elif message.text == "/reg":
        cursor.execute(f"SELECT id FROM login_id WHERE id = {user.id}")
        data = cursor.fetchone()

        if data == None:
            #add value in fields
            fill_form(message)
        else:
            bot.send_message(message.chat.id, 'Данный пользователь уже зарегестрирован.')
    elif message.text == "/delete":
        cursor.execute(f"SELECT id FROM login_id WHERE id = {user.id}")
        data = cursor.fetchone()

        if data == None:
            bot.send_message(message.chat.id, 'Пользователь еще не создан.\nДля регистрации воспользуйтесь командой /reg.')
        else:
            cursor.execute(f"DELETE FROM login_id WHERE id = {user.id}")
            connect.commit()
            bot.send_message(message.chat.id, 'Пользователь был удален.\nДля повторной регистрации воспользуйтесь командой /reg.')
    elif message.text == "/me":
        cursor.execute(f"SELECT id FROM login_id WHERE id = {user.id}")
        data = cursor.fetchone()

        if data == None:
            bot.send_message(message.chat.id, 'Пользователь еще не создан.\nДля регистрации воспользуйтесь командой /reg')
        else:
            greet_user()
    elif message.text == "/help":
        bot.send_message(message.chat.id, 'Список комманд:')
        bot.send_message(message.chat.id, '/start - запуск бота\
                         \n/help - список комманд\
                         \n/reg - регистрация\
                         \n/delete - удаление пользователя\
                         \n/me - Приветствие\
                         ')
    else:
        bot.reply_to(message, '🤨')
        bot.send_message(message.chat.id, 'Не понял.\nДля начала регистрации введите команду /start.')
    

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