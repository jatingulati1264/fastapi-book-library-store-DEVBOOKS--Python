from bson import ObjectId
from datetime import datetime
import json
from typing import Optional
import re
import smtplib
import shutil
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from fastapi.params import Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from schemas.book import booksEntity, bookEntity
from config.db import conn
from models.book import Book
from utils.auth_util import get_admin_user, SECRET_KEY, ALGORITHM
from jose import jwt

book = APIRouter()

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


@book.get('/', response_class=HTMLResponse)
async def index(request: Request, alert: str = None):
    user = get_user(request)
    token = request.cookies.get('access_token')
    return templates.TemplateResponse('index.html', {
        "request": request,
        "token": token,
        "user": user,
        "alert": alert
    })


@book.get('/mission', response_class=HTMLResponse)
async def mission(request: Request):
    user = get_user(request)
    token = request.cookies.get('access_token')
    return templates.TemplateResponse('mission.html', {
        "request": request,
        "token": token,
        "user": user
    })


@book.get('/about-us', response_class=HTMLResponse)
async def about(request: Request):
    user = get_user(request)
    token = request.cookies.get('access_token')
    return templates.TemplateResponse('aboutus.html', {
        "request": request,
        "token": token,
        "user": user
    })


@book.get('/reading-guides', response_class=HTMLResponse)
async def reading_guides(request: Request):
    user = get_user(request)
    token = request.cookies.get('access_token')
    return templates.TemplateResponse('reading-guides.html', {
        "request": request,
        "token": token,
        "user": user
    })


@book.get('/author-interviews', response_class=HTMLResponse)
async def author_interviews(request: Request):
    user = get_user(request)
    token = request.cookies.get('access_token')
    return templates.TemplateResponse('author-interviews.html', {
        "request": request,
        "token": token,
        "user": user
    })


@book.get('/create-book', response_class=HTMLResponse)
async def show_books_created(request: Request):
    user = get_user(request)
    token = request.cookies.get('access_token')
    return templates.TemplateResponse('createbook.html', {
        "request": request,
        "token": token,
        "user": user
    })


@book.post('/create-book')
async def create_book(
        request: Request,
        title: str = Form(...),
        author: str = Form(...),
        description: str = Form(...),
        available_copies: int = Form(...),
        total_copies: int = Form(...),
        price: float = Form(...),
        book_image: UploadFile = File(None),
        admin: dict = Depends(get_admin_user)
):
    image_url = "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&q=80"

    if book_image and book_image.filename:
        upload_dir = "static/uploads"
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, book_image.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(book_image.file, buffer)

        image_url = f"/{file_path}"

    data = {
        'book_title': title,
        'book_author': author,
        'book_description': description,
        'book_available_copies': available_copies,
        'book_total_copies': total_copies,
        'book_price': price,
        'images': [image_url, image_url, image_url]
    }

    validate = Book(**data)

    inserted_data = conn.books.books.insert_one(dict(validate))
    if not inserted_data:
        raise HTTPException(status_code=400, detail={"message": "Failed to add the book"})

    return RedirectResponse(url='/books?alert=created-success', status_code=303)


@book.get('/delete/{id}')
def delete_book(request: Request, id: str, admin: dict = Depends(get_admin_user)):
    deleted_book = conn.books.books.delete_one({"_id": ObjectId(id)})

    if deleted_book:
        return RedirectResponse('/books?alert=deleted', status_code=303)
    raise HTTPException(status_code=404, detail={"message": "Book with id not found"})


@book.get('/delete-all-books')
async def delete_all_books(request: Request, admin: dict = Depends(get_admin_user)):
    conn.books.books.delete_many({})
    return RedirectResponse('/books?alert=all-deleted', status_code=303)


@book.get('/update/{id}', response_class=HTMLResponse)
async def update_book(request: Request, id: str):
    user = get_user(request)
    token = request.cookies.get('access_token')
    existing_record = conn.books.books.find_one({"_id": ObjectId(id)})
    if not existing_record:
        raise HTTPException(status_code=404, detail={"message": "Record not found for given id"})

    return templates.TemplateResponse('updatebook.html', {
        "request": request,
        "id": id,
        "updated_record": existing_record,
        "user": user,
        "token": token
    })


