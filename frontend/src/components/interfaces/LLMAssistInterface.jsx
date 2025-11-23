import React, { useState } from 'react'
import { llmAssistParse, llmAssistExecute } from '../../api'
import ResultsTable from '../ResultsTable'

function LLMAssistInterface({ participantId, taskId, datasetType = 'movies', onSubmit }) {
  const [nlQuery, setNlQuery] = useState('')
  const [parsedQuery, setParsedQuery] = useState(null)
  const [preview, setPreview] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [parsing, setParsing] = useState(false)
  const [selectedItems, setSelectedItems] = useState([])
  const [reformulations, setReformulations] = useState(0)

  const handleParse = async () => {
    if (!nlQuery.trim()) {
      alert('Please enter a query')
      return
    }

    setParsing(true)
    try {
      const response = await llmAssistParse(participantId, taskId, nlQuery, datasetType)
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
      const response = await llmAssistExecute(participantId, taskId, parsedQuery, datasetType)
      setResults(response.data.results || [])
      setSelectedItems([])
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
      parsed_query: parsedQuery,
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
                ? 'e.g., Find English books over 400 pages published after 2005 with average rating above 4.2'
                : 'e.g., Find all dramas or thrillers with a female lead, budget under $10M, sorted by highest revenue'
            }
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

export default LLMAssistInterface

