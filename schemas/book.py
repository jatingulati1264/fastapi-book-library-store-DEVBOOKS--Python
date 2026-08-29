# this function takes a book object from mongo and will convert it to the pythonic dict
def bookEntity(item) -> dict:
    return {
        '_id': item['_id'],
        'book_title': item['book_title'],
        'book_author': item['book_author'],
        'book_description': item['book_description'],
        'book_available_copies': item['book_available_copies'],
        'book_total_copies': item['book_total_copies'],
        'book_price': item['book_price'],
        'images': item.get('images', []),  # <--- ADD THIS LINE HERE
        'book_created_at': item.get('book_created_at', ''),
    }


def booksEntity(items) -> list:
    return [
        bookEntity(item) for item in items
    ]