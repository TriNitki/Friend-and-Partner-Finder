import sqlite3
import json

import models

connect = sqlite3.connect('users.sqlite3', check_same_thread=False)
cursor = connect.cursor()

def delete_user(id):
    cursor.execute(f"DELETE FROM login_id WHERE id = {id}")
    connect.commit()

def check_city(new_city):
    with open ('russia.json', 'r', encoding='utf-8') as f:
        cities = json.loads(f.read())
    
    for city in cities:
        if city["city"] == new_city:
            return {'city': city["city"], 'region': city["region"]}
    return False

def define_user(message):
    cursor.execute(f"SELECT id, first_name, second_name, age, sex, city, region, interests FROM login_id WHERE id = {message.chat.id}")
    id, f_name, s_name, age, sex, city, region, interests = cursor.fetchone()
    user = models.User(id, f_name, s_name, age, sex, city, region, interests)
    return user

def year_type(age):
    if (age % 100 >= 11) and (age % 100 <= 14):
        return 'лет'
    elif age % 10 == 1:
        return 'год'
    elif age % 10 in [2, 3, 4]:
        return 'года'
    else:
        return 'лет'