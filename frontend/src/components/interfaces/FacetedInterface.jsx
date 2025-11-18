import React, { useState, useEffect } from 'react'
import { facetedSearch, getGenres } from '../../api'
import ResultsTable from '../ResultsTable'

function FacetedInterface({ participantId, taskId, onSubmit }) {
  const [filters, setFilters] = useState({
    genres: [],
    lead_gender: '',
    release_year_min: '',
    release_year_max: '',
    runtime_min: '',
    runtime_max: '',
    budget_min: '',
    budget_max: ''
  })
  const [sort, setSort] = useState({ field: '', direction: 'asc' })
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedMovies, setSelectedMovies] = useState([])
  const [allGenres, setAllGenres] = useState([])

  useEffect(() => {
    // Fetch available genres from API
    getGenres()
      .then(response => {
        if (response.data.genres && response.data.genres.length > 0) {
          setAllGenres(response.data.genres)
        } else {
          // Fallback to common genres if API fails
          setAllGenres(['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 
                        'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Mystery', 
                        'Romance', 'Science Fiction', 'Thriller', 'War', 'Western'])
        }
      })
      .catch(() => {
        // Fallback to common genres if API fails
        setAllGenres(['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 
                      'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Mystery', 
                      'Romance', 'Science Fiction', 'Thriller', 'War', 'Western'])
      })
  }, [])

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const handleGenreToggle = (genre) => {
    setFilters(prev => ({
      ...prev,
      genres: prev.genres.includes(genre)
        ? prev.genres.filter(g => g !== genre)
        : [...prev.genres, genre]
    }))
  }

  const handleSearch = async () => {
    setLoading(true)
    try {
      // Clean filters: remove empty strings
      const cleanFilters = {}
      Object.keys(filters).forEach(key => {
        if (filters[key] !== '' && filters[key] !== null && 
            !(Array.isArray(filters[key]) && filters[key].length === 0)) {
          cleanFilters[key] = filters[key]
        }
      })

      const response = await facetedSearch(participantId, taskId, cleanFilters, 
        sort.field ? sort : null)
      setResults(response.data.results || [])
    } catch (err) {
      console.error('Search failed:', err)
      alert('Search failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleMovieSelect = (movieId) => {
    setSelectedMovies(prev => 
      prev.includes(movieId)
        ? prev.filter(id => id !== movieId)
        : [...prev, movieId]
    )
  }

  const handleSelectAll = () => {
    const allMovieIds = results.map(movie => movie.id)
    const allSelected = allMovieIds.every(id => selectedMovies.includes(id))
    
    if (allSelected) {
      // Deselect all
      setSelectedMovies(prev => prev.filter(id => !allMovieIds.includes(id)))
    } else {
      // Select all
      setSelectedMovies(prev => {
        const newSelection = [...prev]
        allMovieIds.forEach(id => {
          if (!newSelection.includes(id)) {
            newSelection.push(id)
          }
        })
        return newSelection
      })
    }
  }

  const handleSubmit = () => {
    onSubmit({
      selected_movie_ids: selectedMovies,
      result_count: results.length
    })
  }

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '20px' }}>
        {/* Filter Panel */}
        <div className="card">
          <h3>Filters</h3>
          
          <div className="form-group">
            <label>Genres</label>
            <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
              {allGenres.map(genre => (
                <label key={genre} style={{ display: 'block', marginBottom: '8px' }}>
                  <input
                    type="checkbox"
                    checked={filters.genres.includes(genre)}
                    onChange={() => handleGenreToggle(genre)}
                  />
                  <span style={{ marginLeft: '8px' }}>{genre}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>Lead Gender</label>
            <select
              value={filters.lead_gender}
              onChange={(e) => handleFilterChange('lead_gender', e.target.value)}
            >
              <option value="">Any</option>
              <option value="female">Female</option>
              <option value="male">Male</option>
              <option value="mixed">Mixed</option>
              <option value="unknown">Unknown</option>
            </select>
          </div>

          <div className="form-group">
            <label>Release Year (Min)</label>
            <input
              type="number"
              value={filters.release_year_min}
              onChange={(e) => handleFilterChange('release_year_min', e.target.value ? parseInt(e.target.value) : '')}
              placeholder="e.g., 2010"
            />
          </div>

          <div className="form-group">
            <label>Release Year (Max)</label>
            <input
              type="number"
              value={filters.release_year_max}
              onChange={(e) => handleFilterChange('release_year_max', e.target.value ? parseInt(e.target.value) : '')}
              placeholder="e.g., 2020"
            />
          </div>

          <div className="form-group">
            <label>Runtime (Min, minutes)</label>
            <input
              type="number"
              value={filters.runtime_min}
              onChange={(e) => handleFilterChange('runtime_min', e.target.value ? parseInt(e.target.value) : '')}
            />
          </div>

          <div className="form-group">
            <label>Runtime (Max, minutes)</label>
            <input
              type="number"
              value={filters.runtime_max}
              onChange={(e) => handleFilterChange('runtime_max', e.target.value ? parseInt(e.target.value) : '')}
            />
          </div>

          <div className="form-group">
            <label>Budget (Min, $)</label>
            <input
              type="number"
              value={filters.budget_min}
              onChange={(e) => handleFilterChange('budget_min', e.target.value ? parseFloat(e.target.value) : '')}
            />
          </div>

          <div className="form-group">
            <label>Budget (Max, $)</label>
            <input
              type="number"
              value={filters.budget_max}
              onChange={(e) => handleFilterChange('budget_max', e.target.value ? parseFloat(e.target.value) : '')}
            />
          </div>

          <div className="form-group">
            <label>Sort By</label>
            <select
              value={sort.field}
              onChange={(e) => setSort(prev => ({ ...prev, field: e.target.value }))}
            >
              <option value="">None</option>
              <option value="release_year">Release Year</option>
              <option value="runtime">Runtime</option>
              <option value="budget">Budget</option>
              <option value="revenue">Revenue</option>
              <option value="title">Title</option>
            </select>
          </div>

          {sort.field && (
            <div className="form-group">
              <label>Direction</label>
              <select
                value={sort.direction}
                onChange={(e) => setSort(prev => ({ ...prev, direction: e.target.value }))}
              >
                <option value="asc">Ascending</option>
                <option value="desc">Descending</option>
              </select>
            </div>
          )}

          <button onClick={handleSearch} disabled={loading} style={{ width: '100%', marginTop: '20px' }}>
            {loading ? 'Searching...' : 'Apply Filters'}
          </button>
        </div>

        {/* Results Panel */}
        <div>
          <div className="card">
            <h3>Results ({results.length})</h3>
            {results.length > 0 && (
            <ResultsTable
              results={results}
              selectedMovies={selectedMovies}
              onMovieSelect={handleMovieSelect}
              onSelectAll={handleSelectAll}
            />
            )}
            {results.length === 0 && !loading && (
              <p style={{ marginTop: '20px', color: '#666' }}>
                Click "Apply Filters" to search for movies.
              </p>
            )}
          </div>

          {results.length > 0 && (
            <div className="card" style={{ marginTop: '20px' }}>
              <button onClick={handleSubmit} style={{ width: '100%' }}>
                Submit Answer ({selectedMovies.length} selected)
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default FacetedInterface

