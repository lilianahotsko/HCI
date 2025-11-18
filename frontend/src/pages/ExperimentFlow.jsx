import React, { useState, useEffect } from 'react'
import { useSearchParams, Routes, Route, Navigate } from 'react-router-dom'
import { getExperimentPlan } from '../api'
import InterfaceBlock from '../components/InterfaceBlock'
import QuestionnaireBlock from '../components/QuestionnaireBlock'
import CompletionPage from './CompletionPage'

function ExperimentFlow() {
  const [searchParams] = useSearchParams()
  const participantId = searchParams.get('participant_id')
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(true)
  const [currentInterfaceIndex, setCurrentInterfaceIndex] = useState(0)
  const [currentTaskIndex, setCurrentTaskIndex] = useState(0)
  const [showQuestionnaire, setShowQuestionnaire] = useState(false)
  const [completedInterfaces, setCompletedInterfaces] = useState([])

  useEffect(() => {
    if (participantId) {
      loadPlan()
    }
  }, [participantId])

  const loadPlan = async () => {
    try {
      const response = await getExperimentPlan(participantId)
      setPlan(response.data)
    } catch (err) {
      console.error('Failed to load experiment plan:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleInterfaceComplete = () => {
    const currentInterface = plan.interface_order[currentInterfaceIndex]
    setCompletedInterfaces([...completedInterfaces, currentInterface])
    setShowQuestionnaire(true)
  }

  const handleQuestionnaireComplete = () => {
    setShowQuestionnaire(false)
    if (currentInterfaceIndex < plan.interface_order.length - 1) {
      // Move to next interface
      setCurrentInterfaceIndex(currentInterfaceIndex + 1)
      setCurrentTaskIndex(0)
    } else {
      // All interfaces completed - this will trigger completion page via the check below
      setCurrentInterfaceIndex(plan.interface_order.length)
    }
  }

  if (loading) {
    return (
      <div className="container">
        <div className="card">
          <p>Loading experiment plan...</p>
        </div>
      </div>
    )
  }

  if (!plan) {
    return (
      <div className="container">
        <div className="card">
          <p>Failed to load experiment plan. Please try again.</p>
        </div>
      </div>
    )
  }

  if (!participantId) {
    return <Navigate to="/" />
  }

  // Check if all interfaces are completed first
  if (currentInterfaceIndex >= plan.interface_order.length) {
    return <CompletionPage participantId={participantId} />
  }

  const currentInterface = plan.interface_order[currentInterfaceIndex]
  const currentTasks = plan.tasks[currentInterface] || []

  if (showQuestionnaire) {
    return (
      <QuestionnaireBlock
        participantId={participantId}
        interfaceType={currentInterface}
        onComplete={handleQuestionnaireComplete}
      />
    )
  }

  return (
    <div className="container">
      <div className="card" style={{ marginBottom: '20px' }}>
        <h2>Experiment Progress</h2>
        <p>
          Interface {currentInterfaceIndex + 1} of {plan.interface_order.length}:{' '}
          <strong>{currentInterface.replace('_', ' ').toUpperCase()}</strong>
        </p>
        <p>
          Task {currentTaskIndex + 1} of {currentTasks.length}
        </p>
      </div>

      <InterfaceBlock
        participantId={participantId}
        interfaceType={currentInterface}
        tasks={currentTasks}
        currentTaskIndex={currentTaskIndex}
        onTaskComplete={() => {
          if (currentTaskIndex < currentTasks.length - 1) {
            setCurrentTaskIndex(currentTaskIndex + 1)
          } else {
            handleInterfaceComplete()
          }
        }}
      />
    </div>
  )
}

export default ExperimentFlow