@book.post('/update/{id}')
async def update_book(request: Request, id: str, admin: dict = Depends(get_admin_user)):
    form = await request.form()
    formDict = dict(form)

    updated_data = {
        'book_title': formDict.get('title'),
        'book_author': formDict.get('author'),
        'book_description': formDict.get('description'),
        'book_available_copies': int(formDict.get('available_copies', 0)),
        'book_total_copies': int(formDict.get('total_copies', 0)),
        'book_price': float(formDict.get('price', 0.0)),
    }

    conn.books.books.update_one(
        {"_id": ObjectId(id)},
        {"$set": updated_data}
    )

    return RedirectResponse(url='/books?alert=updated', status_code=303)


@book.get('/add-cartitem', response_class=HTMLResponse)
async def show_cart(request: Request, alert: str = None):
    token = request.cookies.get("access_token")
    user = get_user(request)
    if not user:
        return RedirectResponse('/users/login', status_code=303)

    cart_items = conn.books.carts.find({"user_id": user["user_id"]})
    all_books = list(cart_items)
    for item in all_books:
        item['book_price'] = int(item['book_price'])
        item['qunatity'] = int(item.get('quantity', 1))
    total = sum(item['book_price'] * item['quantity'] for item in all_books)
    return templates.TemplateResponse('add-cartitem.html', {
        "request": request,
        "all_books": all_books,
        "total_price": total,
        "token": token,
        "user": user,
        "alert": alert
    })


@book.get('/add-cartitem/{id}')
async def add_to_cart(id: str, request: Request):
    user = get_user(request)
    if not user:
        return RedirectResponse('/users/login', status_code=303)
    target_book = conn.books.books.find_one({"_id": ObjectId(id)})
    if not target_book:
        raise HTTPException(status_code=404, detail="Book Not Found!")

    existing_cart_item = conn.books.carts.find_one({
        "user_id": user["user_id"],
        "book_original_id": id
    })

    if existing_cart_item:
        conn.books.carts.update_one(
            {"_id": existing_cart_item["_id"]},
            {"$inc": {"quantity": 1}}
        )
    else:
        new_item = {
            "user_id": user["user_id"],
            "book_original_id": id,
            "book_title": target_book["book_title"],
            "book_author": target_book["book_author"],
            "book_price": int(target_book["book_price"]),
            "quantity": 1
        }
        conn.books.carts.insert_one(new_item)

    return RedirectResponse('/add-cartitem?alert=item-added-to-cart', status_code=303)


@book.get('/remove-cart/{id}')
async def remove_cart(id: str, request: Request):
    user = get_user(request)
    if not user:
        return RedirectResponse('/user/login', status_code=303)

    conn.books.carts.delete_one({"_id": ObjectId(id)})
    return RedirectResponse('/add-cartitem?alert=deleted', status_code=303)


@book.get('/update-quantity/{cart_id}/{action}')
async def update_quantity(cart_id: str, action: str):
    if action == "plus":
        conn.books.carts.update_one({"_id": ObjectId(cart_id)}, {"$inc": {"quantity": 1}})
    elif action == "minus":
        conn.books.carts.update_one(
            {"_id": ObjectId(cart_id), "quantity": {"$gt": 1}},
            {"$inc": {"quantity": -1}}
        )
    return RedirectResponse(url='/add-cartitem', status_code=303)


@book.get('/checkout')
async def checkout(request: Request):
    token = request.cookies.get('access_token')
    user = get_user(request)
    if not user:
        return RedirectResponse('/users/login', status_code=303)

    cart_items = list(conn.books.carts.find({"user_id": user["user_id"]}))
    total_price = sum(int(item['book_price']) * int(item['quantity']) for item in cart_items)
    if not total_price:
        return RedirectResponse('/add-cartitem', status_code=303)

    return templates.TemplateResponse('checkoutpage.html', {
        "request": request,
        "user": user,
        "token": token,
        "all_books": cart_items,
        "total_price": total_price
    })


@book.get('/order-success', response_class=HTMLResponse)
async def order_success(request: Request):
    token = request.cookies.get("access_token")
    user = get_user(request)
    return templates.TemplateResponse('order-success.html', {
        "request": request,
        "token": token,
        "user": user
    })


