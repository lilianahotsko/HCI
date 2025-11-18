import React, { useState } from 'react'

function PreferenceQuestionnaire({ onSubmit }) {
  const [responses, setResponses] = useState({
    ease_of_use: '',
    efficiency: '',
    satisfaction: '',
    preference_ranking: ''
  })

  const handleChange = (field, value) => {
    setResponses(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (!responses.ease_of_use || !responses.efficiency || !responses.satisfaction) {
      alert('Please answer all questions')
      return
    }

    onSubmit(responses)
  }

  return (
    <form onSubmit={handleSubmit}>
      <p style={{ marginBottom: '30px' }}>
        Please provide your preferences and ratings for this interface.
      </p>

      <div className="form-group" style={{ marginBottom: '30px' }}>
        <label style={{ marginBottom: '10px', display: 'block', fontWeight: '500' }}>
          How easy was this interface to use? (1 = Very Difficult, 7 = Very Easy)
        </label>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
          {[1, 2, 3, 4, 5, 6, 7].map((value) => (
            <label key={value} style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                name="ease_of_use"
                value={value}
                checked={responses.ease_of_use === value.toString()}
                onChange={(e) => handleChange('ease_of_use', e.target.value)}
              />
              <span style={{ marginLeft: '5px' }}>{value}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="form-group" style={{ marginBottom: '30px' }}>
        <label style={{ marginBottom: '10px', display: 'block', fontWeight: '500' }}>
          How efficient was this interface for completing the tasks? (1 = Very Inefficient, 7 = Very Efficient)
        </label>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
          {[1, 2, 3, 4, 5, 6, 7].map((value) => (
            <label key={value} style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                name="efficiency"
                value={value}
                checked={responses.efficiency === value.toString()}
                onChange={(e) => handleChange('efficiency', e.target.value)}
              />
              <span style={{ marginLeft: '5px' }}>{value}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="form-group" style={{ marginBottom: '30px' }}>
        <label style={{ marginBottom: '10px', display: 'block', fontWeight: '500' }}>
          How satisfied were you with this interface? (1 = Very Dissatisfied, 7 = Very Satisfied)
        </label>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
          {[1, 2, 3, 4, 5, 6, 7].map((value) => (
            <label key={value} style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                name="satisfaction"
                value={value}
                checked={responses.satisfaction === value.toString()}
                onChange={(e) => handleChange('satisfaction', e.target.value)}
              />
              <span style={{ marginLeft: '5px' }}>{value}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="form-group" style={{ marginBottom: '30px' }}>
        <label style={{ marginBottom: '10px', display: 'block', fontWeight: '500' }}>
          Additional comments (optional):
        </label>
        <textarea
          value={responses.preference_ranking || ''}
          onChange={(e) => handleChange('preference_ranking', e.target.value)}
          rows="4"
          placeholder="Any additional thoughts about this interface..."
        />
      </div>

      <button type="submit" style={{ marginTop: '30px', width: '100%' }}>
        Submit
      </button>
    </form>
  )
}

export default PreferenceQuestionnaire

