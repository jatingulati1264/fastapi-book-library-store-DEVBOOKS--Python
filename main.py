from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes.book import book, templates
from routes.user import user
from schemas.book import bookEntity, booksEntity

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

def last_four_filter(value):
    return str(value)[-4:]

templates.env.filters["last_four"] = last_four_filter

app.include_router(book)
app.include_router(user)