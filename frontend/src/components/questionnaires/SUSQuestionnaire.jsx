import React, { useState } from 'react'

const SUS_QUESTIONS = [
  'I think that I would like to use this system frequently.',
  'I found the system unnecessarily complex.',
  'I thought the system was easy to use.',
  'I think that I would need the support of a technical person to be able to use this system.',
  'I found the various functions in this system were well integrated.',
  'I thought there was too much inconsistency in this system.',
  'I would imagine that most people would learn to use this system very quickly.',
  'I found the system very cumbersome to use.',
  'I felt very confident using the system.',
  'I needed to learn a lot of things before I could get going with this system.'
]

function SUSQuestionnaire({ onSubmit }) {
  const [responses, setResponses] = useState({})

  const handleChange = (questionIndex, value) => {
    setResponses(prev => ({ ...prev, [questionIndex]: parseInt(value) }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    // Check if all questions answered
    const allAnswered = SUS_QUESTIONS.every((_, index) => responses[index] !== undefined)
    if (!allAnswered) {
      alert('Please answer all questions')
      return
    }

    onSubmit(responses)
  }

  return (
    <form onSubmit={handleSubmit}>
      <p style={{ marginBottom: '30px' }}>
        Please rate your agreement with each statement on a scale from 1 (Strongly Disagree) to 5 (Strongly Agree).
      </p>
      
      {SUS_QUESTIONS.map((question, index) => (
        <div key={index} className="form-group" style={{ marginBottom: '30px' }}>
          <label style={{ marginBottom: '10px', display: 'block', fontWeight: '500' }}>
            {index + 1}. {question}
          </label>
          <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                name={`sus_${index}`}
                value="1"
                checked={responses[index] === 1}
                onChange={(e) => handleChange(index, e.target.value)}
              />
              <span style={{ marginLeft: '5px' }}>1 (Strongly Disagree)</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                name={`sus_${index}`}
                value="2"
                checked={responses[index] === 2}
                onChange={(e) => handleChange(index, e.target.value)}
              />
              <span style={{ marginLeft: '5px' }}>2</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                name={`sus_${index}`}
                value="3"
                checked={responses[index] === 3}
                onChange={(e) => handleChange(index, e.target.value)}
              />
              <span style={{ marginLeft: '5px' }}>3 (Neutral)</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                name={`sus_${index}`}
                value="4"
                checked={responses[index] === 4}
                onChange={(e) => handleChange(index, e.target.value)}
              />
              <span style={{ marginLeft: '5px' }}>4</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                name={`sus_${index}`}
                value="5"
                checked={responses[index] === 5}
                onChange={(e) => handleChange(index, e.target.value)}
              />
              <span style={{ marginLeft: '5px' }}>5 (Strongly Agree)</span>
            </label>
          </div>
        </div>
      ))}

      <button type="submit" style={{ marginTop: '30px', width: '100%' }}>
        Submit
      </button>
    </form>
  )
}

export default SUSQuestionnaire

