import telebot
from telebot import types
import sqlite3


token = "1765188979:AAH8__Aetr2x1rxFeRXSP8xGVt3CTSaQ608"
bot = telebot.TeleBot(token)


@bot.message_handler(commands=["start"])
def start(message):
    name = message.text
    bot.send_message(message.chat.id, "Привет {first_name}, рад тебя видеть. Пожалуйста, отправьте мне свой номер для этого есть команда /phone".format(first_name=message.from_user.first_name))

@bot.message_handler(commands=["phone"])
def phone(message):
    user_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)   
    user_markup.add(button_phone)
    msg = bot.send_message(message.chat.id, "Согласны ли вы предоставить ваш номер телефона для регистрации в системе?", reply_markup=user_markup)
    bot.register_next_step_handler(msg, reg_or_auth)

@bot.message_handler('text')
def reg_or_auth(message):
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
        if table_phone == input_phone:   # if user_phone in passengers
            pass
    mycursor.execute('SELECT * FROM taxi_drivers')      
    drivers = mycursor.fetchall()
    for user in drivers:
        table_phone = user[1]
        if table_phone == input_phone:   # if user_phone in taxi_drivers
            pass
    
    # if table is empty
    buttons_characters = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_taxi_driver = types.KeyboardButton(text="Таксист")
    button_passenger = types.KeyboardButton(text="Пассажир")
    buttons_characters.add(button_taxi_driver)
    buttons_characters.add(button_passenger)
    mess = bot.send_message(message.chat.id, "Выберите кем вы являетесь?", reply_markup=buttons_characters)
    bot.register_next_step_handler(mess, choose_character, input_phone)      
        
        
@bot.message_handler('text')
def choose_character(message, user_phone):      # choose taxi_drivers or passenger
    if message.text == 'Таксист':
        mydb = sqlite3.connect('base.db')
        mycursor = mydb.cursor()
        sqlFormula = "INSERT INTO taxi_drivers ('phone', 'machine_firm', 'car_numbers') VALUES (?,?,?)"
        mycursor.execute(sqlFormula, (user_phone, ' ', ' '))
        mydb.commit()
    elif message.text == 'Пассажир':
        mydb = sqlite3.connect('base.db')
        mycursor = mydb.cursor()
        sqlFormula = "INSERT INTO passengers ('phone') VALUES (?)"
        mycursor.execute(sqlFormula, [user_phone])
        mydb.commit()
        
        
if __name__ == '__main__':
    bot.polling(none_stop=True)