@book.post('/place-order')
async def place_order(request: Request):
    user = get_user(request)
    if not user:
        return RedirectResponse('/users/login', status_code=303)

    form = await request.form()
    street = form.get('street_address', '')
    city = form.get('city', '')
    state = form.get('state', '')
    zip_code = form.get('zip', '')
    full_address = f"{street}, {city}, {state} {zip_code}"

    cart_items = list(conn.books.carts.find({"user_id": user["user_id"]}))

    if not cart_items:
        return RedirectResponse('/books', status_code=303)

    total_price = sum(int(item['book_price']) * int(item['quantity']) for item in cart_items)

    order_data = {
        "user_id": user["user_id"],
        "items": cart_items,
        "total_amount": total_price,
        "status": "Pending",
        "shipping_address": full_address,
        "order_date": datetime.utcnow()
    }

    conn.books.orders.insert_one(order_data)
    conn.books.carts.delete_many({"user_id": user["user_id"]})

    return RedirectResponse('/order-success', status_code=303)


@book.get('/my-orders', response_class=HTMLResponse)
async def my_orders(request: Request):
    user = get_user(request)
    token = request.cookies.get("access_token")
    if not user:
        return RedirectResponse('/users/login', status_code=303)

    orders_data = conn.books.orders.find({"user_id": user["user_id"]}).sort("order_date", -1)
    orders = list(orders_data)

    current_time = datetime.utcnow()

    for order in orders:
        order['can_cancel'] = False
        order['remaining_seconds'] = 0

        order_date = order.get('order_date')
        status = order.get('status', 'Pending')

        if order_date:
            time_diff = current_time - order_date
            seconds_elapsed = time_diff.total_seconds()

            if seconds_elapsed <= 300:
                order['can_cancel'] = True
                order['remaining_seconds'] = int(300 - seconds_elapsed)
            else:
                if seconds_elapsed > 3600:
                    status = "Dispatched"
                elif seconds_elapsed > 300:
                    status = "Processing"

        order['status'] = status

    return templates.TemplateResponse('my-orders.html', {
        "request": request,
        "token": token,
        "orders": orders,
        "user": user
    })


@book.get('/orders/cancel/{order_id}')
async def cancel_order(order_id: str, request: Request):
    user = get_user(request)
    if not user:
        return RedirectResponse('/users/login', status_code=303)

    if not order_id or len(order_id) != 24:
        raise HTTPException(status_code=400, detail={"message": "Invalid Order ID."})

    order = conn.books.orders.find_one({"_id": ObjectId(order_id), "user_id": user["user_id"]})

    if not order:
        return RedirectResponse(url='/my-orders', status_code=303)

    order_date = order.get('order_date')
    if order_date:
        time_diff = datetime.utcnow() - order_date
        if time_diff.total_seconds() > 300:
            return RedirectResponse(url='/my-orders', status_code=303)

    conn.books.orders.delete_one({
        "_id": ObjectId(order_id),
        "user_id": user["user_id"]
    })

    return RedirectResponse(url='/my-orders', status_code=303)


@book.post('/orders/update-address')
async def update_order_address(request: Request):
    user = get_user(request)
    if not user:
        return RedirectResponse('/users/login', status_code=303)

    form = await request.form()
    formDict = dict(form)
    order_id = formDict.get('order_id')

    if not order_id or order_id.strip() == "":
        raise HTTPException(status_code=400, detail={"message": "Order ID is missing."})

    address_line_1 = formDict.get('addressLine1')
    address_line_2 = formDict.get('addressLine2', '')
    city = formDict.get('city')
    pincode = formDict.get('pincode')

    full_address = f"{address_line_1}"
    if address_line_2:
        full_address += f", {address_line_2}"
    full_address += f", {city}, {pincode}"

    conn.books.orders.update_one(
        {"_id": ObjectId(order_id), "user_id": user["user_id"]},
        {"$set": {"shipping_address": full_address}}
    )

    return RedirectResponse(url='/my-orders', status_code=303)


@book.get('/contact', response_class=HTMLResponse)
async def contact_page(request: Request, alert: Optional[str] = None):
    user = get_user(request)
    token = request.cookies.get('access_token')
    return templates.TemplateResponse('contact.html', {
        "request": request,
        "token": token,
        "user": user,
        "alert": alert
    })


