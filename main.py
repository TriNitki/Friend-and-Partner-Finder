import telebot
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

class User:
    def __init__(self, id, first_name = None, second_name = None, age = None, sex = None) -> None:
        self.id = id
        self.first_name = first_name
        self.second_name = second_name
        self.age = age
        self.sex = sex
    
    def get_data(self):
        return self.id, self.first_name, self.second_name, self.age, self.sex

#bot
bot_token = os.getenv("bot_token")
bot = telebot.TeleBot(bot_token)

#sqlite3
connect = sqlite3.connect('users.sqlite3', check_same_thread=False)
cursor = connect.cursor()


@bot.message_handler(content_types=['text'])
def main(message):
    global user
    user = User(message.chat.id) # Define user

    # Create new db if it isn't exist
    cursor.execute("""CREATE TABLE IF NOT EXISTS login_id(
        id          INTEGER,
        first_name  STRING,
        second_name STRING,
        age         INTEGER,
        sex         STRING
    )""")
    connect.commit()

    cursor.execute(f"SELECT id FROM login_id WHERE id = {user.id}")
    data = cursor.fetchone()

    '''User commands'''
    if message.text == "/start":
        # greet mew user
        bot.send_message(message.chat.id, f'Привет, {message.chat.username}👋!\
                         \nДобро пожаловать в "DetectyBot"! Этот бот создан для поиска друзей и бизнес партнеров.')
        bot.send_message(message.chat.id, 'Для начала регистрации введите команду /reg. Для полного списка возможностей введите /help.')
    elif message.text == "/reg":
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
            cursor.execute(f"DELETE FROM login_id WHERE id = {user.id}")
            connect.commit()
            bot.send_message(message.chat.id, 'Пользователь был удален.\nДля повторной регистрации воспользуйтесь командой /reg.')
    elif message.text == "/me":
        #greet user if it is exist
        if data == None:
            bot.send_message(message.chat.id, 'Пользователь еще не создан.\nДля регистрации воспользуйтесь командой /reg')
        else:
            greet_user(message)
    elif message.text == "/help":
        #send full list of commands
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
    
def greet_user(message):
    cursor.execute(f"SELECT * FROM login_id")
    id, f_name, s_name, age, sex = cursor.fetchone()
    user = User(id, f_name, s_name, age, sex)
    bot.send_message(message.chat.id, f'Привет, {user.second_name} {user.first_name}. Тебе {user.age} {year_type(user.age)}.')
    
def reg_user(message):
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
    greet_user(message)

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