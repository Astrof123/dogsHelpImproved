from fastapi.testclient import TestClient
import re
import random

from main import app

client = TestClient(app)

# Дополнительные функции

def getTokenAdmin():
    response = client.post("/user/login", json={
        "login": 'BigAdmin',
        "password": "qwerty"
    })

    if (response.status_code == 400):
        response = client.post("/user/register", json={
            "login": 'BigAdmin',
            "password": "qwerty"
        })

    return response.json()["accessToken"]

def doAdmin(login):
    token = getTokenAdmin()

    response = client.post("/user/changeAdmin", json={
        "accessToken": token,
        "changed_user_login": login,
        "admin": True
    })

def getAccessToken():
    names = ["vasya", "glebby", "maxy", "danny"]
    rand_login = names[random.randint(0, 3)] + str(random.randint(1000, 10000))
    response = client.post("/user/register", json={
        "login": rand_login,
        "password": "qwerty"
    })
    while (response.status_code!=200):
        rand_login = names[random.randint(0, 3)] + str(random.randint(1000, 10000))
        response = client.post("/user/register", json={
            "login": rand_login,
            "password": "qwerty",
        })

    doAdmin(rand_login)
    return response.json()["accessToken"]
def getAccessTokennotAdmin():
    names = ["kekorik", "krosh", "ejik", "kopatuch"]
    rand_login = names[random.randint(0, 3)] + str(random.randint(1000, 10000))
    response = client.post("/user/register", json={
        "login": rand_login,
        "password": "qwerty"
    })
    while (response.status_code!=200):
        rand_login = names[random.randint(0, 3)] + str(random.randint(1000, 10000))
        response = client.post("/user/register", json={
            "login": rand_login,
            "password": "qwerty",
        })

    return response.json()["accessToken"]

def getDogId():
    token = getAccessToken()

    response = client.post("/dogs/register", json={
        "accessToken": token,
        "characteristic": "123",
        "place": "Irkutsk",
        'photo': 'dog.img',
        'name': 'Черепокрушитель'
    })
    return response.json()["dogid"]
def getLogin():
    names = ["vasya", "glebby", "maxy", "danny"]
    rand_login = names[random.randint(0, 3)] + str(random.randint(1000, 10000))
    response = client.post("/user/register", json={
        "login": rand_login,
        "password": "qwerty",
    })

    doAdmin(rand_login)
    return rand_login
def getPlace():
    token = getAccessToken()
    pl=["Иркутск","Шелехов","Ангарск"]
    place=pl[random.randint(0, 2)]
    response = client.post("/dogs/register", json={
        "accessToken": token,
        "characteristic": "123",
        "place": place,
        'photo': 'dog.img',
        'name': 'Черепокрушитель'
    })

    return place
def getDogID_AND_accessDogToken():
     token = getAccessToken()

     response = client.post("/dogs/register", json={
         "accessToken": token,
         "characteristic": "123",
         "place": "Irkutsk",
         'photo': 'dog.img',
         'name': 'Черепокрушитель'
     })
     res=[response.json()["dogid"],response.json()["accessDogToken"]]
     return res

def getTaskId():
    token = getAccessToken()
    dogid = getDogId()

    response = client.post("/dogs/task/create", json={
            "accessToken": token,
            "dog_id": dogid,
            "goal": "negr2"
    })

    return response.json()["task_id"]
def getTakeTask():
    token = getAccessToken()
    taskid = getTaskId()

    response = client.post("/dogs/task/take", json={
            "accessToken": token,
            "task_id": taskid
    })

    return [token, taskid]
def getCreateTask():
    token = getAccessToken()
    dogid = getDogId()

    response = client.post("/dogs/task/create", json={
            "accessToken": token,
            "dog_id": dogid,
            "goal": "negr2"
    })

    return [token, response.json()['task_id']]

# Регистрация пользователя
def test_AdminCorrect():
    login=getLogin()
    token = getTokenAdmin()
    response = client.post("/user/changeAdmin", json={
        "accessToken": token,
        "changed_user_login": login,
        "admin": True
    })
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_AdminError():
    login = getLogin()
    token = getAccessTokennotAdmin()
    response = client.post("/user/changeAdmin", json={
        "accessToken": token,
        "changed_user_login": login,
        "admin": True
    })

    assert response.status_code == 400


def test_AdminUserError():
    token = getTokenAdmin()
    response = client.post("/user/changeAdmin", json={
        "accessToken": token,
        "changed_user_login": "kjgfsdlkjgfdkjdgf",
        "admin": True
    })

    assert response.status_code == 400

def test_AdminUserAdminError():
    token = getTokenAdmin()
    login = getLogin()

    response = client.post("/user/changeAdmin", json={
        "accessToken": 'efwjfiuwehfuiwe',
        "changed_user_login": login,
        "admin": True
    })

    assert response.status_code == 400

def test_register_user_correct():
    names = ["vasya", "glebby", "maxy", "danny"]
    rand_login = names[random.randint(0, 3)] + str(random.randint(1000, 10000))
    response = client.post("/user/register", json={
        "login": rand_login,
        "password": "qwerty",
    })

    assert response.status_code == 200
    assert response.json()["success"] == True
    assert re.match(r'[\da-zA-Z]{12}', response.json()["accessToken"]) is not None


# Регистрация гав-гавыча

def test_register_dog_correct():
    token = getAccessToken()

    response = client.post("/dogs/register", json={
            "accessToken": token,
            "characteristic": "Добрый гав-гавыч по имени Черепокрушитель",
            "place": "Irkutsk",
            'photo': 'dog.img',
            'name': 'Черепокрушитель'
        })

    assert response.status_code == 200
    assert response.json()["success"] == True

def test_register_dog_wrongToken():

    response = client.post("/dogs/register", json={
            "accessToken": 'wrong',
            "characteristic": "Добрый гав-гавыч по имени Черепокрушитель",
            "place": "Irkutsk",
            'photo': 'dog.img',
            'name': 'Черепокрушитель'
        })

    assert response.status_code == 400

def test_register_dog_wrongTokenAdmin():
    token = getAccessTokennotAdmin()

    response = client.post("/dogs/register", json={
            "accessToken": token,
            "characteristic": "Добрый гав-гавыч по имени Черепокрушитель",
            "place": "Irkutsk",
            'photo': 'dog.img',
            'name': 'Черепокрушитель'
        })

    assert response.status_code == 400

# Тест создания задания

def test_task_create_correct():
    token = getAccessToken()
    dogid = getDogId()

    response = client.post("/dogs/task/create", json={
            "accessToken": token,
            "dog_id": dogid,
            "goal": "negr2"
    })

    assert response.status_code == 200
    assert response.json()["success"] == True

def test_task_create_wrongToken():
    dogid = getDogId()

    response = client.post("/dogs/task/create", json={
            "accessToken": 'sajfewifjewoi',
            "dog_id": dogid,
            "goal": "negr2"
    })

    assert response.status_code == 400

def test_task_create_wrongDogId():
    token = getAccessToken()

    response = client.post("/dogs/task/create", json={
            "accessToken": token,
            "dog_id": 10000,
            "goal": "negr2"
    })

    assert response.status_code == 400

# Тест взятия задания

def test_task_take_correct():
    token = getAccessToken()
    taskid = getTaskId()

    response = client.post("/dogs/task/take", json={
            "accessToken": token,
            "task_id": taskid
    })

    assert response.status_code == 200
    assert response.json()["success"] == True

def test_task_take_wrongToken():
    taskid = getTaskId()

    response = client.post("/dogs/task/take", json={
            "accessToken": '1284u849124',
            "task_id": taskid
    })

    assert response.status_code == 400

def test_task_take_wrongTaskId():
    token = getAccessToken()

    response = client.post("/dogs/task/take", json={
            "accessToken": token,
            "task_id": 190903
    })

    assert response.status_code == 400

def test_task_take_wrongTaker():
    token = getAccessToken()
    taskid = getTaskId()

    response = client.post("/dogs/task/take", json={
            "accessToken": token,
            "task_id": taskid
    })

    response = client.post("/dogs/task/take", json={
            "accessToken": token,
            "task_id": taskid
    })

    assert response.status_code == 400

# Тест приложения отклика

def test_response_give_correct():
    token, taskid = getTakeTask()

    response = client.post("/dogs/task/response/give", json={
            "accessToken": token,
            "task_id": taskid,
            "comment": "Всё сделал как надо",
            "photo": "dog.img"
    })

    assert response.status_code == 200
    assert response.json()["success"] == True

def test_response_give_wrongToken():
    token, taskid = getTakeTask()

    response = client.post("/dogs/task/response/give", json={
            "accessToken": 'reiojgreoigjreoi',
            "task_id": taskid,
            "comment": "Всё сделал как надо",
            "photo": "dog.img"
    })

    assert response.status_code == 400

def test_response_give_wrongTaskId():
    token, taskid = getTakeTask()

    response = client.post("/dogs/task/response/give", json={
            "accessToken": token,
            "task_id": 10000,
            "comment": "Всё сделал как надо",
            "photo": "dog.img"
    })

    assert response.status_code == 400

def test_response_give_wrongCreator():
    token, taskid = getTakeTask()
    tokenFake = getAccessToken()

    response = client.post("/dogs/task/response/give", json={
            "accessToken": tokenFake,
            "task_id": taskid,
            "comment": "Всё сделал как надо",
            "photo": "dog.img"
    })

    assert response.status_code == 400

# Тест просмотров откликов

def test_response_list_correct():
    token, taskid = getCreateTask()

    response = client.post("/dogs/task/response/list", json={
            "accessToken": token,
            "task_id": taskid,
    })

    assert response.status_code == 200
    assert response.json()["success"] == True

def test_response_list_wrongToken():
    token, taskid = getCreateTask()

    response = client.post("/dogs/task/response/list", json={
            "accessToken": '1347812947',
            "task_id": taskid,
    })

    assert response.status_code == 400

def test_response_list_wrongTaskId():
    token, taskid = getCreateTask()

    response = client.post("/dogs/task/response/list", json={
            "accessToken": token,
            "task_id": 100000,
    })

    assert response.status_code == 400

def test_response_list_wrongCreator():
    token, taskid = getCreateTask()
    tokenFake = getAccessToken()

    response = client.post("/dogs/task/response/list", json={
            "accessToken": tokenFake,
            "task_id": taskid,
    })

    assert response.status_code == 400

# Тест подтвердения задания
def test_task_confirm_correct():
    token, taskid = getCreateTask()

    response = client.post("/dogs/task/confirm", json={
            "accessToken": token,
            "task_id": taskid,
            "done": True
    })

    assert response.status_code == 200
    assert response.json()["success"] == True

def test_task_confirm_wrongToken():
    token, taskid = getCreateTask()

    response = client.post("/dogs/task/confirm", json={
            "accessToken": '21312312',
            "task_id": taskid,
            "done": True
    })

    assert response.status_code == 400

def test_task_confirm_wrongTaskId():
    token, taskid = getCreateTask()

    response = client.post("/dogs/task/confirm", json={
            "accessToken": token,
            "task_id": 1000000000,
            "done": True
    })

    assert response.status_code == 400

def test_task_confirm_wrongCreator():
    token, taskid = getCreateTask()
    tokenFake = getAccessToken()

    response = client.post("/dogs/task/confirm", json={
            "accessToken": tokenFake,
            "task_id": taskid,
            "done": True
    })

    assert response.status_code == 400

# Тест получение данные

def test_dog_info_correct():
    token = getAccessToken()
    dogid = getDogId()

    response = client.post("/dogs/info", json={
            "accessToken": token,
            "dog_id": dogid,
        })

    assert response.status_code == 200
    assert response.json()["success"] == True
def test_dog_info_errorAdmin():
    token = getAccessTokennotAdmin()
    dogid = getDogId()

    response = client.post("/dogs/info", json={
            "accessToken": token,
            "dog_id": dogid,
        })

    assert response.status_code == 400

def test_dog_info_wrongToken():
    dogid = getDogId()

    response = client.post("/dogs/info", json={
            "accessToken": 'kfwoifj',
            "dog_id": dogid,
        })

    assert response.status_code == 400


def test_dog_info_wrongDogId():
    token = getAccessToken()

    response = client.post("/dogs/info", json={
            "accessToken": token,
            "dog_id": 10000,
        })

    assert response.status_code == 400

# Тест удаления пользователя

def test_user_changestatus_correct():
    token = getAccessToken()
    loginForDeleted = getLogin()

    response = client.post("/user/changestatus", json={
            "accessToken": token,
            "changed_user_login": loginForDeleted,
            'delete': True
        })
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_user_changestatus_wrongToken():
    tokenForDeleted = getLogin()

    response = client.post("/user/changestatus", json={
            "accessToken": '123123',
            "changed_user_login": tokenForDeleted,
            'delete': True
        })
    assert response.status_code == 400
def test_user_changestatus_errorAdmin():
    token = getAccessTokennotAdmin()
    tokenForDeleted = getLogin()

    response = client.post("/user/changestatus", json={
            "accessToken": token,
            "changed_user_login": tokenForDeleted,
            'delete': True
        })
    assert response.status_code == 400

def test_user_changestatus_wrongLogin():
    token = getAccessToken()

    response = client.post("/user/changestatus", json={
            "accessToken": token,
            "changed_user_login": '1232123',
            'delete': True
        })
    assert response.status_code == 400

