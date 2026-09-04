import uuid
import shutil
import os

from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from config.db import conn
from models.user import Updated_User
import bcrypt
from jose import jwt
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
async def user_login_get(request: Request, alert: str = None):
    return templates.TemplateResponse('users/login.html', {
        "request": request,
        "token": None,
        "alert": alert
    })


@user.post('/users/login')
async def user_login_post(request: Request):
    form = await request.form()
    formDict = dict(form)

    email = formDict.get('email')
    password = formDict.get('password')

    user_db = conn.books.users.find_one({"user_email": email})

    if not user_db:
        return RedirectResponse('/users/login?alert=user-not-found', status_code=303)

    is_password_hashed = bcrypt.checkpw(
        password.encode('utf-8'),
        user_db.get('user_password').encode('utf-8')
    )

    if not is_password_hashed:
        return RedirectResponse('/users/login?alert=invalid-password', status_code=303)

    token = jwt.encode({"user_id": user_db.get('user_id')}, SECRET_KEY, algorithm=ALGORITHM)

    response = RedirectResponse('/?alert=login-success', status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True, path="/")

    return response


@user.get('/users/create', response_class=HTMLResponse)
async def create_user_get(request: Request):
    return templates.TemplateResponse('users/create.html', {"request": request})


@user.post('/users/create')
async def create_user_post(
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
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
        "user_type": "Student",  # NEW DEFAULT: All public registrations are 'Student'
        "user_avatar": avatar_url,
        "user_created_at": datetime.utcnow().strftime("%Y-%m-%d")
    }

    inserted_data = conn.books.users.insert_one(data)

    if not inserted_data:
        raise HTTPException(status_code=400, detail={"message": "Unable to register the user!"})

    return RedirectResponse('/users/login?alert=register-success', status_code=303)


@user.get('/users/update/{id}', response_class=HTMLResponse)
async def update_user_get(request: Request, id: str):
    token = request.cookies.get("access_token")
    current_user = get_user(request)
    existing_user = conn.books.users.find_one({"user_id": id})

    if not existing_user:
        raise HTTPException(status_code=404, detail={"message": "user not found with given id!"})

    return templates.TemplateResponse('users/update.html', {
        "request": request,
        "id": id,
        "update_record": existing_user,
        "user": current_user,
        "token": token
    })


@user.post('/users/update/{id}')
async def update_user_post(
        request: Request,
        id: str,
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        type: str = Form(None),  # Optional field
        profile_image: UploadFile = File(None)
):
    current_user = get_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

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

    # SECURE ROLE ASSIGNMENT
    final_type = existing_user.get('user_type')
    if current_user.get('user_type') == 'Admin' and type:
        final_type = type

    updated_data = {
        "user_name": name,
        "user_email": email,
        "user_password": final_password,
        "user_type": final_type,
        "user_avatar": avatar_url
    }

    validate = Updated_User(**updated_data)
    if validate:
        conn.books.users.update_one({"user_id": id}, {"$set": updated_data})
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
            token = None

    return templates.TemplateResponse('index.html', {
        "request": request,
        "token": token,
        "user": user_data
    })


@user.get('/users/view-users', response_class=HTMLResponse)
async def view_all_users(request: Request):
    user_data = get_user(request)
    token = request.cookies.get('access_token')
    users = conn.books.users.find({})

    all_users = [{"user_id": i["user_id"], "user_name": i["user_name"], "user_email": i["user_email"],
                  "user_type": i.get("user_type", "Student"), "user_avatar": i.get("user_avatar")} for i in users]

    return templates.TemplateResponse('users/view-users.html', {
        "request": request,
        "token": token,
        "all_users": all_users,
        "user": user_data
    })