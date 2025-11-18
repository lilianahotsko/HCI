import React from 'react'

function CompletionPage({ participantId }) {
  return (
    <div className="container" style={{ maxWidth: '600px', marginTop: '100px' }}>
      <div className="card">
        <h1>Thank You!</h1>
        <p style={{ marginTop: '20px', fontSize: '18px' }}>
          You have completed all parts of the experiment.
        </p>
        <p style={{ marginTop: '20px' }}>
          Your responses have been recorded. Thank you for your participation!
        </p>
        {participantId && (
          <p style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
            Participant ID: {participantId}
          </p>
        )}
      </div>
    </div>
  )
}

export default CompletionPage

