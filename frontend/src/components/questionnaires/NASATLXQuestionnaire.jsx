import React, { useState } from 'react'

const NASA_TLX_DIMENSIONS = [
  { id: 'mental_demand', label: 'Mental Demand', description: 'How mentally demanding was the task?' },
  { id: 'physical_demand', label: 'Physical Demand', description: 'How physically demanding was the task?' },
  { id: 'temporal_demand', label: 'Temporal Demand', description: 'How hurried or rushed was the pace of the task?' },
  { id: 'performance', label: 'Performance', description: 'How successful were you in accomplishing what you were asked to do?' },
  { id: 'effort', label: 'Effort', description: 'How hard did you have to work to accomplish your level of performance?' },
  { id: 'frustration', label: 'Frustration', description: 'How insecure, discouraged, irritated, stressed, and annoyed were you?' }
]

function NASATLXQuestionnaire({ onSubmit }) {
  const [responses, setResponses] = useState({})

  const handleChange = (dimensionId, value) => {
    setResponses(prev => ({ ...prev, [dimensionId]: parseInt(value) }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    const allAnswered = NASA_TLX_DIMENSIONS.every(dim => responses[dim.id] !== undefined)
    if (!allAnswered) {
      alert('Please rate all dimensions')
      return
    }

    onSubmit(responses)
  }

  return (
    <form onSubmit={handleSubmit}>
      <p style={{ marginBottom: '30px' }}>
        Please rate each dimension on a scale from 0 (Very Low) to 100 (Very High) using the slider.
      </p>
      
      {NASA_TLX_DIMENSIONS.map((dimension) => (
        <div key={dimension.id} className="form-group" style={{ marginBottom: '40px' }}>
          <label style={{ marginBottom: '10px', display: 'block', fontWeight: '500' }}>
            {dimension.label}
          </label>
          <p style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>
            {dimension.description}
          </p>
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
            <span style={{ fontSize: '12px', color: '#666' }}>0 (Very Low)</span>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={responses[dimension.id] || 0}
              onChange={(e) => handleChange(dimension.id, e.target.value)}
              style={{ flex: 1 }}
            />
            <span style={{ fontSize: '12px', color: '#666' }}>100 (Very High)</span>
            <span style={{ minWidth: '40px', textAlign: 'center', fontWeight: 'bold' }}>
              {responses[dimension.id] !== undefined ? responses[dimension.id] : 0}
            </span>
          </div>
        </div>
      ))}

      <button type="submit" style={{ marginTop: '30px', width: '100%' }}>
        Submit
      </button>
    </form>
  )
}

export default NASATLXQuestionnaire

