from sqlalchemy.orm import Session
from typing import Optional
from src.users import models, schemas
from secrets import token_hex
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
def create_user(db: Session, user: schemas.UserCreate) -> Optional[models.tableUser]:
    hashedPassword = generate_password_hash(user.password)
    admin = False
    accessToken = token_hex(6)

    db.user = models.tableUser(login=user.login, password=hashedPassword, is_admin=admin, is_deleted=False, accessToken=accessToken)

    db.add(db.user)
    db.commit()
    db.refresh(db.user)
    return db.user

def get_user_by_login(db: Session, login: str) -> Optional[models.tableUser]:
    db_user = db.query(models.tableUser).filter_by(login=login).first()
    return db_user

def get_user_by_Token(db: Session, accessToken: str) -> Optional[models.tableUser]:
    db_user = db.query(models.tableUser).filter_by(accessToken=accessToken).first()
    return db_user

def get_user_by_DogToken(db: Session, accessDogToken: str) -> Optional[models.DogsUser]:
    db_user = db.query(models.DogsUser).filter_by(accessToken=accessDogToken).first()
    return db_user

def get_user_by_DogId(db: Session, dogid: int) -> Optional[models.DogsUser]:
    db_user = db.query(models.DogsUser).filter_by(dogid=dogid).first()
    return db_user

def is_creator_task(db: Session, user_id: int, task_id: int) -> Optional[models.Tasks]:
    db_user = db.query(models.Tasks).filter_by(id=task_id, upload_user_id=user_id).first()
    return db_user

def get_task_by_Id(db: Session, task_id: int) -> Optional[models.Tasks]:
    db_user = db.query(models.Tasks).filter_by(id=task_id).first()
    return db_user

def get_taken_task(db: Session, user_id: int, task_id: int) -> Optional[models.Responses]:
    db_user = db.query(models.Responses).filter_by(task_id=task_id, do_user_id=user_id).first()
    return db_user

def get_user_by_Id(db: Session, id: str) -> str:
    db_user = db.query(models.tableUser.login).filter_by(id=id).first()
    return db_user[0]

def get_user_by_Admin(db: Session, accessToken: str) -> bool:
    db_user = db.query(models.tableUser.accessToken, models.tableUser.is_admin).filter_by(accessToken=accessToken).first()
    return db_user[1]

def get_user_by_Deleted(db: Session, login: str) -> bool:
    db_user = db.query(models.tableUser.login, models.tableUser.is_deleted).filter_by(login=login).first()
    return db_user[1]
def checkPassword(db: Session, login:str,password: str) -> Optional[models.tableUser]:
    db_user = db.query(models.tableUser).filter_by(login=login).first()
    if (db_user):
        if check_password_hash(db_user.password, password):
            db_user.accessToken = token_hex(6)

            db.commit()
        else:
            db_user = False
    return db_user

def create_dogsuser(db: Session, user: schemas.DogsUserBase) -> schemas.DogsUser:
    accessDogToken = token_hex(6)

    db.user = models.DogsUser(characteristic=user.characteristic, coordinates='', last_send=str(datetime.now()), place=user.place, is_deleted=False, accessToken=accessDogToken, name=user.name, photo=user.photo)

    db.add(db.user)
    db.commit()
    db.refresh(db.user)

    return db.user

def create_task(db: Session, task: schemas.CreateTask) -> Optional[models.Tasks]:
    user = get_user_by_Token(db, task.accessToken)

    db.user = models.Tasks(upload_user_id=user.id, dog_id=task.dog_id, goal=task.goal, done=False)

    db.add(db.user)
    db.commit()
    db.refresh(db.user)

    return db.user

def get_tasks(db: Session, dog_id: int) -> object:
    result = []
    for u in db.query(models.Tasks.id, models.Tasks.upload_user_id, models.Tasks.goal, models.Tasks.done).filter_by(dog_id=dog_id).all():
        user = get_user_by_Id(db, u[1])
        if not(u[3]):
            result.append({"task_id": str(u[0]), "asked_user": user, "goal": str(u[2])})

    return result

def take_task(db: Session, task: schemas.TakeTask) -> Optional[models.Responses]:
    user = get_user_by_Token(db, task.accessToken)

    db.user = models.Responses(do_user_id=user.id, task_id=task.task_id, comment="", photo="")

    db.add(db.user)
    db.commit()
    db.refresh(db.user)

    return db.user

def give_response(db: Session, user_id: int, task: schemas.giveResponse):
    db_user = get_taken_task(db, user_id,  task.task_id)

    db_user.comment = task.comment
    db_user.photo = task.photo

    db.commit()

def get_responses(db: Session, task: schemas.TakeTask) -> object:
    result = []
    for u in db.query(models.Responses.do_user_id, models.Responses.comment, models.Responses.photo).filter_by(task_id=task.task_id).all():
        user = get_user_by_Id(db, u[0])
        result.append({"response_user": user, "comment": u[1], "photo": u[2]})

    return result

def confirm_task(db: Session, task_id: int):
    db_user = get_task_by_Id(db, task_id)

    db_user.done = True

    db.commit()

def get_dogsuser_place(db: Session, place: str) -> object:
    result=[]
    for u in db.query(models.DogsUser.dogid, models.DogsUser.coordinates, models.DogsUser.place).filter_by(place=place, is_deleted=False).all():
        result.append({"dogid": str(u[0]), "coordinates": str(u[1])})
    return result

def get_dogsuser_update(db: Session, dogid: int, coordinates: str):
    db_user = db.query(models.DogsUser).filter_by(dogid=dogid).first()
    db_user.coordinates=coordinates
    db_user.last_send = str(datetime.now())
    db.commit()

def get_dogsuser_Characteristic(db: Session, dogid: int) -> str:
    db_user = db.query(models.DogsUser.dogid, models.DogsUser.characteristic).filter_by(dogid=dogid).first()
    return str(db_user[1])

def coordinates(db: Session, user: schemas.Coordinates) -> schemas.CoordinatesResponse:
    db.user = models.DogsUser(characteristic=user.characteristic, coordinates="52.249958,104.264544", last_send=str(datetime.now()), place=user.place, is_deleted=False)

    return db.user

def dog_status_update(db: Session, dogid: int, delete: bool):
    db_user = db.query(models.DogsUser).filter_by(dogid=dogid).first()
    db_user.is_deleted = delete
    db.commit()

def user_status_update(db: Session, db_user, delete: bool):
    db_user.is_deleted = delete
    db.commit()

def dog_info(db: Session, dogid: int):
    db_user = db.query(models.DogsUser).filter_by(dogid=dogid).first()

    return db_user

def user_admin_update(db: Session, db_user, admin: bool):
    db_user.is_admin = admin
    db.commit()