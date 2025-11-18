import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Experiment endpoints
export const createParticipant = (participantId) =>
  api.post('/experiment/participant', { participant_id: participantId })

export const giveConsent = (participantId) =>
  api.post('/experiment/consent', { participant_id: participantId })

export const getExperimentPlan = (participantId) =>
  api.get('/experiment/plan', { params: { participant_id: participantId } })

export const getGenres = () =>
  api.get('/experiment/genres')

// Search endpoints
export const facetedSearch = (participantId, taskId, filters, sort) =>
  api.post('/search/faceted', {
    participant_id: participantId,
    task_id: taskId,
    filters,
    sort
  })

export const llmAssistParse = (participantId, taskId, nlQuery) =>
  api.post('/search/llm_assist/parse', {
    participant_id: participantId,
    task_id: taskId,
    nl_query: nlQuery
  })

export const llmAssistExecute = (participantId, taskId, parsedQuery) =>
  api.post('/search/llm_assist/execute', {
    participant_id: participantId,
    task_id: taskId,
    parsed_query: parsedQuery
  })

export const llmOnlySearch = (participantId, taskId, nlQuery) =>
  api.post('/search/llm_only', {
    participant_id: participantId,
    task_id: taskId,
    nl_query: nlQuery
  })

// Logging endpoints
export const logEvent = (participantId, interfaceType, taskId, eventType, payload) =>
  api.post('/log', {
    participant_id: participantId,
    interface_type: interfaceType,
    task_id: taskId,
    event_type: eventType,
    payload
  })

export const startTask = (participantId, interfaceType, taskId) =>
  api.post('/log/task/start', {
    participant_id: participantId,
    interface_type: interfaceType,
    task_id: taskId
  })

export const endTask = (participantId, interfaceType, taskId, submission) =>
  api.post('/log/task/end', {
    participant_id: participantId,
    interface_type: interfaceType,
    task_id: taskId,
    submission
  })

// Questionnaire endpoints
export const submitQuestionnaire = (participantId, interfaceType, questionnaireType, responses) =>
  api.post('/questionnaire', {
    participant_id: participantId,
    interface_type: interfaceType,
    questionnaire_type: questionnaireType,
    responses
  })

export default api

