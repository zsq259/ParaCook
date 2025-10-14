import axios from 'axios'
import config from '../../../../config/gui_config.json'

const API_HOST = config.api.host
const API_PORT = config.api.port
const BASE_URL = `http://${API_HOST}:${API_PORT}/api`
const WS_URL = `ws://${API_HOST}:${API_PORT}/ws`

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// Actions
export const getActions = () => api.get('/actions')
export const saveActions = (actions) => api.post('/actions', { actions })
export const addAction = (agent, action) => api.post('/actions/add', action, { params: { agent } })
export const removeAction = (agent, index) => api.delete(`/actions/${agent}/${index}`)
export const clearActions = () => api.delete('/actions')
export const executeActions = () => api.post('/actions/execute')

// World State
export const getWorld = () => api.get('/world')
export const getAgents = () => api.get('/agents')
export const getRecipes = () => api.get('/recipes')
export const getOrders = () => api.get('/orders')

// Logs
export const getLogs = (limit = 100) => api.get('/logs', { params: { limit } })
export const clearLogs = () => api.delete('/logs')

// Task Status
export const getTaskStatus = () => api.get('/task/status')
export const markTaskComplete = () => api.post('/task/complete')
export const resetTask = () => api.post('/task/reset')

export const resetAll = () => api.post('/reset')

// WebSocket 连接
export const createWebSocket = (onMessage) => {
  const ws = new WebSocket(WS_URL)
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    onMessage(data)
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
  }
  
  return ws
}