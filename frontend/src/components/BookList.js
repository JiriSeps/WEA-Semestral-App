import React from 'react';

export const BookList = ({ books, translations, language }) => (
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
          <th>{translations[language].numberOfPages}</th>
          <th>{translations[language].averageRating}</th>
          <th>{translations[language].numberOfRatings}</th>
        </tr>
      </thead>
      <tbody>
        {books.map(book => (
          <tr key={book.ISBN10 || book.ISBN13}>
            <td>
              {book.Cover_Image && (
                <img
                  src={book.Cover_Image}
                  alt={book.Title}
                  className="book-cover"
                  onError={(e) => {
                    e.target.src = '/placeholder-book.png';
                    e.target.onerror = null;
                  }}
                />
              )}
            </td>
            <td>{book.Title}</td>
            <td>{book.Author}</td>
            <td>{book.ISBN10}</td>
            <td>{book.ISBN13}</td>
            <td>{book.Genres}</td>
            <td>{book.Year_of_Publication}</td>
            <td>{book.Number_of_Pages}</td>
            <td>{book.Average_Customer_Rating?.toFixed(1)}</td>
            <td>{book.Number_of_Ratings}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);