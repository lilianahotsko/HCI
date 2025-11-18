import React from 'react'

function ResultsTable({ results, selectedMovies, onMovieSelect, onSelectAll }) {
  const formatCurrency = (value) => {
    if (!value) return 'N/A'
    return `$${value.toLocaleString('en-US', { maximumFractionDigits: 0 })}`
  }

  const allSelected = results.length > 0 && results.every(movie => selectedMovies.includes(movie.id))
  const someSelected = results.some(movie => selectedMovies.includes(movie.id))

  const handleSelectAll = () => {
    if (onSelectAll) {
      onSelectAll()
    } else {
      // Fallback: select/deselect all manually
      const allMovieIds = results.map(movie => movie.id)
      if (allSelected) {
        // Deselect all
        allMovieIds.forEach(id => {
          if (selectedMovies.includes(id)) {
            onMovieSelect(id)
          }
        })
      } else {
        // Select all
        allMovieIds.forEach(id => {
          if (!selectedMovies.includes(id)) {
            onMovieSelect(id)
          }
        })
      }
    }
  }

  return (
    <div style={{ marginTop: '20px' }}>
      {results.length > 0 && (
        <div style={{ marginBottom: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <button
            onClick={handleSelectAll}
            style={{
              padding: '6px 12px',
              fontSize: '14px',
              backgroundColor: allSelected ? '#6c757d' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            {allSelected ? 'Deselect All' : 'Select All'}
          </button>
          <span style={{ fontSize: '14px', color: '#666' }}>
            {selectedMovies.length} of {results.length} selected
          </span>
        </div>
      )}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ backgroundColor: '#f5f5f5' }}>
            <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>
              Select
            </th>
            <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>
              Title
            </th>
            <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>
              Year
            </th>
            <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>
              Runtime
            </th>
            <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>
              Genres
            </th>
            <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>
              Lead Gender
            </th>
            <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>
              Budget
            </th>
            <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>
              Revenue
            </th>
          </tr>
        </thead>
        <tbody>
          {results.map((movie) => (
            <tr
              key={movie.id}
              style={{
                backgroundColor: selectedMovies.includes(movie.id) ? '#e3f2fd' : 'white',
                cursor: 'pointer'
              }}
              onClick={() => onMovieSelect(movie.id)}
            >
              <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                <input
                  type="checkbox"
                  checked={selectedMovies.includes(movie.id)}
                  onChange={() => onMovieSelect(movie.id)}
                  onClick={(e) => e.stopPropagation()}
                />
              </td>
              <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                {movie.title}
              </td>
              <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                {movie.release_year || 'N/A'}
              </td>
              <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                {movie.runtime ? `${movie.runtime} min` : 'N/A'}
              </td>
              <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                {movie.genres ? movie.genres.join(', ') : 'N/A'}
              </td>
              <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                {movie.lead_gender || 'N/A'}
              </td>
              <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                {formatCurrency(movie.budget)}
              </td>
              <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                {formatCurrency(movie.revenue)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
    </div>
  )
}

export default ResultsTable

