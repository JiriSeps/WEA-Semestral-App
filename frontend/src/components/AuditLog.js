import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';

const AuditLog = ({ user }) => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({ date: '', eventType: '', page: 1 });
  const [pagination, setPagination] = useState({ totalLogs: 0, totalPages: 1 });
  const [inputValue, setInputValue] = useState('');

  useEffect(() => {
    fetchAuditLogs();
  }, [filters]);

  const fetchAuditLogs = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/audit_logs?date=${filters.date}&event_type=${filters.eventType}&page=${filters.page}`,
        { credentials: 'include' }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch audit logs.');
      }

      const data = await response.json();
      setLogs(data.logs);
      setPagination({ totalLogs: data.total_logs, totalPages: data.total_pages });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setInputValue(e.target.value); // Update input value without applying filter yet
  };

  const handleFilterSubmit = (e) => {
    if (e.key === 'Enter') {
      setFilters((prev) => ({ ...prev, eventType: inputValue, page: 1 })); // Apply filter on Enter
      e.preventDefault();
    }
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    if (name !== 'eventType') {
      setFilters((prev) => ({ ...prev, [name]: value, page: 1 }));
    }
  };

  const handlePageChange = (newPage) => {
    setFilters((prev) => ({ ...prev, page: newPage }));
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  return (
    <div className="audit-log-container">
      <div className="filters">
        <input
          type="date"
          name="date"
          value={filters.date}
          onChange={handleFilterChange}
          placeholder="Filter by date"
        />
        <input
          type="text"
          name="eventType"
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleFilterSubmit}
          placeholder="Filter by event type"
        />
      </div>

      <table className="audit-log-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Event Type</th>
            <th>Timestamp</th>
            <th>Username</th>
            <th>Book ISBN</th>
            <th>Additional Data</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id}>
              <td>{log.id}</td>
              <td>{log.event_type}</td>
              <td>{new Date(log.timestamp).toLocaleString()}</td>
              <td>{log.username}</td>
              <td>{log.book_isbn || 'N/A'}</td>
              <td>{JSON.stringify(log.additional_data) || 'N/A'}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="pagination">
        <button
          disabled={filters.page === 1}
          onClick={() => handlePageChange(filters.page - 1)}
        >
          Previous
        </button>
        <span>
          Page {filters.page} of {pagination.totalPages}
        </span>
        <button
          disabled={filters.page === pagination.totalPages}
          onClick={() => handlePageChange(filters.page + 1)}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default AuditLog;
