import React from 'react';
import Book from './Book';

export const BookList = ({ 
  books, 
  translations, 
  language, 
  onBookSelect,
  showFavorites  // Nový prop
}) => (
  <div className="table-container">
    <table>
      <thead>
        <tr>
          <th>{translations[language].cover}</th>
          <th>{translations[language].searchBook}</th>
          <th>{translations[language].searchAuthor}</th>
          <th>ISBN10</th>
          <th>ISBN13</th>
          <th>{translations[language].genres}</th>
          <th>{translations[language].yearOfPublication}</th>
        </tr>
      </thead>
      <tbody>
        {books.map((book) => (
          <Book
            key={book.ISBN10 || book.ISBN13}
            coverImage={book.Cover_Image}
            title={book.Title}
            author={book.Author}
            isbn10={book.ISBN10}
            isbn13={book.ISBN13}
            genres={book.Genres}
            yearOfPublication={book.Year_of_Publication}
            onBookSelect={onBookSelect}
            isVisible={book.is_visible}  // Nový prop
            showFavorites={showFavorites}  // Předáváme dál do Book komponenty
          />
        ))}
      </tbody>
    </table>
  </div>
);