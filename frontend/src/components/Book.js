import React from 'react';
import { useNavigate } from 'react-router-dom';

const Book = ({ 
  coverImage, 
  title, 
  author, 
  isbn10, 
  isbn13, 
  genres, 
  yearOfPublication, 
  numberOfPages, 
  averageRating, 
  numberOfRatings 
}) => {
  const navigate = useNavigate();
  
  const handleClick = () => {
    navigate(`/book/${isbn10 || isbn13}`);
  };

  return (
    <tr 
      onClick={handleClick} 
      className="cursor-pointer hover:bg-gray-50 transition-colors"
    >
      <td>
        {coverImage && (
          <img
            src={coverImage}
            alt={title}
            className="book-cover"
            onError={(e) => {
              e.target.src = '/placeholder-book.png';
              e.target.onerror = null;
            }}
          />
        )}
      </td>
      <td>{title}</td>
      <td>{author}</td>
      <td>{isbn10}</td>
      <td>{isbn13}</td>
      <td>{genres}</td>
      <td>{yearOfPublication}</td>
      <td>{numberOfPages}</td>
      <td>{averageRating?.toFixed(1)}</td>
      <td>{numberOfRatings}</td>
    </tr>
  );
};

export default Book;