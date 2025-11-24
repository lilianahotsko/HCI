import axios from 'axios'

// Use environment variable for production, fallback to relative path for development
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

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

export const getExperimentPlan = (participantId, datasetType = 'mixed') =>
  api.get('/experiment/plan', { params: { participant_id: participantId, dataset_type: datasetType } })

export const getGenres = (datasetType = 'movies') =>
  api.get('/experiment/genres', { params: { dataset_type: datasetType } })

// Search endpoints
export const facetedSearch = (participantId, taskId, filters, sort, datasetType = 'movies') =>
  api.post('/search/faceted', {
    participant_id: participantId,
    task_id: taskId,
    filters,
    sort,
    dataset_type: datasetType
  })

export const llmAssistParse = (participantId, taskId, nlQuery, datasetType = 'movies') =>
  api.post('/search/llm_assist/parse', {
    participant_id: participantId,
    task_id: taskId,
    nl_query: nlQuery,
    dataset_type: datasetType
  })

export const llmAssistExecute = (participantId, taskId, parsedQuery, datasetType = 'movies') =>
  api.post('/search/llm_assist/execute', {
    participant_id: participantId,
    task_id: taskId,
    parsed_query: parsedQuery,
    dataset_type: datasetType
  })

export const llmOnlySearch = (participantId, taskId, nlQuery, datasetType = 'movies') =>
  api.post('/search/llm_only', {
    participant_id: participantId,
    task_id: taskId,
    nl_query: nlQuery,
    dataset_type: datasetType
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

export const startTask = (participantId, interfaceType, taskId, datasetType) =>
  api.post('/log/task/start', {
    participant_id: participantId,
    interface_type: interfaceType,
    task_id: taskId,
    dataset_type: datasetType
  })

export const endTask = (participantId, interfaceType, taskId, submission, datasetType) =>
  api.post('/log/task/end', {
    participant_id: participantId,
    interface_type: interfaceType,
    task_id: taskId,
    submission,
    dataset_type: datasetType
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

