import React from 'react';

export const Pagination = ({ currentPage, totalPages, handlePageChange, translations, language }) => (
  <div className="pagination">
    <button
      onClick={() => handlePageChange(currentPage - 1)}
      disabled={currentPage === 1}
      className="pagination-button"
    >
      {translations[language].previous}
    </button>
    <span className="page-info">
      {translations[language].page} {currentPage} {translations[language].of} {totalPages}
    </span>
    <button
      onClick={() => handlePageChange(currentPage + 1)}
      disabled={currentPage === totalPages}
      className="pagination-button"
    >
      {translations[language].next}
    </button>
  </div>
);