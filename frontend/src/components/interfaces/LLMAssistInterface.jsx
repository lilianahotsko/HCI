import React, { useState } from 'react'
import { llmAssistParse, llmAssistExecute } from '../../api'
import ResultsTable from '../ResultsTable'

function LLMAssistInterface({ participantId, taskId, onSubmit }) {
  const [nlQuery, setNlQuery] = useState('')
  const [parsedQuery, setParsedQuery] = useState(null)
  const [preview, setPreview] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [parsing, setParsing] = useState(false)
  const [selectedMovies, setSelectedMovies] = useState([])
  const [reformulations, setReformulations] = useState(0)

  const handleParse = async () => {
    if (!nlQuery.trim()) {
      alert('Please enter a query')
      return
    }

    setParsing(true)
    try {
      const response = await llmAssistParse(participantId, taskId, nlQuery)
      setParsedQuery(response.data.parsed_query)
      setPreview(response.data.human_readable)
    } catch (err) {
      console.error('Parse failed:', err)
      alert('Failed to parse query. Please try again.')
    } finally {
      setParsing(false)
    }
  }

  const handleConfirmAndRun = async () => {
    if (!parsedQuery) {
      alert('Please parse a query first')
      return
    }

    setLoading(true)
    try {
      const response = await llmAssistExecute(participantId, taskId, parsedQuery)
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
    setParsedQuery(null)
    setPreview('')
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
      parsed_query: parsedQuery,
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
            placeholder="e.g., Find all dramas or thrillers with a female lead, budget under $10M, sorted by highest revenue"
            rows="3"
            disabled={parsing}
          />
        </div>
        <button onClick={handleParse} disabled={parsing || !nlQuery.trim()}>
          {parsing ? 'Interpreting...' : 'Interpret Query'}
        </button>
      </div>

      {preview && (
        <div className="card" style={{ marginBottom: '20px', backgroundColor: '#e3f2fd' }}>
          <h3>Interpreted Query Preview</h3>
          <p style={{ marginTop: '10px', fontSize: '16px' }}>{preview}</p>
          <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
            <button onClick={handleConfirmAndRun} disabled={loading}>
              {loading ? 'Running...' : 'Confirm & Run'}
            </button>
            <button onClick={handleReformulate} style={{ backgroundColor: '#6c757d' }}>
              Edit Query
            </button>
          </div>
        </div>
      )}

      {results.length > 0 && (
        <div className="card">
          <h3>Results ({results.length})</h3>
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

export default LLMAssistInterface

