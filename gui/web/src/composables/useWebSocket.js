import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { wsService } from '../services/websocket.js'
import configData from '../../../../config/gui_config.json'

export const API_HOST = configData.api.host
export const API_PORT = configData.api.port
export const WS_URL = `ws://${API_HOST}:${API_PORT}/ws`

/**
 * WebSocket Composable
 * 提供组件级别的 WebSocket 功能
 */
export function useWebSocket() {
  const isConnected = ref(false)
  const unsubscribers = []

  onMounted(() => {
    // 连接 WebSocket
    wsService.connect(WS_URL)
    
    // 订阅连接状态变化
    const unsubscribe = wsService.subscribe('connected', (data) => {
      isConnected.value = data.connected
      console.log('WebSocket connection status changed:', data)
      console.log(isConnected.value)
      
      if (data.connected) {
        console.log('✅ WebSocket connected in component')
      } else {
        console.log('❌ WebSocket disconnected in component')
      }
    })
    
    unsubscribers.push(unsubscribe)
    
    // 订阅重连失败
    const unsubscribeReconnectFailed = wsService.subscribe('reconnect_failed', (data) => {
      ElMessage({
        type: 'error',
        message: data.message || 'WebSocket connection failed. Please refresh the page.',
        duration: 0,
        showClose: true
      })
    })
    
    unsubscribers.push(unsubscribeReconnectFailed)
    
    // 初始化连接状态
    isConnected.value = wsService.getConnectionState()
  })

  onUnmounted(() => {
    // 清理所有订阅
    unsubscribers.forEach(unsub => unsub())
  })

  /**
   * 订阅消息
   * @param {string} eventType - 消息类型
   * @param {Function} callback - 回调函数
   * @returns {Function} 取消订阅函数
   */
  const subscribe = (eventType, callback) => {
    const unsubscribe = wsService.subscribe(eventType, callback)
    unsubscribers.push(unsubscribe)
    return unsubscribe
  }

  /**
   * 获取 WebSocket 统计信息
   */
  const getStats = () => {
    return wsService.getStats()
  }

  return {
    isConnected,
    subscribe,
    getStats
  }
}