@book.post('/contact/submit')
async def submit_contact_form(request: Request):
    form = await request.form()
    first_name = form.get('first_name', '')
    last_name = form.get('last_name', '')
    sender_email = form.get('email', '')
    subject = form.get('subject', '')
    message = form.get('message', '')

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    SENDER_GMAIL = "jatingulati1261@gmail.com"
    GMAIL_APP_PASSWORD = "your_app_password_here"

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_GMAIL
        msg['To'] = "jatingulati1261@gmail.com"
        msg['Subject'] = f"[DevBooks Contact] {subject} (from {first_name} {last_name})"

        email_body = f"""
        You have received a new message from your DevBooks Contact Form:

        Name: {first_name} {last_name}
        Email: {sender_email}
        Subject: {subject}

        Message:
        {message}
        """

        msg.attach(MIMEText(email_body, 'plain'))

        server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        server.starttls()
        server.login(SENDER_GMAIL, GMAIL_APP_PASSWORD)
        server.sendmail(SENDER_GMAIL, "jatingulati1261@gmail.com", msg.as_string())
        server.quit()

        return RedirectResponse('/contact?alert=success', status_code=303)

    except Exception as e:
        print(f"Email sending failed: {e}")
        return RedirectResponse('/contact?alert=error', status_code=303)


@book.get('/faq', response_class=HTMLResponse)
async def faq_page(request: Request):
    user = get_user(request)
    token = request.cookies.get('access_token')
    return templates.TemplateResponse('faq.html', {
        "request": request,
        "token": token,
        "user": user
    })


@book.get('/tracking')
async def tracking_redirect(request: Request):
    return RedirectResponse('/my-orders', status_code=303)


@book.get('/books', response_class=HTMLResponse)
async def get_all_books(request: Request, category: Optional[str] = None, alert: Optional[str] = None):
    user = get_user(request)
    token = request.cookies.get("access_token")

    query = {}

    if category:
        if category == 'backend':
            keywords = "backend|python|fastapi|django|node|express|api|database|sql|mongo"
        elif category == 'frontend':
            keywords = "frontend|react|angular|vue|css|html|javascript|ui|ux|web"
        elif category == 'devops':
            keywords = "devops|docker|kubernetes|aws|cloud|ci/cd|linux|deploy|server"
        else:
            keywords = category

        query = {
            "$or": [
                {"book_title": {"$regex": keywords, "$options": "i"}},
                {"book_description": {"$regex": keywords, "$options": "i"}}
            ]
        }

    books_data = conn.books.books.find(query)
    all_books = booksEntity(books_data)

    return templates.TemplateResponse('books.html', {
        "request": request,
        "token": token,
        "new_books": all_books,
        "user": user,
        "alert": alert
    })


@book.post('/upload-books')
async def upload_books(request: Request, file: UploadFile = File(...)):
    user = get_user(request)

    if not user or user.get('user_type') != 'Admin':
        raise HTTPException(status_code=403, detail="Unauthorized action!")

    try:
        contents = await file.read()
        books_list = json.loads(contents)

        if not isinstance(books_list, list):
            raise ValueError("The uploaded JSON file must contain an array of objects.")

        records_to_insert = []
        current_date = datetime.utcnow().strftime("%Y-%m-%d")

        for item in books_list:
            records_to_insert.append({
                "book_title": item.get("book_title", item.get("title", "Unknown Title")),
                "book_author": item.get("book_author", item.get("author", "Unknown Author")),
                "book_description": item.get("book_description", item.get("description", "")),
                "book_available_copies": int(item.get("book_available_copies", item.get("available_copies", 0))),
                "book_total_copies": int(item.get("book_total_copies", item.get("total_copies", 0))),
                "book_price": float(item.get("book_price", item.get("price", 0.0))),
                "images": item.get("images", ["https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&q=80"]),
                "book_created_at": current_date
            })

        if records_to_insert:
            conn.books.books.insert_many(records_to_insert)

        return RedirectResponse('/books?alert=created-success', status_code=303)

    except Exception as e:
        print(f"Error processing JSON upload: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON format or missing data: {str(e)}")


