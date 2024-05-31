import requests
import json
from time import sleep
import random

def requesterReg():
    uri = 'http://127.0.0.1:8001/dogs/register'
    adminToken = input('Введите токен админа: ')
    charact = input('Введите характеристику собаки: ')
    place = input('Введите местоположение собаки: ')
    photo = input('Введите характеристику собаки: ')
    name = input('Введите местоположение собаки: ')

    dates = json.dumps({
            'accessToken': adminToken,
            'characteristic': charact,
            'place': place,
            'photo': photo,
            'name': name
        })

    try:
        response = requests.post(uri, data = dates)
        print(response)
        if (response.status_code == 200):
            jsn = json.loads(response.text)
            return [jsn["success"], jsn['dogid'], jsn['accessDogToken']]
        else:
            print('Ошибка')

    except Exception as exception:
        print(exception)
        exit()


def requesterUpdate(accessDogToken, dog_id, coordinates):
    uri = 'http://127.0.0.1:8001/dogs/update'

    try:
        dates = json.dumps({
            'accessDogToken': accessDogToken,
            'dogid': dog_id,
            "coordinates": coordinates
        })

        response = requests.post(uri, data=dates)
        if (response.status_code == 200):
            jsn = json.loads(response.text)
            return jsn["success"]

    except Exception as exception:
        print(exception)
        exit()


flag = False
while not(flag):
    flag, dog_id, accessDogToken = requesterReg()

coordinatesW = 52.250323
coordinatesD = 143.413123

while True:
    coords = str(coordinatesW) + ', ' + str(coordinatesD)

    requesterUpdate(accessDogToken, dog_id, coords)

    coordinatesW += random.randint(-5, 5)
    coordinatesD += random.randint(-5, 5)

    sleep(60)

flag = False
while not(flag):
    flag, dog_id, accessDogToken = requesterReg()

coordinatesW = '52.250323'
coordinatesD = '143.413123'

while True:
    coordinates = coordinatesW + coordinatesD
    requesterUpdate(accessDogToken, dog_id, coordinates)

    coordinatesW = str(int(coordinatesW) + 1)
    coordinatesD = str(int(coordinatesD) + 1)

    sleep(60)