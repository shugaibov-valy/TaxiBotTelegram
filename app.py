#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import telebot
from telebot import types
import sqlite3


token = "1330594469:AAHRlk2BdO2JTBNtXyPG3_b29yrW1bcBDqM"
bot = telebot.TeleBot(token)


@bot.message_handler(commands=["start"])
def start(message):
    name = message.text
    bot.send_message(message.chat.id, "Привет {first_name} {last_name}, рад тебя видеть. Пожалуйста, отправьте мне свой номер для этого есть команда /phone".format(first_name=message.from_user.first_name, last_name=message.from_user.last_name))

@bot.message_handler(commands=["phone"])
def phone(message):
    user_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)   
    user_markup.add(button_phone)
    msg = bot.send_message(message.chat.id, "Согласны ли вы предоставить ваш номер телефона для регистрации в системе?", reply_markup=user_markup)
    bot.register_next_step_handler(msg, main_menu)

@bot.message_handler('text')
def main_menu(message):
    # user phone
    user_phone = message.contact.phone_number    
    

if __name__ == '__main__':
    bot.polling(none_stop=True)


# In[ ]:




