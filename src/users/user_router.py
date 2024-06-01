from fastapi import APIRouter, Depends
from src.database import DBSession
import src.users.schemas as schemas
import src.users.crud as crud
from src.dependecies import get_db_session
import src.users.exceptions as exceptions
import logging
import sys

router = APIRouter()

from logging.handlers import TimedRotatingFileHandler

FORMATTER_STRING = "%(asctime)s — %(name)s — %(levelname)s — %(message)s"
FORMATTER = logging.Formatter(FORMATTER_STRING)
LOG_FILE = "./src/tmp/user_router.log"

def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)

    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    logger.addHandler(file_handler)

    return logger

logger = get_logger("user_router_logger")


@router.post("/user/register", response_model=schemas.UserResponse)
async def register_user(user: schemas.UserCreate, db: DBSession = Depends(get_db_session)):
    if crud.get_user_by_login(db, user.login):
        logger.warning(f"POST /user/register — Пользователь {user.login} уже зарегистрирован.")
        raise exceptions.LoginTaken()

    db_user = crud.create_user(db, user)
    response = schemas.UserResponse(success=True, accessToken=db_user.accessToken)

    logger.info(f"POST /user/register — Пользователь {user.login} зарегистрирован.")    
    return response

@router.post("/user/login", response_model=schemas.UserResponse)
async def login_user(user: schemas.UserLogin, db: DBSession = Depends(get_db_session)):
    db_user = crud.checkPassword(db, user.login,user.password)
    if not(db_user):
        logger.warning(f"POST /user/login — Пользователь {user.login} ввел неверный пароль.")
        raise exceptions.IncorrectPassword()
    if (crud.get_user_by_Deleted(db, user.login)):
        logger.warning(f"POST /user/login — Забаненный пользователь {user.login} пытался войти.")
        raise exceptions.UserBanned()

    logger.info(f"POST /user/login — Пользователь {user.login} вошел в аккаунт.")
    return schemas.UserResponse(success=True, accessToken=db_user.accessToken)

@router.post("/dogs/register", response_model=schemas.DogsUser)
async def create_dogsuser(user: schemas.DogsUserBase, db: DBSession = Depends(get_db_session)):
    if not(crud.get_user_by_Token(db, user.accessToken)):
        logger.warning(f"POST /dogs/register — Собаку {user.accessToken[0:5]} пытался зарегистрировать несуществующий пользователь")
        raise exceptions.TokenNotTaken()
    if not(crud.get_user_by_Admin(db, user.accessToken)):
        logger.warning(f"POST /dogs/register — Собаку {user.accessToken[0:5]} пытался зарегистрировать не админ.")
        raise exceptions.AdminNotTaken()
    db_user = crud.create_dogsuser(db, user)

    response = schemas.DogsUser(success=True, dogid=db_user.dogid, accessDogToken=db_user.accessToken)
    logger.info(f"POST /dogs/register — Собака {user.accessToken[0:5]} зарегистрирована.")
    return response

@router.post("/dogs/task/create", response_model=schemas.CreateTaskResponse)
async def create_task(task: schemas.CreateTask, db: DBSession = Depends(get_db_session)):
    if not(crud.get_user_by_Token(db, task.accessToken)):
        logger.warning(f"POST /dogs/task/create — Задание {task.goal[0:6]}... пытался зарегистрировать несуществующий пользователь.")
        raise exceptions.TokenNotTaken()
    if not(crud.get_user_by_DogId(db, task.dog_id)):
        logger.warning(
            f"POST /dogs/task/create — Задание {task.goal[0:6]}... пытались зарегистрировать на несуществующую собаку.")
        raise exceptions.DogNotTaken()
    db_user = crud.create_task(db, task)

    response = schemas.CreateTaskResponse(success=True, task_id=db_user.id)
    logger.info(
        f"POST /dogs/task/create — Задание {db_user.id}... успешно создано.")
    return response

@router.post("/dogs/task/list", response_model=schemas.GetTasksResponse)
async def get_all_task(task: schemas.GetTasks, db: DBSession = Depends(get_db_session)):
    if not(crud.get_user_by_Token(db, task.accessToken)):
        logger.warning(
            f"POST /dogs/task/list — Список заданий пытался получить несуществующий пользователь.")
        raise exceptions.TokenNotTaken()
    if not(crud.get_user_by_DogId(db, task.dog_id)):
        logger.warning(
            f"POST /dogs/task/list — Список заданий пытались получить на несуществующую собаку.")
        raise exceptions.DogNotTaken()

    db_user = crud.get_tasks(db, task.dog_id)

    response = schemas.GetTasksResponse(success=True, tasks=db_user)
    logger.info(
        f"POST /dogs/task/list — Список заданий успешно получен.")
    return response

@router.post("/dogs/task/take", response_model=schemas.TakeTaskResponse)
async def take_task(task: schemas.TakeTask, db: DBSession = Depends(get_db_session)):
    user = crud.get_user_by_Token(db, task.accessToken)
    if not(user):
        logger.warning(
            f"POST /dogs/task/take — Взять задание {task.task_id} пытался несуществующий пользователь.")
        raise exceptions.TokenNotTaken()
    if not(crud.get_task_by_Id(db, task.task_id)):
        logger.warning(
            f"POST /dogs/task/take — Пользователь {user.login} пытался взять несуществующее задание.")
        raise exceptions.TaskNotTaken()
    if crud.get_taken_task(db, user.id, task.task_id):
        logger.warning(
            f"POST /dogs/task/take — Пользователь {user.login} пытался повторно взять задание.")
        raise exceptions.TaskAlreadyTaken()

    crud.take_task(db, task)

    response = schemas.TakeTaskResponse(success=True)
    logger.info(
        f"POST /dogs/task/take — Пользователь {user.login} успешно взял задание {task.task_id}.")
    return response

@router.post("/dogs/task/response/give", response_model=schemas.TakeTaskResponse)
async def give_response_task(task: schemas.giveResponse, db: DBSession = Depends(get_db_session)):
    user = crud.get_user_by_Token(db, task.accessToken)
    if not(user):
        logger.warning(
            f"POST /dogs/task/response/give — Отправить отклик к заданию {task.task_id} пытался несуществующий пользователь.")
        raise exceptions.TokenNotTaken()
    if not(crud.get_task_by_Id(db, task.task_id)):
        logger.warning(
            f"POST /dogs/task/response/give — Пользователь {user.login} пытался отправить отклик к несуществующему заданию.")
        raise exceptions.TaskNotTaken()
    if not(crud.get_taken_task(db, user.id, task.task_id)):
        logger.warning(
            f"POST /dogs/task/response/give — Пользователь {user.login} пытался отправить отклик к заданию, которое не брал.")
        raise exceptions.UserNotTakenTask()

    crud.give_response(db, user.id, task)

    response = schemas.TakeTaskResponse(success=True)
    logger.info(
        f"POST /dogs/task/response/give — Пользователь {user.login} успешно отправил отклик к заданию {task.task_id}.")
    return response

@router.post("/dogs/task/response/list", response_model=schemas.GetResponsesResponse)
async def get_responses(task: schemas.TakeTask, db: DBSession = Depends(get_db_session)):
    user = crud.get_user_by_Token(db, task.accessToken)
    if not(user):
        logger.warning(
            f"POST /dogs/task/response/list — Получить отклики к заданию {task.task_id} пытался несуществующий пользователь.")
        raise exceptions.TokenNotTaken()
    if not(crud.get_task_by_Id(db, task.task_id)):
        logger.warning(
            f"POST /dogs/task/response/list — Пользователь {user.login} пытался получить отклики к несуществующему заданию.")
        raise exceptions.TaskNotTaken()
    if not(crud.is_creator_task(db, user.id, task.task_id)):
        logger.warning(
            f"POST /dogs/task/response/list — Пользователь {user.login} пытался получить отклики к заданию {task.task_id}, не являясь создателем.")
        raise exceptions.CreatorNotTaken()

    response = schemas.GetResponsesResponse(success=True, responses=crud.get_responses(db, task))
    logger.info(
        f"POST /dogs/task/response/list — Пользователь {user.login} успешно получил список откликов.")
    return response

@router.post("/dogs/task/confirm", response_model=schemas.TakeTaskResponse)
async def confirm_task(task: schemas.ConfirmTask, db: DBSession = Depends(get_db_session)):
    user = crud.get_user_by_Token(db, task.accessToken)
    if not(user):
        logger.warning(
            f"POST /dogs/task/confirm — Изменить статус задания {task.task_id} пытался несуществующий пользователь.")
        raise exceptions.TokenNotTaken()
    if not(crud.get_task_by_Id(db, task.task_id)):
        logger.warning(
            f"POST /dogs/task/confirm — Пользователь {user.login} пытался изменить статус несуществующего задания.")
        raise exceptions.TaskNotTaken()
    if not(crud.is_creator_task(db, user.id, task.task_id)):
        logger.warning(
            f"POST /dogs/task/confirm — Пользователь {user.login} пытался изменить статус задания, не являясь создателем.")
        raise exceptions.CreatorNotTaken()

    crud.confirm_task(db, task.task_id)

    response = schemas.TakeTaskResponse(success=True)
    logger.info(
        f"POST /dogs/task/confirm — Пользователь {user.login} успешно изменил статус задания.")
    return response

@router.post("/dogs/coordinates",response_model=schemas.CoordinatesResponse)
async def Сoordinates(user: schemas.Coordinates, db: DBSession = Depends(get_db_session)):
    userByToken = crud.get_user_by_Token(db, user.accessToken)
    if not(userByToken):
        logger.warning(
            f"POST /dogs/coordinates — Получить координаты собак пытался несуществующий пользователь.")
        raise exceptions.TokenNotTaken()
    db_user = schemas.CoordinatesResponse(dogs=crud.get_dogsuser_place(db, user.place),success=True)

    logger.info(
        f"POST /dogs/coordinates — Пользователь {userByToken.login} успешно получил координаты собак.")
    return db_user

@router.post("/dogs/characteristic",response_model=schemas.CharacteristicResponse)
async def Characteristic(user: schemas.Characteristic, db: DBSession = Depends(get_db_session)):
    userByToken = crud.get_user_by_Token(db, user.accessToken)
    if not(userByToken):
        logger.warning(
            f"POST /dogs/characteristic — Получить характеристику собаки {user.dogid} пытался несуществующий пользователь.")
        raise exceptions.TokenNotTaken()
    if not(crud.get_user_by_DogId(db, user.dogid)):
        logger.warning(
            f"POST /dogs/characteristic — Пользователь {userByToken.login} пытался получить характеристику несуществующей собаки.")
        raise exceptions.DogNotTaken()
    db_user = schemas.CharacteristicResponse(success=True, charterictic=crud.get_dogsuser_Characteristic(db, user.dogid))

    logger.info(
        f"POST /dogs/characteristic — Пользователь {userByToken.login} успешно получил характеристику собаки.")
    return db_user

@router.post("/dogs/update", response_model=schemas.DogsUpdateResponse)
async def Update(user: schemas.DogsUpdate, db: DBSession = Depends(get_db_session)):
    if not(crud.get_user_by_DogToken(db, user.accessDogToken)):
        logger.warning(
            f"POST /dogs/update — Отправить координаты пытался несуществующий ошейник.")
        raise exceptions.DogTokenNotTaken()
    if not(crud.get_user_by_DogId(db, user.dogid)):
        logger.warning(
            f"POST /dogs/update — Отправить координаты пытался несуществующий ошейник.")
        raise exceptions.DogNotTaken()
    crud.get_dogsuser_update(db, user.dogid, user.coordinates)
    db_user = schemas.DogsUpdateResponse(success=True)

    logger.info(
        f"POST /dogs/update — Ошейник {user.dogid} успешно отправила координаты.")
    return db_user

@router.post("/dogs/changestatus", response_model = schemas.DogChangeStatusResponse)
async def dog_change_status(user: schemas.DogChangeStatus, db: DBSession = Depends(get_db_session)):
    userByToken = crud.get_user_by_Token(db, user.accessToken)
    if not(userByToken):
        logger.warning(
            f"POST /dogs/changestatus — Статус собаки пытался изменить несуществующий пользователь.")
        raise exceptions.TokenNotTaken()
    if not(crud.get_user_by_Admin(db, user.accessToken)):
        logger.warning(
            f"POST /dogs/changestatus — Статус собаки пытался изменить пользователь {userByToken.login}, не являющийся админом.")
        raise exceptions.AdminNotTaken()
    if not(crud.get_user_by_DogId(db, user.dogid)):
        logger.warning(
            f"POST /dogs/changestatus — Пользователь {userByToken.login} пытался поменять статус несуществующей собаки.")
        raise exceptions.DogNotTaken()
    crud.dog_status_update(db, user.dogid, user.delete)
    db_user = schemas.DogChangeStatusResponse(success=True)

    logger.info(
        f"POST /dogs/changestatus — Статус собаки {user.dogid} успешно изменен админом {user.accessToken[0:5]}.")
    return db_user

@router.post("/user/changestatus", response_model = schemas.UserChangeStatusResponse)
async def user_change_status(user: schemas.UserChangeStatus, db: DBSession = Depends(get_db_session)):
    userByToken = crud.get_user_by_Token(db, user.accessToken)
    if not(userByToken):
        logger.warning(
            f"POST /user/changestatus — Статус пользователя пытался изменить несуществующий пользователь.")
        raise exceptions.TokenNotTaken()
    if not(crud.get_user_by_Admin(db, user.accessToken)):
        logger.warning(
            f"POST /user/changestatus — Статус пользователя пытался изменить пользователь {userByToken.login}, не являющийся админом.")
        raise exceptions.AdminNotTaken()
    check_user = crud.get_user_by_login(db, user.changed_user_login)
    if not(crud.get_user_by_login(db, user.changed_user_login)):
        logger.warning(
            f"POST /user/changestatus — Админ {userByToken.login} пытался поменять статус несуществующего пользователя.")
        raise exceptions.LoginTaken()

    crud.user_status_update(db, check_user, user.delete)
    db_user = schemas.UserChangeStatusResponse(success=True)

    logger.info(
        f"POST /user/changestatus — Статус пользователя {user.changed_user_login} успешно изменен админом {user.accessToken[0:5]}.")
    return db_user

@router.post("/dogs/info", response_model = schemas.DogInfoResponse)
async def dog_info(user: schemas.DogInfo, db: DBSession = Depends(get_db_session)):
    userByToken = crud.get_user_by_Token(db, user.accessToken)
    if not(userByToken):
        logger.warning(
            f"POST /dogs/info — Получить данные ошейника пытался несуществующий пользователь.")
        raise exceptions.TokenNotTaken()
    if not(crud.get_user_by_Admin(db, user.accessToken)):
        logger.warning(
            f"POST /dogs/info — Получить данные ошейника пытался пользователь, не являющийся админом.")
        raise exceptions.AdminNotTaken()
    if not (crud.get_user_by_DogId(db, user.dog_id)):
        logger.warning(
            f"POST /dogs/info — Админ {userByToken.login} пытался получить данные несуществующего ошейника.")
        raise exceptions.DogNotTaken()

    db_user = crud.dog_info(db, user.dog_id)
    db_user = schemas.DogInfoResponse(success=True, lastsend=db_user.last_send, coordinates=db_user.coordinates)

    logger.info(
        f"POST /dogs/info — Данные ошейника {user.dog_id} успешно отправлены.")
    return db_user

@router.post("/user/changeAdmin", response_model = schemas.changeStatusAdminResponse)
async def change_admin(user: schemas.changeStatusAdmin, db: DBSession = Depends(get_db_session)):
    userByToken = crud.get_user_by_Token(db, user.accessToken)
    if not (userByToken):
        logger.warning(
            f"POST /user/changeAdmin — Статус админа пользователя пытался изменить несуществующий пользователь.")
        raise exceptions.TokenNotTaken()
    if userByToken.login != 'BigAdmin':
        logger.warning(
            f"POST /user/changeAdmin — Статус пользователя пытался изменить пользователь {userByToken.login}, не являющийся биг админом.")
        raise exceptions.AdminNotTaken()
    check_user = crud.get_user_by_login(db, user.changed_user_login)
    if not (crud.get_user_by_login(db, user.changed_user_login)):
        logger.warning(
            f"POST /user/changeAdmin — Биг админ пытался поменять статус несуществующего пользователя.")
        raise exceptions.LoginTaken()

    crud.user_admin_update(db, check_user, user.admin)
    db_user = schemas.UserChangeStatusResponse(success=True)

    logger.info(
        f"POST /user/changeAdmin — Статус админа пользователя {user.changed_user_login} успешно изменен.")
    return db_user