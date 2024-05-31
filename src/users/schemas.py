from pydantic import BaseModel

class UserBase(BaseModel):
    login: str

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class UserResponse(BaseModel):
    success: bool
    accessToken: str

    class Config:
        orm_model = True

class DogsUserBase(BaseModel):
    accessToken: str
    characteristic: str
    place: str
    photo: str
    name: str

class DogsUser(BaseModel):
    success: bool
    dogid: int
    accessDogToken: str
    class Config:
        orm_model = True

class CreateTaskResponse(BaseModel):
    success: bool
    task_id: int
    class Config:
        orm_model = True

class CreateTask(BaseModel):
    accessToken: str
    dog_id: int
    goal: str

class GetTasksResponse(BaseModel):
    success: bool
    tasks: object
    class Config:
        orm_model = True

class GetTasks(BaseModel):
    accessToken: str
    dog_id: int

class TakeTaskResponse(BaseModel):
    success: bool
    class Config:
        orm_model = True

class TakeTask(BaseModel):
    accessToken: str
    task_id: int

class giveResponse(BaseModel):
    accessToken: str
    task_id: int
    comment: str
    photo: str

class GetResponsesResponse(BaseModel):
    success: bool
    responses: object
    class Config:
        orm_model = True

class ConfirmTask(BaseModel):
    accessToken: str
    task_id: int
    done: bool

class Coordinates(BaseModel):
    accessToken: str
    place: str

class CoordinatesResponse(BaseModel):
    success: bool
    dogs: object
    class Config:
        orm_model = True

class Characteristic(BaseModel):
    accessToken: str
    dogid: int

class CharacteristicResponse(BaseModel):
    success: bool
    charterictic: str
    class Config:
        orm_model = True

class DogsUpdate(BaseModel):
    accessDogToken: str
    dogid: int
    coordinates: str

class DogsUpdateResponse(BaseModel):
    success: bool
    class Config:
        orm_model = True

class DogChangeStatus(BaseModel):
    accessToken: str
    dogid: int
    delete: bool

class DogChangeStatusResponse(BaseModel):
    success: bool

class UserChangeStatus(BaseModel):
    accessToken: str
    changed_user_login: str
    delete: bool

class UserChangeStatusResponse(BaseModel):
    success: bool

class DogInfo(BaseModel):
    accessToken: str
    dog_id: int

class DogInfoResponse(BaseModel):
    success: bool
    lastsend: str
    coordinates: str

class changeStatusAdmin(BaseModel):
    accessToken: str
    changed_user_login: str
    admin: bool

class changeStatusAdminResponse(BaseModel):
    success: bool
