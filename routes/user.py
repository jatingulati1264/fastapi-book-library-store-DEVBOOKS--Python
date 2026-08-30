# routes for user login and signup
import uuid
import shutil
import os
from os import access

from bson import ObjectId
from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from config.db import conn
from models.user import Register_User, Updated_User
import bcrypt  # to securely hashed passwords
from jose import jwt  # for jwt authentication
from schemas.user import UserEntity, UsersEntity

from datetime import datetime

user = APIRouter()
SECRET_KEY = 'jatingulati'
ALGORITHM = 'HS256'

templates = Jinja2Templates(directory="templates")


def get_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return conn.books.users.find_one({"user_id": payload.get("user_id")})
    except:
        return None


@user.get('/users/login', response_class=HTMLResponse)
async def user_login(request: Request, alert: str = None):
    return templates.TemplateResponse('users/login.html', {
        "request": request,
        "token": None,
        "alert": alert
    })


@user.post('/users/login')
async def user_login(request: Request):
    form = await request.form()
    formDict = dict(form)

    email = formDict.get('email')
    password = formDict.get('password')
    u_type = formDict.get('type')

    user = conn.books.users.find_one({"user_email": email})

    if not user:
        return RedirectResponse('/users/login?alert=user-not-found', status_code=303)

    if u_type != user.get('user_type'):
        return RedirectResponse('/users/login?alert=wrong-type', status_code=303)

    is_password_hashed = bcrypt.checkpw(
        password.encode('utf-8'),
        user.get('user_password').encode('utf-8')
    )

    if not is_password_hashed:
        return RedirectResponse('/users/login?alert=invalid-password', status_code=303)

    token = jwt.encode({"user_id": user.get('user_id')}, SECRET_KEY, algorithm=ALGORITHM)

    response = RedirectResponse('/?alert=login-success', status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True, path="/")

    return response


@user.get('/users/create', response_class=HTMLResponse)
async def create_user(request: Request):
    return templates.TemplateResponse('users/create.html', {"request": request})


@user.post('/users/create')
async def create_user(
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        # Notice we removed the `type: str = Form(...)` parameter completely
        profile_image: UploadFile = File(None)
):
    if conn.books.users.find_one({'user_email': email}):
        raise HTTPException(status_code=400, detail="User already exists!")

    avatar_url = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&q=80"
    if profile_image and profile_image.filename:
        upload_dir = "static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, profile_image.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(profile_image.file, buffer)
        avatar_url = f"/{file_path}"

    hashpw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    user_id = str(uuid.uuid4())
    token = jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm=ALGORITHM)

    data = {
        "user_id": user_id,
        "user_name": name,
        "user_email": email,
        "user_password": hashpw.decode(),
        "token": token,
        "user_type": "Guest",  # HARDCODED: All public registrations are forced to Guest
        "user_avatar": avatar_url,
        "user_created_at": datetime.utcnow().strftime("%Y-%m-%d")
    }

    inserted_data = conn.books.users.insert_one(data)

    if not inserted_data:
        raise HTTPException(status_code=400, detail={"message": "Unable to register the user!"})

    return RedirectResponse('/users/login?alert=register-success', status_code=303)


@user.get('/users/update/{id}', response_class=HTMLResponse)
async def update_user(request: Request, id: str):
    token = request.cookies.get("access_token")
    existing_user = conn.books.users.find_one({"user_id": id})
    if not existing_user:
        raise HTTPException(status_code=404, detail={"message": "user not found with given id!"})
    return templates.TemplateResponse('users/update.html', {
        "request": request,
        "id": id,
        "update_record": existing_user,
        "user": existing_user,
        "token": token
    })


@user.post('/users/update/{id}')
async def update_user(
        request: Request,
        id: str,
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        type: str = Form(...),
        profile_image: UploadFile = File(None)
):
    existing_user = conn.books.users.find_one({"user_id": id})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found!")

    avatar_url = existing_user.get("user_avatar",
                                   "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&q=80")
    if profile_image and profile_image.filename:
        upload_dir = "static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, profile_image.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(profile_image.file, buffer)
        avatar_url = f"/{file_path}"

    new_password = password
    if new_password == existing_user.get('user_password'):
        final_password = new_password
    else:
        final_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

    updated_data = {
        "user_name": name,
        "user_email": email,
        "user_password": final_password,
        "user_type": existing_user.get('user_type'),
        "user_avatar": avatar_url
    }

    validate = Updated_User(**updated_data)
    if validate:
        conn.books.users.update_one(
            {"user_id": id},
            {"$set": updated_data}
        )
        return RedirectResponse('/?alert=updated', status_code=303)
    raise HTTPException(status_code=400, detail={"message": "unable to update!"})


@user.get('/logout')
async def logout(request: Request):
    response = RedirectResponse('/users/login?alert=logged-out', status_code=303)

    response.delete_cookie("access_token", path="/")
    return response


@user.get('/')
async def home(request: Request):
    token = request.cookies.get("access_token")

    user_data = None

    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_data = conn.books.users.find_one({"user_id": payload.get("user_id")})

        except Exception as e:
            print(f"TOKEN ERROR!{e}")
            token = None

        return templates.TemplateResponse('index.html', {
            "request": request,
            "token": token,
            "user": user_data
        })


@user.get('/users/view-users', response_class=HTMLResponse)
async def view_all_users(request: Request):
    user = get_user(request)
    token = request.cookies.get('access_token')
    users = conn.books.users.find({})
    all_users = UsersEntity(users)

    return templates.TemplateResponse('users/view-users.html', {
        "request": request,
        "token": token,
        "all_users": all_users,
        "user": user
    })


@user.post('/users/admin-create')
async def admin_create_user(request: Request):
    current_user = get_user(request)
    if not current_user or current_user.get('user_type') != 'Admin':
        raise HTTPException(status_code=403, detail="Unauthorized action!")

    form = await request.form()
    formDict = dict(form)

    if conn.books.users.find_one({'user_email': formDict.get('email')}):
        raise HTTPException(status_code=400, detail="User already exists!")

    hashpw = bcrypt.hashpw(formDict.get('password').encode(), bcrypt.gensalt())
    user_id = str(uuid.uuid4())
    token = jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm=ALGORITHM)

    data = {
        "user_id": user_id,
        "user_name": formDict.get('name'),
        "user_email": formDict.get('email'),
        "user_password": hashpw.decode(),
        "token": token,
        "user_type": formDict.get('type'),
        "user_avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&q=80",
        "user_created_at": datetime.utcnow().strftime("%Y-%m-%d")
    }

    inserted_data = conn.books.users.insert_one(data)

    if not inserted_data:
        raise HTTPException(status_code=400, detail={"message": "Unable to register the user!"})

    return RedirectResponse('/users/view-users', status_code=303)


@user.get('/users/delete/{id}')
async def delete_user(id: str, request: Request):
    user = conn.books.users.delete_one({"user_id": id})

    if user.deleted_count > 0:
        return RedirectResponse('/users/view-users', status_code=303)

    raise HTTPException(status_code=404, detail="User Detail not found!")


def UserEntity(item) -> dict:
    return {
        "user_id": item["user_id"],
        "user_name": item["user_name"],
        "user_email": item["user_email"],
        "user_password": item["user_password"],
        "user_type": item["user_type"],
        "token": item["token"],
        "user_avatar": item.get("user_avatar",
                                "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&q=80"),
        "user_created_at": item.get("user_created_at", "N/A"),
    }


def UsersEntity(items) -> list:
    return [
        UserEntity(item) for item in items
    ]