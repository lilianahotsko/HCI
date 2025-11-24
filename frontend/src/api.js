import axios from 'axios'

// Use environment variable for production, fallback to relative path for development
// In production, VITE_API_BASE_URL should be set to your backend URL
// Example: https://your-backend.onrender.com (will auto-add /api)
// Or: https://your-backend.onrender.com/api (also works)
let API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '/api'

// Normalize the URL: remove trailing slashes, then ensure /api is included
API_BASE_URL = API_BASE_URL.replace(/\/+$/, '')  // Remove trailing slashes

if (API_BASE_URL.startsWith('http')) {
  // It's a full URL (production)
  if (!API_BASE_URL.endsWith('/api')) {
    API_BASE_URL = API_BASE_URL + '/api'
  }
} else {
  // It's a relative path (development)
  if (API_BASE_URL !== '/api') {
    API_BASE_URL = '/api'
  }
}

console.log('API Base URL:', API_BASE_URL)

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 120000  // 120 second timeout (LLM calls can take longer)
})

// Add response interceptor for better error handling
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: error.message,
      response: error.response?.data
    })
    return Promise.reject(error)
  }
)

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