# Тест удаления собаки

def test_dog_changestatus_correct():
    token = getAccessToken()
    dogid = getDogId()

    response = client.post("/dogs/changestatus", json={
            "accessToken": token,
            "dogid": dogid,
            'delete': True
        })
    assert response.status_code == 200
    assert response.json()["success"] == True
def test_dog_changestatus_errorAdmin():
    token = getAccessTokennotAdmin()
    dogid = getDogId()

    response = client.post("/dogs/changestatus", json={
            "accessToken": token,
            "dogid": dogid,
            'delete': True
        })
    assert response.status_code == 400
def test_dog_changestatus_wrongToken():
    dogid = getDogId()

    response = client.post("/dogs/changestatus", json={
            "accessToken": '123123',
            "dogid": dogid,
            'delete': True
        })
    assert response.status_code == 400

def test_dog_changestatus_wrongLogin():
    token = getAccessToken()

    response = client.post("/dogs/changestatus", json={
            "accessToken": token,
            "dogid": '1232123',
            'delete': True
        })
    assert response.status_code == 400
def test_dogs_correctupdate():
    resp = getDogID_AND_accessDogToken()
    response = client.post("/dogs/update", json={
            "accessDogToken": resp[1],
            "dogid": resp[0],
            "coordinates": "52.250323, 104.264442"
    })
    assert response.status_code == 200
    assert response.json()["success"] == True
def test_dogs_errortupdate():
    resp = getDogID_AND_accessDogToken()
    response = client.post("/dogs/update", json={
            "accessDogToken": resp[1],
            "dogid": '123123',
            "coordinates": "52.250323, 104.264442"
    })
    assert response.status_code == 400
def test_dogs_errorupdate1():
    resp = getDogID_AND_accessDogToken()
    response = client.post("/dogs/update", json={
            "accessDogToken": '123123',
            "dogid": resp[0],
            "coordinates": "52.250323, 104.264442"
    })
    assert response.status_code == 400


def test_dogs_correctcharacterictic():
    token = getAccessToken()
    dogid = getDogId()

    response = client.post("/dogs/characteristic", json={
        "accessToken": token,
        "dogid": dogid,
    })

    assert response.status_code == 200
    assert response.json()["success"] == True

def test_dogs_errorcharacterictic():
    token = getAccessToken()
    dogid = getDogId()

    response = client.post("/dogs/characteristic", json={
        "accessToken": token,
        "dogid": '123123',
    })

    assert response.status_code == 400
def test_dogs_errorcharacterictic1():
    token = getAccessToken()
    dogid = getDogId()

    response = client.post("/dogs/characteristic", json={
        "accessToken": '123123',
        "dogid": dogid,
    })

    assert response.status_code == 400

def test_user_correctlogin():
    login = getLogin()
    response = client.post("/user/login", json={
        "login": login,
        "password": "qwerty"
    })
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_user_wrongPassword():
    login = getLogin()
    response = client.post("/user/login", json={
        "login": login,
        "password": "erveruivhberuvherui"
    })
    assert response.status_code == 400

def test_user_errorlogin():
    login = getLogin()
    response = client.post("/user/login", json={
        "login": login
    })
    assert response.status_code == 422

def test_user_errorBanned():
    login = getLogin()
    token = getAccessToken()

    response = client.post("/user/changestatus", json={
            "accessToken": token,
            "changed_user_login": login,
            'delete': True
        })

    response = client.post("/user/login", json={
        "login": login,
        "password": "qwerty"
    })
    assert response.status_code == 400

def test_user_correctplace():
    token = getAccessToken()
    place = getPlace()
    response = client.post("/dogs/coordinates", json={
        "accessToken": token,
        "place": place
    })
    assert response.status_code == 200
    assert response.json()["success"] == True
def test_user_errorplace():
    token = getAccessToken()
    place = getPlace()
    response = client.post("/dogs/coordinates", json={
        "accessToken": '123123',
        "place": place
    })
    assert response.status_code == 400
def test_user_correcttaskList():
    token = getAccessToken()
    dogid = getDogId()
    response = client.post("/dogs/task/list", json={
        "accessToken": token,
        "dog_id": dogid
    })
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_error_user_errortaskList():
    dogid = getDogId()
    response = client.post("/dogs/task/list", json={
        "accessToken": '123123',
        "dog_id": dogid
    })
    assert response.status_code == 400

def test_error_user_errortaskList1():
    token = getAccessToken()
    response = client.post("/dogs/task/list", json={
        "accessToken": token,
        "dog_id": 123123
    })
    assert response.status_code == 400

