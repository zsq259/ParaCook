/**
 * WebSocket 服务
 * 负责管理与后端的 WebSocket 连接，处理消息分发和自动重连
 */
class WebSocketService {
  constructor() {
    this.ws = null
    this.listeners = new Map()
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 3000
    this.isConnected = false
    this.heartbeatTimer = null
    this.url = ''
  }

  /**
   * 连接到 WebSocket 服务器
   * @param {string} url - WebSocket URL
   */
  connect(url) {
    console.log('WebSocketService connect called with url:', url)
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected')
      return
    }

    this.url = url
    console.log('Connecting to WebSocket:', url)
    
    try {
      this.ws = new WebSocket(url)
      this.setupEventHandlers()
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      this.scheduleReconnect()
    }
  }

  /**
   * 设置 WebSocket 事件处理器
   */
  setupEventHandlers() {
    this.ws.onopen = () => {
      console.log('✅ WebSocket connected')
      this.isConnected = true
      this.reconnectAttempts = 0
      this.startHeartbeat()
      this.notifyListeners('connected', { connected: true })
    }

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        console.log('📨 WebSocket message:', message.type)
        
        // 处理 pong 响应
        if (message.type === 'pong') {
          return
        }
        
        // 分发消息到监听器
        this.notifyListeners(message.type, message.data)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    this.ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error)
      this.notifyListeners('error', { error })
    }

    this.ws.onclose = (event) => {
      console.log('🔌 WebSocket disconnected', {
        code: event.code,
        reason: event.reason,
        clean: event.wasClean
      })
      
      this.isConnected = false
      this.stopHeartbeat()
      this.notifyListeners('connected', { connected: false })
      
      // 如果不是正常关闭，尝试重连
      if (!event.wasClean) {
        this.scheduleReconnect()
      }
    }
  }

  /**
   * 启动心跳
   */
  startHeartbeat() {
    this.stopHeartbeat() // 先清除旧的定时器
    
    this.heartbeatTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        console.log('💓 Sending heartbeat...')
        this.ws.send('ping')
      }
    }, 30000) // 30秒心跳
  }

  /**
   * 停止心跳
   */
  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  /**
   * 安排重连
   */
  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error(`❌ Max reconnect attempts (${this.maxReconnectAttempts}) reached`)
      this.notifyListeners('reconnect_failed', {
        message: 'Failed to reconnect to server. Please refresh the page.'
      })
      return
    }

    this.reconnectAttempts++
    console.log(`🔄 Reconnecting... (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
    
    setTimeout(() => {
      this.connect(this.url)
    }, this.reconnectDelay)
  }

  /**
   * 订阅消息类型
   * @param {string} eventType - 消息类型
   * @param {Function} callback - 回调函数
   * @returns {Function} 取消订阅函数
   */
  subscribe(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set())
    }
    
    this.listeners.get(eventType).add(callback)
    console.log(`📝 Subscribed to ${eventType}, total listeners: ${this.listeners.get(eventType).size}`)
    
    // 返回取消订阅函数
    return () => {
      this.unsubscribe(eventType, callback)
    }
  }

  /**
   * 取消订阅
   * @param {string} eventType - 消息类型
   * @param {Function} callback - 回调函数
   */
  unsubscribe(eventType, callback) {
    const callbacks = this.listeners.get(eventType)
    if (callbacks) {
      callbacks.delete(callback)
      console.log(`🗑️ Unsubscribed from ${eventType}, remaining listeners: ${callbacks.size}`)
      
      // 如果没有监听器了，删除该事件类型
      if (callbacks.size === 0) {
        this.listeners.delete(eventType)
      }
    }
  }

  /**
   * 通知所有监听器
   * @param {string} eventType - 事件类型
   * @param {any} data - 数据
   */
  notifyListeners(eventType, data) {
    const callbacks = this.listeners.get(eventType)
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error in listener for ${eventType}:`, error)
        }
      })
    }
  }

  /**
   * 断开连接
   */
  disconnect() {
    console.log('Disconnecting WebSocket...')
    this.stopHeartbeat()
    
    if (this.ws) {
      // 标记为正常关闭，避免自动重连
      this.ws.close(1000, 'Client closing connection')
      this.ws = null
    }
    
    this.isConnected = false
    this.reconnectAttempts = 0
  }

  /**
   * 获取连接状态
   * @returns {boolean}
   */
  getConnectionState() {
    return this.isConnected
  }

  /**
   * 获取所有监听器统计
   * @returns {Object}
   */
  getStats() {
    const stats = {}
    this.listeners.forEach((callbacks, eventType) => {
      stats[eventType] = callbacks.size
    })
    return {
      connected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      listeners: stats,
      totalListeners: Array.from(this.listeners.values()).reduce((sum, set) => sum + set.size, 0)
    }
  }
}

// 导出单例
export const wsService = new WebSocketService()