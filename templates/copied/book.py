from idlelib.rpc import request_queue

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from schemas.book import bookEntity, booksEntity

from config.db import conn
from models.book import Book
from utils.auth_util import get_admin_user
from utils.auth_util import SECRET_KEY, ALGORITHM
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
    return templates.TemplateResponse('mission.html',{
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
async def mission(request: Request):
    user = get_user(request)
    token = request.cookies.get('access_token')
    return templates.TemplateResponse('author-interviews.html',{
        "request": request,
        "token": token,
        "user": user
    })


@book.get("/books", response_class=HTMLResponse)
async def get_books(request: Request, alert: str = None):
    token = request.cookies.get('access_token')
    books = conn.books.books.find({})
    new_books = booksEntity(books)   # booksEntity is schema helper method
    return templates.TemplateResponse('books.html', {
        "request": request,
        "token": token,
        "user": get_user(request),
        "new_books": new_books,
        "alert": alert
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
async def create_book(request: Request, admin: dict = Depends(get_admin_user)):
    form = await request.form()
    formDict = dict(form)

    data = {
        'book_title': formDict.get('title'),
        'book_author': formDict.get('author'),
        'book_description': formDict.get('description'),
        'book_available_copies': formDict.get('available_copies'),
        'book_total_copies': formDict.get('total_copies'),
        'book_price': formDict.get('price')
    }


    # Validate your dictionary before inserting in database so that we can bypass it
    # to the model which is a gateway only then book_created_at will automatically comes.
    validate = Book(**data)


    inserted_data = conn.books.books.insert_one(dict(validate))
    if not inserted_data:
        raise HTTPException(status_code=400, detail={"message":"Failed to add the book"})

    return RedirectResponse(url='/books?alert=created-success', status_code=303)


@book.get('/delete/{id}')
def delete_book(request: Request, id: str, admin: dict = Depends(get_admin_user)):
    deleted_book = conn.books.books.delete_one({"_id": ObjectId(id)})

    if deleted_book:
        return RedirectResponse('/books?alert=deleted', status_code=303)
    raise HTTPException(status_code=404, detail={"message": "Book with id not found"})


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
        'book_available_copies': formDict.get('available_copies'),
        'book_total_copies': formDict.get('total_copies'),
        'book_price': formDict.get('price'),
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
        item['book_price']= int(item['book_price'])
        item['qunatity'] = int(item.get('quantity', 1))
    total = sum(item['book_price'] * item['quantity'] for item in all_books)
    return templates.TemplateResponse('add-cartitem.html',{
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
    book = conn.books.books.find_one({"_id": ObjectId(id)})
    if not book:
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
            "book_title": book["book_title"],
            "book_author": book["book_author"],
            "book_price": int(book["book_price"]),
            "quantity": 1
        }
        conn.books.carts.insert_one(new_item)

    return RedirectResponse('/add-cartitem?alert=item-added-to-cart', status_code=303)


@book.get('/remove-cart/{id}')
async def remove_cart(id: str, request: Request):
    token = request.cookies.get("access_token")
    user = get_user(request)
    if not user:
        return RedirectResponse('/user/login', status_code=303)

    result = conn.books.carts.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        print(f"Delete failed: No item found with ID {id}")

    return RedirectResponse('/add-cartitem?alert=deleted', status_code=303)



@book.get('/update-quantity/{cart_id}/{action}')
async def update_quantity(cart_id: str, action: str):
    if action == "plus":
        conn.books.carts.update_one({"_id": ObjectId(cart_id)}, {"$inc": {"quantity": 1}})
    elif action == "minus":
        # Ensures quantity stays at 1 or higher
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

    cart_items = conn.books.carts.find({"user_id": user["user_id"]})
    total_price = sum(int(item['book_price']) * int(item['quantity']) for item in cart_items)
    if not total_price:
        return RedirectResponse('/add-cartitem', status_code=303)

    return templates.TemplateResponse('checkoutpage.html', {
        "request": request,
        "user":user,
        "token": token,
        "all_books": cart_items,
        "total_price": total_price
    })


@book.get('/place-order', response_class=HTMLResponse)
async def order_success(request: Request):
    token = request.cookies.get("access_token")
    return templates.TemplateResponse('checkoutpage.html', {
        "request": request,
        "token": token
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
        return RedirectResponse('/user/login', status_code=303)

    cart_items = list(conn.books.carts.find({"user_id": user["user_id"]}))

    if not cart_items:
        return RedirectResponse('/books', status_code=303)

    total_price = sum(int(item['book_price']) * int(item['quantity']) for item in cart_items)

    order_data = {
        "user_id": user["user_id"],
        "items": cart_items,
        "total_amount": total_price,
        "status": "Pending"
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

    # Fetch orders for this user, sorted by newest first
    orders_data = conn.books.orders.find({"user_id": user["user_id"]}).sort("order_date", -1)
    orders = list(orders_data)

    return templates.TemplateResponse('my-orders.html', {
        "request": request,
        "token": token,
        "orders": orders,
        "user": user
    })