import requests
import json
from time import sleep

def requesterReg():
    uri = 'http://127.0.0.1:8000/dogs/register'
    adminToken = input('Введите токен админа: ')
    charact = input('Введите характеристику собаки: ')
    place = input('Введите местоположение собаки: ')

    try:
        response = requests.post(uri, data={
            'accessToken': adminToken,
            'characteristic': charact,
            "place": place
        })
        if (response.status_code == 200):
            jsn = json.loads(response.text)
            return [jsn["success"], jsn['dog_id'], jsn['accessDogToken']]
        else:
            print('Ошибка')

    except Exception as exception:
        print(exception)

def requesterUpdate(accessDogToken, dog_id):
    uri = 'http://127.0.0.1:8000/dogs/update'

    try:
        response = requests.post(uri, data={
            'accessDogToken': accessDogToken,
            'dog_id': dog_id,
            "coordinates": coordinates
        })
        if (response.status_code == 200):
            jsn = json.loads(response.text)
            return jsn["success"]
        else:
            return [False, False, False]

    except Exception as exception:
        print(exception)
        exit()



flag = False
while not(flag):
    flag, dog_id, accessDogToken = requesterReg()

coordinatesW = '52.250323'
coordinatesD = '143.413123'

while True:
    requesterUpdate(accessDogToken, dog_id)

    coordinates = ''

    sleep(60)