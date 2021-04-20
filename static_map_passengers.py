import sqlite3
import sys
from io import BytesIO
import requests
from PIL import Image


def create_static_map_order(coords):      # static map geopos for choose passenger
    
    mydb = sqlite3.connect('base.db')    # connect to db
    mycursor = mydb.cursor()          # create cursor
    
    URL = f"https://static-maps.yandex.ru/1.x/?l=map&ll={coords}&pt={coords},pm2rdm&spn=0.004,0.004"
    response = requests.get(URL)
    image = Image.open(BytesIO(
    response.content))
    image.save('map_point.png')