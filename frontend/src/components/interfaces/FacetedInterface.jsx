import React, { useState, useEffect } from 'react'
import { facetedSearch, getGenres } from '../../api'
import ResultsTable from '../ResultsTable'

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

const MOVIE_DEFAULT_FILTERS = {
  genres: [],
  lead_gender: '',
  release_year_min: '',
  release_year_max: '',
  runtime_min: '',
  runtime_max: '',
  budget_min: '',
  budget_max: ''
}

const BOOK_DEFAULT_FILTERS = {
  languages: [],
  author_keyword: '',
  publication_year_min: '',
  publication_year_max: '',
  num_pages_min: '',
  num_pages_max: '',
  average_rating_min: '',
  average_rating_max: '',
  ratings_count_min: '',
  ratings_count_max: ''
}

function FacetedInterface({ participantId, taskId, datasetType = 'movies', onSubmit }) {
  const [filters, setFilters] = useState(datasetType === 'books' ? { ...BOOK_DEFAULT_FILTERS } : { ...MOVIE_DEFAULT_FILTERS })
  const [sort, setSort] = useState({ field: '', direction: 'asc' })
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedItems, setSelectedItems] = useState([])
  const [facetOptions, setFacetOptions] = useState([])
  const [facetLabel, setFacetLabel] = useState(datasetType === 'books' ? 'Languages' : 'Genres')
  const [facetField, setFacetField] = useState(datasetType === 'books' ? 'languages' : 'genres')

  useEffect(() => {
    setFilters(datasetType === 'books' ? { ...BOOK_DEFAULT_FILTERS } : { ...MOVIE_DEFAULT_FILTERS })
    setSort({ field: '', direction: 'asc' })
    setResults([])
    setSelectedItems([])
  }, [datasetType])

  useEffect(() => {
    getGenres(datasetType)
      .then(response => {
        const { values = [], facet_label, facet_field } = response.data || {}
        setFacetOptions(values.length > 0 ? values : [])
        if (facet_label) setFacetLabel(facet_label)
        if (facet_field) setFacetField(facet_field)
      })
      .catch(() => {
        setFacetOptions(datasetType === 'books'
          ? ['eng', 'spa', 'fre', 'ger', 'ita']
          : ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 
             'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Mystery', 
             'Romance', 'Science Fiction', 'Thriller', 'War', 'Western'])
        setFacetLabel(datasetType === 'books' ? 'Languages' : 'Genres')
        setFacetField(datasetType === 'books' ? 'languages' : 'genres')
      })
  }, [datasetType])

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const handleFacetToggle = (value) => {
    setFilters(prev => {
      const currentValues = prev[facetField] || []
      return {
        ...prev,
        [facetField]: currentValues.includes(value)
          ? currentValues.filter(v => v !== value)
          : [...currentValues, value]
      }
    })
  }

  const handleSearch = async () => {
    setLoading(true)
    try {
      const cleanFilters = {}
      Object.keys(filters).forEach(key => {
        const value = filters[key]
        if (value === '' || value === null) return
        if (Array.isArray(value) && value.length === 0) return
        cleanFilters[key] = value
      })

      const response = await facetedSearch(
        participantId,
        taskId,
        cleanFilters,
        sort.field ? sort : null,
        datasetType
      )
      setResults(response.data.results || [])
      setSelectedItems([])
    } catch (err) {
      console.error('Search failed:', err)
      alert('Search failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleItemSelect = (itemId) => {
    setSelectedItems(prev => 
      prev.includes(itemId)
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    )
  }

  const handleSelectAll = () => {
    const allIds = results.map(item => item.id)
    const allSelected = allIds.every(id => selectedItems.includes(id))
    
    if (allSelected) {
      setSelectedItems(prev => prev.filter(id => !allIds.includes(id)))
    } else {
      setSelectedItems(prev => {
        const newSelection = [...prev]
        allIds.forEach(id => {
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
      selected_movie_ids: selectedItems,
      result_count: results.length,
      dataset_type: datasetType
    })
  }

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '20px' }}>
        {/* Filter Panel */}
        <div className="card">
          <h3>Filters</h3>
          
          <div className="form-group">
            <label>{facetLabel}</label>
            <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
              {facetOptions.map(option => (
                <label key={option} style={{ display: 'block', marginBottom: '8px' }}>
                  <input
                    type="checkbox"
                    checked={(filters[facetField] || []).includes(option)}
                    onChange={() => handleFacetToggle(option)}
                  />
                  <span style={{ marginLeft: '8px' }}>
                    {datasetType === 'books' ? (LANGUAGE_LABELS[option] || option) : option}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {datasetType === 'movies' && (
            <>
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
            </>
          )}

          {datasetType === 'books' && (
            <>
              <div className="form-group">
                <label>Author Contains</label>
                <input
                  type="text"
                  value={filters.author_keyword}
                  onChange={(e) => handleFilterChange('author_keyword', e.target.value)}
                  placeholder="e.g., Stephen King"
                />
              </div>

              <div className="form-group">
                <label>Publication Year (Min)</label>
                <input
                  type="number"
                  value={filters.publication_year_min}
                  onChange={(e) => handleFilterChange('publication_year_min', e.target.value ? parseInt(e.target.value) : '')}
                />
              </div>

              <div className="form-group">
                <label>Publication Year (Max)</label>
                <input
                  type="number"
                  value={filters.publication_year_max}
                  onChange={(e) => handleFilterChange('publication_year_max', e.target.value ? parseInt(e.target.value) : '')}
                />
              </div>

              <div className="form-group">
                <label>Pages (Min)</label>
                <input
                  type="number"
                  value={filters.num_pages_min}
                  onChange={(e) => handleFilterChange('num_pages_min', e.target.value ? parseInt(e.target.value) : '')}
                />
              </div>

              <div className="form-group">
                <label>Pages (Max)</label>
                <input
                  type="number"
                  value={filters.num_pages_max}
                  onChange={(e) => handleFilterChange('num_pages_max', e.target.value ? parseInt(e.target.value) : '')}
                />
              </div>

              <div className="form-group">
                <label>Average Rating (Min)</label>
                <input
                  type="number"
                  step="0.1"
                  value={filters.average_rating_min}
                  onChange={(e) => handleFilterChange('average_rating_min', e.target.value ? parseFloat(e.target.value) : '')}
                />
              </div>

              <div className="form-group">
                <label>Average Rating (Max)</label>
                <input
                  type="number"
                  step="0.1"
                  value={filters.average_rating_max}
                  onChange={(e) => handleFilterChange('average_rating_max', e.target.value ? parseFloat(e.target.value) : '')}
                />
              </div>

              <div className="form-group">
                <label>Ratings Count (Min)</label>
                <input
                  type="number"
                  value={filters.ratings_count_min}
                  onChange={(e) => handleFilterChange('ratings_count_min', e.target.value ? parseInt(e.target.value) : '')}
                />
              </div>

              <div className="form-group">
                <label>Ratings Count (Max)</label>
                <input
                  type="number"
                  value={filters.ratings_count_max}
                  onChange={(e) => handleFilterChange('ratings_count_max', e.target.value ? parseInt(e.target.value) : '')}
                />
              </div>
            </>
          )}

          <div className="form-group">
            <label>Sort By</label>
            <select
              value={sort.field}
              onChange={(e) => setSort(prev => ({ ...prev, field: e.target.value }))}
            >
              <option value="">None</option>
              {datasetType === 'books' ? (
                <>
                  <option value="publication_year">Publication Year</option>
                  <option value="num_pages">Pages</option>
                  <option value="average_rating">Average Rating</option>
                  <option value="ratings_count">Ratings Count</option>
                  <option value="title">Title</option>
                </>
              ) : (
                <>
                  <option value="release_year">Release Year</option>
                  <option value="runtime">Runtime</option>
                  <option value="budget">Budget</option>
                  <option value="revenue">Revenue</option>
                  <option value="title">Title</option>
                </>
              )}
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
                datasetType={datasetType}
                selectedItems={selectedItems}
                onItemSelect={handleItemSelect}
                onSelectAll={handleSelectAll}
              />
            )}
            {results.length === 0 && !loading && (
              <p style={{ marginTop: '20px', color: '#666' }}>
                Click "Apply Filters" to search for {datasetType === 'books' ? 'books' : 'movies'}.
              </p>
            )}
          </div>

          {results.length > 0 && (
            <div className="card" style={{ marginTop: '20px' }}>
              <button onClick={handleSubmit} style={{ width: '100%' }}>
                Submit Answer ({selectedItems.length} selected)
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default FacetedInterface