@book.get('/books/{id}', response_class=HTMLResponse)
async def view_book_details(request: Request, id: str, alert: Optional[str] = None):
    user = get_user(request)
    token = request.cookies.get("access_token")

    raw_book = conn.books.books.find_one({"_id": ObjectId(id)})
    if not raw_book:
        raise HTTPException(status_code=404, detail="Book not found")

    book_data = bookEntity(raw_book)

    comments_cursor = conn.books.comments.find({"book_id": id}).sort("created_at", -1)
    comments = list(comments_cursor)

    avg_rating = 0
    if comments:
        total_stars = sum(int(c.get("rating", 5)) for c in comments)
        avg_rating = round(total_stars / len(comments), 1)

    return templates.TemplateResponse('book-details.html', {
        "request": request,
        "token": token,
        "user": user,
        "book": book_data,
        "comments": comments,
        "avg_rating": avg_rating,
        "alert": alert
    })


@book.post('/books/{id}/comment')
async def add_book_comment(request: Request, id: str):
    user = get_user(request)
    if not user:
        return RedirectResponse('/users/login', status_code=303)

    form = await request.form()

    comment_data = {
        "book_id": id,
        "user_id": user["user_id"],
        "user_name": user["user_name"],
        "rating": int(form.get("rating", 5)),
        "review_text": form.get("review_text", ""),
        "created_at": datetime.utcnow().strftime("%B %d, %Y")
    }

    conn.books.comments.insert_one(comment_data)

    return RedirectResponse(f'/books/{id}?alert=review-added', status_code=303)


@book.get('/books/comment/edit/{comment_id}', response_class=HTMLResponse)
async def edit_comment_page(request: Request, comment_id: str):
    user = get_user(request)
    if not user:
        return RedirectResponse('/users/login', status_code=303)

    comment = conn.books.comments.find_one({"_id": ObjectId(comment_id)})
    if not comment or comment.get("user_id") != user["user_id"]:
        raise HTTPException(status_code=403, detail="Unauthorized action")

    token = request.cookies.get('access_token')
    return templates.TemplateResponse('edit-comment.html', {
        "request": request,
        "comment": comment,
        "token": token,
        "user": user
    })


@book.post('/books/comment/edit/{comment_id}')
async def update_comment(request: Request, comment_id: str):
    user = get_user(request)
    if not user:
        return RedirectResponse('/users/login', status_code=303)

    comment = conn.books.comments.find_one({"_id": ObjectId(comment_id)})
    if not comment or comment.get("user_id") != user["user_id"]:
        raise HTTPException(status_code=403, detail="Unauthorized action")

    form = await request.form()
    rating = int(form.get("rating", 5))
    review_text = form.get("review_text", "")

    conn.books.comments.update_one(
        {"_id": ObjectId(comment_id)},
        {"$set": {"rating": rating, "review_text": review_text}}
    )

    return RedirectResponse(f"/books/{comment['book_id']}?alert=review-updated", status_code=303)


@book.get('/books/comment/delete/{comment_id}')
async def delete_comment(request: Request, comment_id: str):
    user = get_user(request)
    if not user:
        return RedirectResponse('/users/login', status_code=303)

    comment = conn.books.comments.find_one({"_id": ObjectId(comment_id)})
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.get("user_id") != user["user_id"] and user.get("user_type") != "Admin":
        raise HTTPException(status_code=403, detail="Unauthorized action")

    book_id = comment["book_id"]
    conn.books.comments.delete_one({"_id": ObjectId(comment_id)})

    return RedirectResponse(f"/books/{book_id}?alert=review-deleted", status_code=303)


@book.post('/subscribe')
async def subscribe_newsletter(request: Request):
    form = await request.form()
    email = form.get('email')

    if email:
        # Optional: Save to a 'subscribers' collection in MongoDB if it doesn't already exist
        existing = conn.books.subscribers.find_one({"email": email})
        if not existing:
            conn.books.subscribers.insert_one({
                "email": email,
                "subscribed_at": datetime.utcnow()
            })

    # Redirect back to the homepage with a newsletter success query flag
    return RedirectResponse(url='/?alert=subscribed', status_code=303)