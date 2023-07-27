from fastapi import Cookie, FastAPI, Form, HTTPException, Depends, Response
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .database import SessionLocal, Base, engine
from .user_repo import UserResponse, UserRequest, UsersRepository, UserChangeRequest
from .advertisement_repo import Advert_request, Adverts_repository, Advert, Advert_response
from .comment_repository import Comment_repo, Comment_request, Comment, Comment_response
from typing import List

Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/login")

app = FastAPI()

users_repository = UsersRepository()
adverts_repository = Adverts_repository()
comments_repository = Comment_repo()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def autorization(
    token : str = Depends(oauth2_scheme),
    db : Session = Depends(get_db)
):
    email = users_repository.decode_token(token)
    user = users_repository.get_user_by_email(db, email["email"])
    if user == None:
        raise HTTPException(status_code=401, detail="Not authorized")
    else:
        return (db, email["email"], user)
 
@app.post("/auth/users/", response_model=UserResponse)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
def signup_save(
    user : UserRequest,
    db : Session = Depends(get_db)
):
    user = users_repository.create_user(
        db, user
    )
    return user

@app.post("/auth/users/login")                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
def login(
    username : str = Form(),
    password : str = Form(),
    db : Session = Depends(get_db)
):
    tmp = users_repository.get_user_by_email(db, username)
    if tmp != None and tmp.password == users_repository.encode_email(password):
        shifr_email = users_repository.encode_email(username)
        return {'access_token': shifr_email, 'type': 'bearer'}
    raise HTTPException(status_code=401, detail="Incorrect login or password")

@app.patch("/auth/users/me")
def change_user_data(
    user_new_data : UserChangeRequest,
    tuple_ : tuple = Depends(autorization)
):
    db, email, user = tuple_
    users_repository.update_data(db, email, user_new_data)
    return users_repository.get_user_by_email(db, email)

@app.get("/auth/users/me", response_model=UserResponse)
def get_user(
    tuple_ : tuple = Depends(autorization)
):
    db, email, user = tuple_
    return user

@app.post("/shanyraks/")
def add_advert(
    advert : Advert_request,
    tuple_ : tuple = Depends(autorization)
):
    db, email, user = tuple_
    advert = adverts_repository.add_advert(db, advert, user)
    return {"id" : advert.advert_id}

@app.get("/shanyraks/{id}", response_model=Advert_response)
def get_advert(
    id : int, 
    db = Depends(get_db)
):
    advert = adverts_repository.get_advert(db, id)
    if advert != None:
        count_of_comments = comments_repository.get_count_of_comments(db, id)
        advert.total_comments = count_of_comments
        return advert
    else:
        raise HTTPException(404, "Does not exist such advert")

@app.patch("/shanyraks/{id}")
def change_advert(
    new_data_of_advert : Advert_request,
    id : int,
    tuple_ : tuple = Depends(autorization)
):
    db, email, user = tuple_
    flag = adverts_repository.change_advert(db, id, user, new_data_of_advert)
    if flag:
        raise HTTPException(403, "permission denied")
    return Response("Successfully changed")

@app.delete("/shanyraks/{id}")
def delete_advert(
    id : int,
    tuple_ : tuple = Depends(autorization)
):
    db, email, user = tuple_
    flag = adverts_repository.delete_advert(db, id, user)
    if flag:
        raise HTTPException(403, "permission denied")
    return Response("Successfully deleted")

@app.post("/shanyraks/{id}/comments")
def add_comment(
    id : int,
    comment : Comment_request,
    tuple_ : tuple = Depends(autorization)
):
    db, email, user = tuple_
    comments_repository.add_comment(db, user, id, comment)
    return Response("Successfully added comment")

@app.get("/shanyraks/{id}/comments", response_model=List[Comment_response])
def get_comments(
    id : int,
    db = Depends(get_db)
):
    return comments_repository.get_comments(db, id)

@app.patch("/shanyraks/{id}/comments/{comment_id}")
def change_comment(
    new_data_of_comment : Comment_request,
    id : int,
    comment_id : int,
    tuple_ : tuple = Depends(autorization)
):
    db, email, user = tuple_
    flag = comments_repository.change_comment(db, comment_id, user, id, new_data_of_comment)
    if flag:
        raise HTTPException(403, "permission denied")
    return Response("Successfully changed comment")

@app.delete("/shanyraks/{id}/comments/{comment_id}")
def delete_comment(
    id : int,
    comment_id : int,
    tuple_ : tuple = Depends(autorization)
):
    db, email, user = tuple_
    flag = comments_repository.delete_comment(db, comment_id, id, user)
    if flag:
        raise HTTPException(403, "permission denied")
    return Response("Successfully deleted comment")


        