import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const BookComments = ({ isbn, translations, language, user }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchComments();
  }, [isbn]);

  const fetchComments = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/comments/${isbn}`);
      setComments(response.data.comments);
      setLoading(false);
    } catch (err) {
      setError(translations[language].errorLoadingComments);
      setLoading(false);
    }
  };

  const handleSubmitComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      await axios.post(`${API_BASE_URL}/api/comments`, {
        book_isbn: isbn,
        text: newComment
      });
      setNewComment('');
      fetchComments(); // Refresh comments after posting
    } catch (err) {
      setError(translations[language].errorAddingComment);
    }
  };

  if (loading) return <div>{translations[language].loading}</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="comments-section">
      <h3 className="comments-title">{translations[language].comments}</h3>
      
      {user ? (
        <form onSubmit={handleSubmitComment} className="comment-form">
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            className="comment-textarea"
            placeholder={translations[language].addCommentPlaceholder}
            rows="3"
          />
          <button
            type="submit"
            className="submit-comment"
          >
            {translations[language].addComment}
          </button>
        </form>
      ) : (
        <p className="login-message">
          {translations[language].loginToComment}
        </p>
      )}
  
      <div className="comments-list">
        {comments.length > 0 ? (
          comments.map((comment) => (
            <div key={comment.id} className="comment-item">
              <div className="comment-timestamp">
                {new Date(comment.created_at).toLocaleString(language === 'cs' ? 'cs-CZ' : 'en-US')}
              </div>
              <div className="comment-text">{comment.text}</div>
            </div>
          ))
        ) : (
          <p className="no-comments">{translations[language].noComments}</p>
        )}
      </div>
    </div>
  );
};

export default BookComments;