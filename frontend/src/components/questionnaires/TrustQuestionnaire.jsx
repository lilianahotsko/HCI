import React, { useState } from 'react'

const TRUST_QUESTIONS = [
  { id: 'trust_accuracy', label: 'I trust the accuracy of the search results.' },
  { id: 'trust_transparency', label: 'I understand how the system processes my queries.' },
  { id: 'trust_control', label: 'I feel in control when using this system.' },
  { id: 'trust_reliability', label: 'I trust this system to provide reliable information.' },
  { id: 'trust_predictability', label: 'I can predict how the system will respond to my actions.' }
]

function TrustQuestionnaire({ onSubmit }) {
  const [responses, setResponses] = useState({})

  const handleChange = (questionId, value) => {
    setResponses(prev => ({ ...prev, [questionId]: parseInt(value) }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    const allAnswered = TRUST_QUESTIONS.every(q => responses[q.id] !== undefined)
    if (!allAnswered) {
      alert('Please answer all questions')
      return
    }

    onSubmit(responses)
  }

  return (
    <form onSubmit={handleSubmit}>
      <p style={{ marginBottom: '30px' }}>
        Please rate your agreement with each statement on a scale from 1 (Strongly Disagree) to 7 (Strongly Agree).
      </p>
      
      {TRUST_QUESTIONS.map((question) => (
        <div key={question.id} className="form-group" style={{ marginBottom: '30px' }}>
          <label style={{ marginBottom: '10px', display: 'block', fontWeight: '500' }}>
            {question.label}
          </label>
          <div style={{ display: 'flex', gap: '15px', alignItems: 'center', flexWrap: 'wrap' }}>
            {[1, 2, 3, 4, 5, 6, 7].map((value) => (
              <label key={value} style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name={question.id}
                  value={value}
                  checked={responses[question.id] === value}
                  onChange={(e) => handleChange(question.id, e.target.value)}
                />
                <span style={{ marginLeft: '5px' }}>{value}</span>
              </label>
            ))}
            <div style={{ marginLeft: '10px', fontSize: '12px', color: '#666' }}>
              (1 = Strongly Disagree, 7 = Strongly Agree)
            </div>
          </div>
        </div>
      ))}

      <button type="submit" style={{ marginTop: '30px', width: '100%' }}>
        Submit
      </button>
    </form>
  )
}

export default TrustQuestionnaire

