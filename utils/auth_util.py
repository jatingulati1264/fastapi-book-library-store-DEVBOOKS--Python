from fastapi import Request,HTTPException, status
from jose import jwt
from config.db import conn

SECRET_KEY = 'jatingulati'
ALGORITHM = 'HS256'

async def get_admin_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        user = conn.books.users.find_one({"user_id":user_id})

        if not user or user.get('user_type') != 'Admin':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Admin Privileges required!")
        return user
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")