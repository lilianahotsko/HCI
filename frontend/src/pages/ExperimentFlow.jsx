import React, { useState, useEffect } from 'react'
import { useSearchParams, Routes, Route, Navigate } from 'react-router-dom'
import { getExperimentPlan } from '../api'
import InterfaceBlock from '../components/InterfaceBlock'
import QuestionnaireBlock from '../components/QuestionnaireBlock'
import CompletionPage from './CompletionPage'

function ExperimentFlow() {
  const [searchParams] = useSearchParams()
  const participantId = searchParams.get('participant_id')
  const datasetType = searchParams.get('dataset') || 'mixed'
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
  }, [participantId, datasetType])

  const loadPlan = async () => {
    try {
      setLoading(true)
      // Use 'mixed' mode to get tasks from both datasets
      const response = await getExperimentPlan(participantId, datasetType === 'mixed' ? 'mixed' : datasetType)
      console.log('Experiment plan loaded:', response.data)
      setPlan(response.data)
    } catch (err) {
      console.error('Failed to load experiment plan:', err)
      console.error('Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        url: err.config?.url
      })
      // Set plan to null to show error message
      setPlan(null)
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
          <h2>Error Loading Experiment Plan</h2>
          <p>Failed to load experiment plan. Please try again.</p>
          <p style={{ fontSize: '14px', color: '#666', marginTop: '10px' }}>
            Check browser console for details.
          </p>
          <button 
            onClick={() => {
              setLoading(true)
              loadPlan()
            }}
            style={{
              marginTop: '20px',
              padding: '10px 20px',
              backgroundColor: '#3498db',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Retry
          </button>
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
  const currentTask = currentTasks[currentTaskIndex]
  
  // Get dataset type from current task (for mixed mode, each task can have different dataset)
  const taskDatasetType = currentTask?.dataset_type || (plan.dataset_type === 'mixed' ? 'movies' : plan.dataset_type || datasetType)
  const isMixedMode = plan.dataset_type === 'mixed'
  
  // Create dataset label
  let datasetLabel = 'Mixed (Movies & Books)'
  if (!isMixedMode) {
    datasetLabel = taskDatasetType === 'books' ? 'Books dataset' : 'Movies dataset'
  } else if (currentTask) {
    datasetLabel = `Current task: ${taskDatasetType === 'books' ? 'Books' : 'Movies'} dataset`
  }

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
        <p style={{ marginBottom: '10px', color: '#444' }}>
          Dataset: <strong>{datasetLabel}</strong>
        </p>
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
        datasetType={taskDatasetType}
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

