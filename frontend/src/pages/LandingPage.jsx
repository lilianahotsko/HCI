import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createParticipant } from '../api'

function LandingPage() {
  const [participantId, setParticipantId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!participantId.trim()) {
      setError('Please enter a participant ID')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await createParticipant(participantId.trim())
      console.log('Participant created:', response.data)
      navigate(`/consent?participant_id=${encodeURIComponent(participantId.trim())}`)
    } catch (err) {
      console.error('Error creating participant:', err)
      const errorMessage = err.response?.data?.error || err.message || 'Failed to create participant. Please try again.'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container" style={{ maxWidth: '600px', marginTop: '100px' }}>
      <div className="card">
        <h1>HCI Research Experiment</h1>
        <p style={{ marginTop: '20px', marginBottom: '30px' }}>
          Welcome to the Movie Dataset Search Platform study. Please enter your participant ID to begin.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="participantId">Participant ID</label>
            <input
              type="text"
              id="participantId"
              value={participantId}
              onChange={(e) => setParticipantId(e.target.value)}
              placeholder="e.g., P01"
              disabled={loading}
            />
          </div>

          {error && (
            <div style={{ color: 'red', marginBottom: '15px' }}>
              {error}
            </div>
          )}

          <button type="submit" disabled={loading}>
            {loading ? 'Loading...' : 'Continue'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default LandingPage

