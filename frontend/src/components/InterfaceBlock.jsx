import React, { useState, useEffect } from 'react'
import FacetedInterface from './interfaces/FacetedInterface'
import LLMAssistInterface from './interfaces/LLMAssistInterface'
import LLMOnlyInterface from './interfaces/LLMOnlyInterface'
import { startTask, endTask } from '../api'

function InterfaceBlock({ participantId, interfaceType, tasks, currentTaskIndex, onTaskComplete }) {
  const [taskStarted, setTaskStarted] = useState(false)
  const [taskStartTime, setTaskStartTime] = useState(null)
  const currentTask = tasks[currentTaskIndex]

  useEffect(() => {
    // Reset task state when task changes
    setTaskStarted(false)
    setTaskStartTime(null)
  }, [currentTaskIndex])

  const handleStartTask = async () => {
    if (!currentTask) return

    try {
      await startTask(participantId, interfaceType, currentTask.task_id)
      setTaskStarted(true)
      setTaskStartTime(Date.now())
    } catch (err) {
      console.error('Failed to start task:', err)
      alert('Failed to start task. Please try again.')
    }
  }

  const handleSubmitAnswer = async (submission) => {
    if (!currentTask) return

    try {
      const taskDuration = taskStartTime ? Date.now() - taskStartTime : null
      await endTask(participantId, interfaceType, currentTask.task_id, {
        ...submission,
        task_duration_ms: taskDuration
      })
      onTaskComplete()
    } catch (err) {
      console.error('Failed to submit answer:', err)
      alert('Failed to submit answer. Please try again.')
    }
  }

  if (!currentTask) {
    return (
      <div className="card">
        <p>No tasks available for this interface.</p>
      </div>
    )
  }

  const interfaceNames = {
    faceted: 'Faceted Search',
    llm_assist: 'LLM-Assisted Search with Preview',
    llm_only: 'LLM-Only Search'
  }

  const interfaceDescriptions = {
    faceted: 'Use the filters on the left to search for movies. Select movies from the results and submit your answer.',
    llm_assist: 'Enter your query in natural language. Review the interpreted query preview, then confirm to see results.',
    llm_only: 'Enter your query in natural language. The system will provide a direct answer based on the movie database.'
  }

  return (
    <div>
      <div className="card" style={{ marginBottom: '20px' }}>
        <h2>{interfaceNames[interfaceType]}</h2>
        <p style={{ marginTop: '10px', color: '#666' }}>
          {interfaceDescriptions[interfaceType]}
        </p>
      </div>

      <div className="card" style={{ marginBottom: '20px' }}>
        <div style={{ padding: '15px', backgroundColor: '#e3f2fd', borderRadius: '4px' }}>
          <h3 style={{ marginBottom: '10px' }}>Task:</h3>
          <p style={{ fontSize: '16px', marginTop: '10px', lineHeight: '1.6' }}>
            {currentTask.description}
          </p>
          <div style={{ marginTop: '15px', display: 'flex', gap: '20px', fontSize: '14px' }}>
            <span>
              <strong>Complexity:</strong> {currentTask.complexity}
            </span>
            <span>
              <strong>Task:</strong> {currentTaskIndex + 1} of {tasks.length}
            </span>
          </div>
        </div>

        {!taskStarted ? (
          <div style={{ marginTop: '20px' }}>
            <button onClick={handleStartTask} style={{ width: '100%', padding: '12px', fontSize: '16px' }}>
              Start Task
            </button>
          </div>
        ) : (
          <div style={{ marginTop: '20px' }}>
            {taskStartTime && (
              <div style={{ marginBottom: '15px', padding: '10px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
                <strong>Task started.</strong> Complete the task and submit your answer when finished.
              </div>
            )}
            
            {interfaceType === 'faceted' && (
              <FacetedInterface
                participantId={participantId}
                taskId={currentTask.task_id}
                onSubmit={handleSubmitAnswer}
              />
            )}
            
            {interfaceType === 'llm_assist' && (
              <LLMAssistInterface
                participantId={participantId}
                taskId={currentTask.task_id}
                onSubmit={handleSubmitAnswer}
              />
            )}
            
            {interfaceType === 'llm_only' && (
              <LLMOnlyInterface
                participantId={participantId}
                taskId={currentTask.task_id}
                onSubmit={handleSubmitAnswer}
              />
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default InterfaceBlock

