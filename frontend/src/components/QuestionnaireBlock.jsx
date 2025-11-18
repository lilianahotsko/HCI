import React, { useState } from 'react'
import { submitQuestionnaire } from '../api'
import SUSQuestionnaire from './questionnaires/SUSQuestionnaire'
import NASATLXQuestionnaire from './questionnaires/NASATLXQuestionnaire'
import TrustQuestionnaire from './questionnaires/TrustQuestionnaire'
import PreferenceQuestionnaire from './questionnaires/PreferenceQuestionnaire'

function QuestionnaireBlock({ participantId, interfaceType, onComplete }) {
  const [currentQuestionnaire, setCurrentQuestionnaire] = useState(0)
  const [responses, setResponses] = useState({})

  const questionnaires = [
    { type: 'SUS', component: SUSQuestionnaire },
    { type: 'NASA_TLX', component: NASATLXQuestionnaire },
    { type: 'trust', component: TrustQuestionnaire },
    { type: 'preference', component: PreferenceQuestionnaire }
  ]

  const handleQuestionnaireSubmit = async (questionnaireResponses) => {
    const questionnaireType = questionnaires[currentQuestionnaire].type
    
    try {
      await submitQuestionnaire(participantId, interfaceType, questionnaireType, questionnaireResponses)
      setResponses(prev => ({ ...prev, [questionnaireType]: questionnaireResponses }))
      
      if (currentQuestionnaire < questionnaires.length - 1) {
        setCurrentQuestionnaire(currentQuestionnaire + 1)
      } else {
        onComplete()
      }
    } catch (err) {
      console.error('Failed to submit questionnaire:', err)
      alert('Failed to submit questionnaire. Please try again.')
    }
  }

  const CurrentQuestionnaire = questionnaires[currentQuestionnaire].component

  return (
    <div className="container" style={{ maxWidth: '800px' }}>
      <div className="card">
        <h2>Questionnaire</h2>
        <p style={{ marginTop: '10px', marginBottom: '20px' }}>
          Please complete the following questionnaire about your experience with the{' '}
          <strong>{interfaceType.replace('_', ' ').toUpperCase()}</strong> interface.
        </p>
        <p style={{ marginBottom: '30px', fontSize: '14px', color: '#666' }}>
          Questionnaire {currentQuestionnaire + 1} of {questionnaires.length}
        </p>
        <CurrentQuestionnaire onSubmit={handleQuestionnaireSubmit} />
      </div>
    </div>
  )
}

export default QuestionnaireBlock

