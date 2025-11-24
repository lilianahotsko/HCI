import React, { useState } from 'react'
import { llmOnlySearch } from '../../api'
import ResultsTable from '../ResultsTable'

function LLMOnlyInterface({ participantId, taskId, datasetType = 'movies', onSubmit }) {
  const [nlQuery, setNlQuery] = useState('')
  const [answer, setAnswer] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedItems, setSelectedItems] = useState([])
  const [reformulations, setReformulations] = useState(0)

  const handleSearch = async () => {
    if (!nlQuery.trim()) {
      alert('Please enter a query')
      return
    }

    setLoading(true)
    try {
      const response = await llmOnlySearch(participantId, taskId, nlQuery, datasetType)
      setAnswer(response.data.answer || '')
      setResults(response.data.results || [])
      setSelectedItems([])
    } catch (err) {
      console.error('Search failed:', err)
      const errorMessage = err.response?.data?.error || err.message || 'Search failed. Please try again.'
      alert(`Search failed: ${errorMessage}`)
      // Clear previous results on error
      setAnswer('')
      setResults([])
      setSelectedItems([])
    } finally {
      setLoading(false)
    }
  }

  const handleReformulate = () => {
    setReformulations(prev => prev + 1)
    setAnswer('')
    setResults([])
    setSelectedItems([])
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
      // Deselect all
      setSelectedItems(prev => prev.filter(id => !allIds.includes(id)))
    } else {
      // Select all
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
      nl_query: nlQuery,
      answer: answer,
      selected_movie_ids: selectedItems,
      result_count: results.length,
      reformulations: reformulations,
      dataset_type: datasetType
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
            placeholder={
              datasetType === 'books'
                ? 'e.g., Recommend books over 300 pages published before 2000 with average rating above 4'
                : 'e.g., Give me all movies after 2015 under 100 minutes with a female lead and order them by revenue'
            }
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
          <h3>Retrieved {datasetType === 'books' ? 'Books' : 'Movies'} ({results.length})</h3>
          <ResultsTable
            results={results}
            datasetType={datasetType}
            selectedItems={selectedItems}
            onItemSelect={handleItemSelect}
            onSelectAll={handleSelectAll}
          />
          <div style={{ marginTop: '20px' }}>
            <button onClick={handleSubmit} style={{ width: '100%' }}>
              Submit Answer ({selectedItems.length} selected)
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default LLMOnlyInterface

