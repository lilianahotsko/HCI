import React, { useState } from 'react'
import { llmOnlySearch } from '../../api'
import ResultsTable from '../ResultsTable'

function LLMOnlyInterface({ participantId, taskId, onSubmit }) {
  const [nlQuery, setNlQuery] = useState('')
  const [answer, setAnswer] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedMovies, setSelectedMovies] = useState([])
  const [reformulations, setReformulations] = useState(0)

  const handleSearch = async () => {
    if (!nlQuery.trim()) {
      alert('Please enter a query')
      return
    }

    setLoading(true)
    try {
      const response = await llmOnlySearch(participantId, taskId, nlQuery)
      setAnswer(response.data.answer || '')
      setResults(response.data.results || [])
    } catch (err) {
      console.error('Search failed:', err)
      alert('Search failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleReformulate = () => {
    setReformulations(prev => prev + 1)
    setAnswer('')
    setResults([])
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
      nl_query: nlQuery,
      answer: answer,
      selected_movie_ids: selectedMovies,
      result_count: results.length,
      reformulations: reformulations
    })
  }

  return (
    <div>
      <div className="card" style={{ marginBottom: '20px' }}>
        <h3>Natural Language Query</h3>
        <div className="form-group">
          <textarea
            value={nlQuery}
            onChange={(e) => setNlQuery(e.target.value)}
            placeholder="e.g., Give me all movies after 2015 under 100 minutes with a female lead and order them by revenue"
            rows="3"
            disabled={loading}
          />
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={handleSearch} disabled={loading || !nlQuery.trim()}>
            {loading ? 'Searching...' : 'Ask'}
          </button>
          {answer && (
            <button onClick={handleReformulate} style={{ backgroundColor: '#6c757d' }}>
              Ask Different Question
            </button>
          )}
        </div>
      </div>

      {answer && (
        <div className="card" style={{ marginBottom: '20px', backgroundColor: '#f0f0f0' }}>
          <h3>Answer</h3>
          <div style={{ marginTop: '10px', whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
            {answer}
          </div>
        </div>
      )}

      {results.length > 0 && (
        <div className="card">
          <h3>Retrieved Movies ({results.length})</h3>
          <ResultsTable
            results={results}
            selectedMovies={selectedMovies}
            onMovieSelect={handleMovieSelect}
            onSelectAll={handleSelectAll}
          />
          <div style={{ marginTop: '20px' }}>
            <button onClick={handleSubmit} style={{ width: '100%' }}>
              Submit Answer ({selectedMovies.length} selected)
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default LLMOnlyInterface

