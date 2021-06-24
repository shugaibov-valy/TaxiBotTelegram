# libraries for bot

import telebot
from telebot import types
import sqlite3
import math
import sys
from io import BytesIO
import requests
from PIL import Image


# python files functions

from geocoder_coords import coords_to_address, addess_to_coords
from static_map_passengers import create_static_map_order     # get static map geopos for choose order


# TOKEN for bot

token = "1892369905:AAErBKLVAT95cNV7oLTzrTmxjhEM4fvEMNE"
bot = telebot.TeleBot(token)


@bot.message_handler(commands=["start"])
def start(message):
    name = message.text
    bot.send_message(message.chat.id, "Привет <b>{first_name}</b>, рад тебя видеть. Пожалуйста, отправьте мне свой номер для этого есть команда /phone".format(first_name=message.from_user.first_name), parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=["phone"])
def phone(message):
    user_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)   
    user_markup.add(button_phone)
    msg = bot.send_message(message.chat.id, "Согласны ли вы предоставить ваш номер телефона для регистрации в системе?", reply_markup=user_markup)
    bot.register_next_step_handler(msg, reg_or_auth)

    
def reg_or_auth(message):
    try:
        # user phone
        input_phone = message.contact.phone_number    

        # connect to base
        mydb = sqlite3.connect('base.db')
        mycursor = mydb.cursor()
    
        # find phone in passengers table
        mycursor.execute('SELECT * FROM passengers')      
        passengers = mycursor.fetchall()
    
        for user in passengers:
            table_phone = user[1]
            if table_phone == input_phone:   # if user_phone find in passengers table
            
                # keyboard for auth passenger
                buttons_actions = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                button_history_ways = types.KeyboardButton(text="Мои поездки")
                button_add_order = types.KeyboardButton(text="Новая поездка")
                buttons_actions.add(button_history_ways)
                buttons_actions.add(button_add_order)
                mess = bot.send_message(message.chat.id, "Выберите действие.", reply_markup=buttons_actions)
                bot.register_next_step_handler(mess, choose_action_passenger, input_phone, message.chat.id)      
        
                return ''            # stop function
    
    
        mycursor.execute('SELECT * FROM taxi_drivers')      
        drivers = mycursor.fetchall()
        print(drivers)
        for user in drivers:
            table_phone = user[1]
            if table_phone == input_phone:   # if user_phone find in taxi_drivers table
                # keyboard for auth taxi driver
                buttons_actions = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                button_settings = types.KeyboardButton(text="Настройки")
                button_choose_order = types.KeyboardButton(text="Выбрать поездку")
                buttons_actions.add(button_settings)
                buttons_actions.add(button_choose_order)
                mess = bot.send_message(message.chat.id, "Выберите действие.", reply_markup=buttons_actions)
                bot.register_next_step_handler(mess, choose_action_taxi_driver, input_phone, message.chat.id)      
        
                return ''            # stop function
            
        # if table is empty
        buttons_characters = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button_taxi_driver = types.KeyboardButton(text="Таксист")
        button_passenger = types.KeyboardButton(text="Пассажир")
        buttons_characters.add(button_taxi_driver)
        buttons_characters.add(button_passenger)
        mess = bot.send_message(message.chat.id, "Выберите кем вы являетесь?", reply_markup=buttons_characters)
        bot.register_next_step_handler(mess, choose_character, input_phone)      
    
    except:
        mess = bot.send_message(message.chat.id, "Ошибка. Отправьте номер телефона!")
        bot.register_next_step_handler(mess, reg_or_auth)
    
    
