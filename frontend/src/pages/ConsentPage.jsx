import React, { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { giveConsent } from '../api'

function ConsentPage() {
  const [searchParams] = useSearchParams()
  const participantId = searchParams.get('participant_id')
  const [consentGiven, setConsentGiven] = useState(false)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleConsent = async () => {
    if (!consentGiven) return

    setLoading(true)
    try {
      await giveConsent(participantId)
      navigate(`/experiment?participant_id=${encodeURIComponent(participantId)}`)
    } catch (err) {
      console.error('Failed to record consent:', err)
      alert('Failed to record consent. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (!participantId) {
    return (
      <div className="container">
        <div className="card">
          <p>Invalid participant ID. Please start from the beginning.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container" style={{ maxWidth: '800px', marginTop: '50px' }}>
      <div className="card">
        <h1>Informed Consent</h1>
        <div style={{ marginTop: '30px', lineHeight: '1.8' }}>
          <h2>Study Overview</h2>
          <p>
            You are being invited to participate in a research study about search interfaces for datasets.
            This study will involve using different types of search interfaces to find movies in a database.
          </p>

          <h2 style={{ marginTop: '30px' }}>What You Will Do</h2>
          <ul style={{ marginLeft: '20px', marginTop: '10px' }}>
            <li>Use three different search interfaces to complete search tasks</li>
            <li>Complete questionnaires about your experience</li>
            <li>The session will take approximately 30-45 minutes</li>
          </ul>

          <h2 style={{ marginTop: '30px' }}>Risks and Benefits</h2>
          <p>
            There are no known risks associated with this study. Your participation will help advance
            research in human-computer interaction and search interface design.
          </p>

          <h2 style={{ marginTop: '30px' }}>Confidentiality</h2>
          <p>
            Your responses will be kept confidential. Your participant ID will be used to track your
            responses, but no personally identifiable information will be collected.
          </p>

          <h2 style={{ marginTop: '30px' }}>Voluntary Participation</h2>
          <p>
            Your participation is voluntary. You may withdraw from the study at any time without penalty.
          </p>

          <div style={{ marginTop: '40px', padding: '20px', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={consentGiven}
                onChange={(e) => setConsentGiven(e.target.checked)}
                style={{ width: '20px', height: '20px', marginRight: '10px' }}
              />
              <span>I have read and understood the information above, and I agree to participate in this study.</span>
            </label>
          </div>

          <button
            onClick={handleConsent}
            disabled={!consentGiven || loading}
            style={{ marginTop: '30px', width: '100%' }}
          >
            {loading ? 'Processing...' : 'I Agree - Begin Study'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ConsentPage

