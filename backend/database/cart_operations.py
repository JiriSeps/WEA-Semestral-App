from .book import Book
from flask import session
from datetime import datetime

def get_formatted_shopping_cart(page=1, per_page=25):
    """
    Gets a formatted list of books in the shopping cart with pagination.
    Returns only visible books from the session.
    """
    # Get cart from session, defaulting to empty list
    cart = session.get('shopping_cart', [])
    
    # Filter only visible books
    try:
        filtered_books = []
        for cart_item in cart:
            book = Book.query.filter(
                (Book.ISBN10 == cart_item['isbn']) | (Book.ISBN13 == cart_item['isbn'])
            ).first()
            
            if book and book.is_visible:
                filtered_books.append({
                    'book': book,
                    'is_visible': book.is_visible,
                    'added_at': cart_item.get('added_at')
                })
        
        # Sort books by added_at in descending order
        filtered_books.sort(key=lambda x: x['added_at'] or datetime.min, reverse=True)
        
        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_books = filtered_books[start:end]
        
        books_data = [{
            'ISBN10': book['book'].ISBN10,
            'ISBN13': book['book'].ISBN13,
            'Title': book['book'].Title,
            'Author': book['book'].Author,
            'Genres': [genre.name for genre in book['book'].genres],
            'Cover_Image': book['book'].Cover_Image,
            'Description': book['book'].Description,
            'Year_of_Publication': book['book'].Year_of_Publication,
            'Number_of_Pages': book['book'].Number_of_Pages,
            'Average_Rating': book['book'].Average_Rating,
            'Number_of_Ratings': book['book'].Number_of_Ratings,
            'Price': book['book'].Price,
            'is_visible': book['is_visible']
        } for book in paginated_books]
        
        return {
            'books': books_data,
            'total_books': len(filtered_books),
            'page': page,
            'per_page': per_page,
            'total_pages': (len(filtered_books) + per_page - 1) // per_page
        }
    except Exception as e:
        return {'error': f'Chyba při získávání knih v košíku: {str(e)}'}

def toggle_cart(isbn):
    """
    Toggles book state in the cart - adds or removes based on current state
    """
    try:
        # Get current cart from session, default to empty list
        cart = session.get('shopping_cart', [])
        
        # Find the book
        book = Book.query.filter(
            (Book.ISBN10 == isbn) | (Book.ISBN13 == isbn)
        ).first()
        
        if not book:
            return {'error': 'Kniha nenalezena'}
        
        if not book.is_visible:
            return {'error': 'Kniha není dostupná'}
        
        # Check if book is already in cart
        existing_book = next((item for item in cart if item['isbn'] == book.ISBN10 or item['isbn'] == book.ISBN13), None)
        
        if existing_book:
            # Remove book from cart
            cart = [item for item in cart if item['isbn'] != book.ISBN10 and item['isbn'] != book.ISBN13]
            action = 'odebrána z'
            is_in_cart = False
        else:
            # Add book to cart
            cart.append({
                'isbn': book.ISBN10,
                'added_at': datetime.utcnow()
            })
            action = 'přidána do'
            is_in_cart = True
        
        # Update session
        session['shopping_cart'] = cart
        session.modified = True
        
        return {
            'message': f'Kniha byla {action} košíku',
            'is_in_cart': is_in_cart,
            'book': {
                'ISBN10': book.ISBN10,
                'Title': book.Title,
                'Price': book.Price
            }
        }
    except Exception as e:
        return {'error': f'Chyba při změně stavu knihy v košíku: {str(e)}'}

def is_book_in_shopping_cart(isbn):
    """
    Checks if a book is in the shopping cart
    """
    try:
        # Get current cart from session, default to empty list
        cart = session.get('shopping_cart', [])
        
        # Find the book
        book = Book.query.filter(
            (Book.ISBN10 == isbn) | (Book.ISBN13 == isbn)
        ).first()
        
        if not book:
            return {'error': 'Kniha nenalezena'}
        
        if not book.is_visible:
            return {'error': 'Kniha není dostupná'}
        
        # Check if book is in cart
        is_in_cart = any(
            item['isbn'] == book.ISBN10 or item['isbn'] == book.ISBN13 
            for item in cart
        )
        
        return {
            'is_in_cart': is_in_cart,
            'book': {
                'ISBN10': book.ISBN10,
                'Title': book.Title,
                'Price': book.Price
            } if is_in_cart else None
        }
    except Exception as e:
        return {'error': f'Chyba při kontrole knihy v košíku: {str(e)}'}