@bot.message_handler(content_types=['text'])
def choose_action_passenger(message, user_phone, teg_id):      # auth passenger action
    if message.text == 'Мои поездки':
        
        # connect to base
        mydb = sqlite3.connect('base.db')
        mycursor = mydb.cursor()
    
        # find orders for history orders to passenger
        mycursor.execute('SELECT * FROM orders')      
        orders = mycursor.fetchall()
        
        for order in orders:
            if order[1] == user_phone:

                first_checkpoint = coords_to_address(order[2], order[3])    # start address
                second_checkpoint = coords_to_address(order[4], order[5])   # end address
                bot.send_message(message.chat.id, f"<i><b>Заказ №{order[0]}.</b></i>\n\n<i><b>Начальная точка:</b></i> {first_checkpoint}\n\n<i><b>Конечная точка:</b></i> {second_checkpoint}\n\n<i><b>Расстояние:</b></i> {order[7]} м\n\n<i><b>Время пути:</b></i> {order[8]} мин\n\n<b>Цена:</b> {order[6]} ₽", parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
    
    elif message.text == 'Новая поездка':
        # geolocation new order
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_loca = types.KeyboardButton(text="🌐 Определить местоположение", request_location=True)
        keyboard.add(button_loca)
        mess = bot.send_message(message.chat.id, "Отправьте вашу геолокацию.🌐", reply_markup=keyboard)
        bot.register_next_step_handler(mess, geo_location, user_phone, 'Пассажир')
        

@bot.message_handler(content_types=['text'])
def choose_action_taxi_driver(message, user_phone, teg_id):      # auth taxi driver action
    if message.text == 'Выбрать поездку':

        # connect to base
        mydb = sqlite3.connect('base.db')
        mycursor = mydb.cursor()
        print(user_phone)
        # choose order for taxi driver
        mycursor.execute(f'SELECT * FROM taxi_drivers')
        taxi_drivers = mycursor.fetchall()
        for taxi_driver in taxi_drivers:
            if taxi_driver[1] == user_phone:
                print(taxi_driver)
    
        
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                button_loca = types.KeyboardButton(text="🌐 Определить местоположение", request_location=True)
                keyboard.add(button_loca)
    
                mess = bot.send_message(message.chat.id, "Отправьте вашу геолокацию.🌐", reply_markup=keyboard)
                bot.register_next_step_handler(mess, geo_location, user_phone, 'Таксист', firm=taxi_driver[2], car_numbers=taxi_driver[3], src_photo_car=taxi_driver[-2])
                break

        
        
@bot.message_handler(content_types=['text'])
def choose_character(message, user_phone):      # choose taxi_drivers or passenger
    if message.text == 'Таксист':
        mess = bot.send_message(message.chat.id, "Введите марку машины.", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(mess, machine_firm, user_phone)
        
        
    elif message.text == 'Пассажир':
        
        # connect to base
        mydb = sqlite3.connect('base.db')
        mycursor = mydb.cursor()
            
        # Add new passenger in 'passengers' table
        sqlFormula = "INSERT INTO passengers ('phone', 'teg_id') VALUES (?,?)"
        mycursor.execute(sqlFormula, (user_phone, message.chat.id))
        mydb.commit()
        
        
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_loca = types.KeyboardButton(text="🌐 Определить местоположение", request_location=True)
        keyboard.add(button_loca)
        mess = bot.send_message(message.chat.id, "Отправьте вашу геолокацию.🌐", reply_markup=keyboard)
        bot.register_next_step_handler(mess, geo_location, user_phone, 'Пассажир')

        
@bot.message_handler(content_types=['text'])              # machine_firm
def machine_firm(message, phone):
    firm = message.text
    mess = bot.send_message(message.chat.id, "Введите номера машины.", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(mess, car_numbers, phone, firm)

    
@bot.message_handler(content_types=['text'])             # car_numbers
def car_numbers(message, phone, machine_firm):          
    car_numbers = message.text
    
    mess = bot.send_message(message.chat.id, "Отправьте фото машины.")    
    bot.register_next_step_handler(mess, handle_docs_photo, car_numbers, phone, machine_firm)


@bot.message_handler(content_types=['photo'])    # function for get photo car from user
def handle_docs_photo(message, car_numbers, phone, machine_firm):
    try:
        chat_id = message.chat.id

        file_info = bot.get_file(message.photo[0].file_id)
        
        downloaded_file = bot.download_file(file_info.file_path)

        src = 'photo_cars/' + car_numbers + '.png';     # save png photo name - car_numbers
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
    
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_loca = types.KeyboardButton(text="🌐 Определить местоположение", request_location=True)
        keyboard.add(button_loca)
    
        mess = bot.send_message(message.chat.id, "Отправьте вашу геолокацию.🌐", reply_markup=keyboard)
        bot.register_next_step_handler(mess, geo_location, phone, 'Таксист', firm=machine_firm, car_numbers=car_numbers, src_photo_car=src)
    except:
        pass
    
    
@bot.message_handler(content_types=['text'])
def geo_location(message, phone, job, firm=None, car_numbers=None, src_photo_car=None):   # firm and car_numbers if taxi, default passenger
        latitude = message.location.latitude
        longitude = message.location.longitude
        dict_length = {}

        address_location = coords_to_address(longitude, latitude)     # get address from coords, function file geocoder.py
        bot.send_message(message.chat.id, address_location, reply_markup=types.ReplyKeyboardRemove())
                         
        mydb = sqlite3.connect('base.db')
        mycursor = mydb.cursor()
        
        if job == 'Таксист':
            c = 0
            mycursor.execute(f'SELECT * FROM taxi_drivers')
            taxi_drivers = mycursor.fetchall()
            for driver in taxi_drivers:
                if driver[1] != phone:
                    c += 1
            if c == len(taxi_drivers):
                    
                sqlFormula = "INSERT INTO taxi_drivers ('phone', 'machine_firm', 'car_numbers', 'longitude', 'latitude', 'photo_car', 'teg_id') VALUES (?,?,?,?,?,?,?)"
                mycursor.execute(sqlFormula, (phone, firm, car_numbers, longitude, latitude, src_photo_car, message.chat.id))
                mydb.commit()

                mydb = sqlite3.connect('base.db')
                mycursor = mydb.cursor()

            mycursor.execute(f'SELECT * FROM orders')
            orders = mycursor.fetchall()
            for us in orders:
                user = us
                        
                first_checkpoint = coords_to_address(user[2], user[3])    # start address
                second_checkpoint = coords_to_address(user[4], user[5])   # end address
                bot.send_message(message.chat.id, f"<i><b>Заказ №{user[0]}.</b></i>\n\n<i><b>Начальная точка:</b></i> {first_checkpoint}\n\n<i><b>Конечная точка:</b></i> {second_checkpoint}\n\n<i><b>Расстояние:</b></i> {user[7]} м\n\n<i><b>Время пути:</b></i> {user[8]} мин\n\n<b>Цена:</b> {user[6]} ₽", parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
                
                
            
                
            mess = bot.send_message(message.chat.id, "Введите номер заказа.", parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(mess, choose_order)

         
        elif job == 'Пассажир':
            mess = bot.send_message(message.chat.id, "<b>Куда едем?</b>", parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(mess, where_go, phone, longitude, latitude)

@bot.message_handler(content_types=['text'])
def choose_order(message):   # num order
    num_order = message.text
    mydb = sqlite3.connect('base.db')
    mycursor = mydb.cursor()
    mycursor.execute(f'SELECT * FROM orders')
    users = mycursor.fetchall()
    passenger = []
    for us in users:              # find order in table by id
        if us[0] == int(num_order):
            passenger.append(us)

    first_checkpoint = coords_to_address(passenger[0][2], passenger[0][3])    # start address
    second_checkpoint = coords_to_address(passenger[0][4], passenger[0][5])   # end address
    bot.send_message(message.chat.id, f"<i><b>Номер пассажира: {passenger[0][1]}.</b></i>\n\n<i><b>Начальная точка:</b></i> {first_checkpoint}\n\n<i><b>Конечная точка:</b></i> {second_checkpoint}\n\n<i><b>Расстояние:</b></i> {passenger[0][7]} м\n\n<i><b>Время пути:</b></i> {passenger[0][8]} мин\n\n<b>Цена:</b> {passenger[0][6]} ₽", parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
    
    
    # create map_point.png for choose order
    create_static_map_order(f'{passenger[0][2]},{passenger[0][3]}')
    
    
    # send map_point.png to taxi driver
    bot.send_photo(message.chat.id, open('map_point.png', 'rb'));
    
    
    # send photo taxi_car to passenger
    mydb = sqlite3.connect('base.db')
    mycursor = mydb.cursor()
    mycursor.execute(f'SELECT * FROM taxi_drivers WHERE teg_id={message.chat.id}')
    user_taxi = mycursor.fetchall()
    src_photo_car = user_taxi[0][6]                    # src_photo_car                                       
    
    bot.send_photo(passenger[0][-1], open(src_photo_car, 'rb')); # passenger[0][-1] - teg_id user
    
    sql = 'DELETE FROM orders WHERE id=?'
    mycursor.execute(sql, (int(num_order),))
    mydb.commit()
    
    
@bot.message_handler(content_types=['text'])
def where_go(message, phone, longitude_start, latitude_start):   # end address for passenger
    address_go = message.text
    longitude_end, latitude_end = [float(x) for x in addess_to_coords(address_go).split(' ')]
    
    mess = bot.send_message(message.chat.id, "<b>Укажите желаемую цену в ₽.</b>", parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(mess, price_way, phone, longitude_start, latitude_start, longitude_end, latitude_end)

    
@bot.message_handler(content_types=['text'])
def price_way(message, phone, longitude_start, latitude_start, longitude_end, latitude_end):   # end address for passenger
    price_way = int(message.text)
    
    # length of way
    x1, y1 = longitude_start, latitude_start
    x2, y2 = longitude_end, latitude_end
    
    y = math.radians((y1 + y2) / 2)   
    x = math.cos(y)
    n = abs(x1 - x2) * 111000 * x
    n2 = abs(y1 - y2) * 111000 
    length_way = round(math.sqrt(n * n + n2 * n2))
    #---------------

    # time way
    time_way = round(length_way / (40 * 1000) * 60)
    #--------
    
    first_checkpoint = coords_to_address(longitude_start, latitude_start)
    second_checkpoint = coords_to_address(longitude_end, latitude_end)

    bot.send_message(message.chat.id, f"<i><b>Ваш заказ.</b></i>\n\n<i><b>Начальная точка:</b></i> {first_checkpoint}\n\n<i><b>Конечная точка:</b></i> {second_checkpoint}\n\n<i><b>Расстояние:</b></i> {length_way} м\n\n<i><b>Время пути:</b></i> {time_way} мин\n\n<b>Цена:</b> {price_way} ₽", parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
    
    mydb = sqlite3.connect('base.db')
    mycursor = mydb.cursor()
    sqlFormula = "INSERT INTO orders ('phone', 'longitude_start', 'latitude_start', 'longitude_end', 'latitude_end', 'price', 'length_way', 'time_way', 'teg_id') VALUES (?,?,?,?,?,?,?,?,?)"
    mycursor.execute(sqlFormula, (phone, longitude_start, latitude_start, longitude_end, latitude_end, price_way, length_way, time_way, message.chat.id))
    mydb.commit()
    
            
            
if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)