from flask import Blueprint, jsonify, request, session
from database.comment_operations import (
    add_comment, 
    get_comments_for_book, 
    delete_comment,
    get_formatted_comments_for_book
)
import logging

bp = Blueprint('comments', __name__)
error_logger = logging.getLogger('error_logger')
info_logger = logging.getLogger('info_logger')

@bp.route('/api/comments/<isbn>', methods=['GET'])
def get_book_comments_endpoint(isbn):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    result = get_formatted_comments_for_book(isbn, page, per_page)
    
    if result.get('error'):
        info_logger.warning(result['error'])
        return jsonify({'error': result['error']}), 404
        
    info_logger.info('Úspěšně získány komentáře pro knihu %s', isbn)
    return jsonify(result)

@bp.route('/api/comments', methods=['POST'])
def add_book_comment_endpoint():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    data = request.json
    book_isbn = data.get('book_isbn')
    text = data.get('text')
    
    if not book_isbn or not text:
        return jsonify({'error': 'Chybí povinné údaje'}), 400
        
    success, message = add_comment(book_isbn, user_id, text)
    
    if success:
        info_logger.info('Uživatel %s přidal komentář ke knize %s', user_id, book_isbn)
        return jsonify({'message': message}), 201
    else:
        info_logger.warning(
            'Nepodařilo se přidat komentář ke knize %s: %s',
            book_isbn, message
        )
        return jsonify({'error': message}), 400

@bp.route('/api/comments/<int:comment_id>', methods=['DELETE'])
def delete_book_comment_endpoint(comment_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Uživatel není přihlášen'}), 401
        
    success, message = delete_comment(comment_id, user_id)
    
    if success:
        info_logger.info('Komentář %s byl smazán uživatelem %s', comment_id, user_id)
        return jsonify({'message': message}), 200
    else:
        info_logger.warning(
            'Nepodařilo se smazat komentář %s: %s',
            comment_id, message
        )
        return jsonify({'error': message}), 400
