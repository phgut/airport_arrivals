import React, { useState } from 'react';
import { flightProcessor } from '../processor/flightProcessor';
import '../styles/FlightSearch.css';

const FlightSearch = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [flightData, setFlightData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = await flightProcessor.getFlightsByCountry(searchTerm);
      setFlightData(data);
    } catch (err) {
      setError('Failed to fetch flight data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flight-search-container">
      <h2>Flight Search</h2>
      <p className="timezone-info">All flight times are in UTC timezone</p>
      
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search by Airport Code (SGN, HAN, ...)"
          className="search-input"
        />
        <button type="submit" className="search-button" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      {flightData.length > 0 ? (
        <div className="results-container">
          <table className="flight-table">
            <thead>
              <tr>
                <th>Country</th>
                <th># Flights (UTC)</th>
              </tr>
            </thead>
            <tbody>
              {flightData.map((item, index) => (
                <tr key={index}>
                  <td>{item.country}</td>
                  <td>{item.flightCount}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        !loading && <p className="no-results">No results found</p>
      )}
    </div>
  );
};

export default FlightSearch;