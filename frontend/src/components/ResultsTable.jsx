import React from 'react'

const LANGUAGE_LABELS = {
  eng: 'English',
  spa: 'Spanish',
  fre: 'French',
  ger: 'German',
  ita: 'Italian',
  rus: 'Russian',
  por: 'Portuguese',
  ara: 'Arabic',
  chi: 'Chinese',
  jpn: 'Japanese',
  mul: 'Multiple',
  'en-US': 'English (US)'
}

const MOVIE_COLUMNS = [
  {
    key: 'release_year',
    label: 'Year',
    render: (item) => item.release_year || 'N/A'
  },
  {
    key: 'runtime',
    label: 'Runtime',
    render: (item) => (item.runtime ? `${item.runtime} min` : 'N/A')
  },
  {
    key: 'genres',
    label: 'Genres',
    render: (item) => (item.genres && item.genres.length > 0 ? item.genres.join(', ') : 'N/A')
  },
  {
    key: 'lead_gender',
    label: 'Lead Gender',
    render: (item) => item.lead_gender || 'N/A'
  },
  {
    key: 'budget',
    label: 'Budget',
    render: (item) => formatCurrency(item.budget)
  },
  {
    key: 'revenue',
    label: 'Revenue',
    render: (item) => formatCurrency(item.revenue)
  }
]

const BOOK_COLUMNS = [
  {
    key: 'authors',
    label: 'Authors',
    render: (item) => (item.authors && item.authors.length > 0 ? item.authors.join(', ') : 'N/A')
  },
  {
    key: 'publication_year',
    label: 'Year',
    render: (item) => item.publication_year || 'N/A'
  },
  {
    key: 'num_pages',
    label: 'Pages',
    render: (item) => item.num_pages || 'N/A'
  },
  {
    key: 'average_rating',
    label: 'Avg Rating',
    render: (item) => (item.average_rating ? item.average_rating.toFixed(2) : 'N/A')
  },
  {
    key: 'language',
    label: 'Language',
    render: (item) => formatLanguage(item.language)
  },
  {
    key: 'ratings_count',
    label: 'Ratings Count',
    render: (item) => (item.ratings_count ? item.ratings_count.toLocaleString() : 'N/A')
  }
]

const formatCurrency = (value) => {
  if (!value) return 'N/A'
  return `$${Number(value).toLocaleString('en-US', { maximumFractionDigits: 0 })}`
}

const formatLanguage = (code) => {
  if (!code) return 'N/A'
  return LANGUAGE_LABELS[code] || code
}

function ResultsTable({ results, datasetType = 'movies', selectedItems = [], onItemSelect, onSelectAll }) {
  const columnConfig = datasetType === 'books' ? BOOK_COLUMNS : MOVIE_COLUMNS
  const allSelected = results.length > 0 && results.every(item => selectedItems.includes(item.id))

  const handleSelectAll = () => {
    if (onSelectAll) {
      onSelectAll()
    } else {
      const allIds = results.map(item => item.id)
      if (allSelected) {
        allIds.forEach(id => {
          if (selectedItems.includes(id)) {
            onItemSelect(id)
          }
        })
      } else {
        allIds.forEach(id => {
          if (!selectedItems.includes(id)) {
            onItemSelect(id)
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
            {selectedItems.length} of {results.length} selected
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
              {columnConfig.map(column => (
                <th key={column.key} style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {results.map((item) => (
              <tr
                key={item.id}
                style={{
                  backgroundColor: selectedItems.includes(item.id) ? '#e3f2fd' : 'white',
                  cursor: 'pointer'
                }}
                onClick={() => onItemSelect(item.id)}
              >
                <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                  <input
                    type="checkbox"
                    checked={selectedItems.includes(item.id)}
                    onChange={() => onItemSelect(item.id)}
                    onClick={(e) => e.stopPropagation()}
                  />
                </td>
                <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                  {item.title}
                </td>
                {columnConfig.map(column => (
                  <td key={column.key} style={{ padding: '10px', border: '1px solid #ddd' }}>
                    {column.render(item)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default ResultsTable

