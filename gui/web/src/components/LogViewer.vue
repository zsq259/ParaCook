<template>
  <el-card shadow="hover" class="log-viewer-card">
    <template #header>
      <div class="card-header-flex">
        <span class="card-header">
          <!-- 【修改】更新标题和添加条目统计 -->
          Execution Logs
          <el-tag size="small" style="margin-left: 10px">{{ logEntries.length }} entries</el-tag>
        </span>
        <el-space>
          <!-- 【修改】添加连接状态指示器 -->
          <el-tag 
            :type="isConnected ? 'success' : 'danger'" 
            size="small"
            effect="plain"
          >
            {{ isConnected ? '● Connected' : '● Disconnected' }}
          </el-tag>
          <el-button 
            size="small" 
            type="info" 
            text
            @click="copyLog"
            :disabled="logEntries.length === 0"
          >
            <el-icon style="margin-right: 5px"><CopyDocument /></el-icon>
            Copy
          </el-button>
          <!-- 【新增】清空按钮 -->
          <el-button 
            size="small" 
            type="danger" 
            text
            @click="clearLogs"
            :disabled="logEntries.length === 0"
          >
            Clear
          </el-button>
        </el-space>
      </div>
    </template>

    <!-- 【修改】完全重写日志容器 -->
    <div ref="logContainer" class="log-container">
      <div 
        v-for="(entry, index) in logEntries" 
        :key="index" 
        class="log-entry"
      >
        <span class="log-time">{{ entry.timestamp }}</span>
        <span :class="['log-level', `level-${entry.level.toLowerCase()}`]">
          [{{ entry.level }}]
        </span>
        <!-- 【新增】使用 v-html 渲染带颜色的 HTML -->
        <span class="log-message" v-html="entry.formattedMessage"></span>
      </div>
      
      <!-- 【修改】空状态显示 -->
      <div v-if="logEntries.length === 0" class="empty-log">
        <el-empty 
          description="No execution logs yet. Execute an action plan to see logs."
          :image-size="80"
        >
          <template #image>
            <el-icon :size="60" color="#909399">
              <Document />
            </el-icon>
          </template>
        </el-empty>
      </div>
    </div>
  </el-card>
</template>

<script setup>
// 【修改】完全重写 script 部分
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { CopyDocument, Document } from '@element-plus/icons-vue'
import config from '../../../../config/gui_config.json'

const API_HOST = config.api.host
const API_PORT = config.api.port
const WS_LOGS_URL = `ws://${API_HOST}:${API_PORT}/ws/logs`
const API_URL = `http://${API_HOST}:${API_PORT}/api`

// 【删除】移除 props 定义
// const props = defineProps({ log: { type: String, default: '' } })

// 【新增】状态管理
const logContainer = ref(null)
const logEntries = ref([])
const isConnected = ref(false)
let ws = null
let reconnectTimer = null

// 【新增】ANSI 颜色映射表
const ansiColorMap = {
  '30': '#2e3436', '31': '#cc0000', '32': '#4e9a06', '33': '#c4a000',
  '34': '#3465a4', '35': '#75507b', '36': '#06989a', '37': '#d3d7cf',
  '90': '#555753', '91': '#ef2929', '92': '#8ae234', '93': '#fce94f',
  '94': '#729fcf', '95': '#ad7fa8', '96': '#34e2e2', '97': '#eeeeec',
  '40': '#2e3436', '41': '#cc0000', '42': '#4e9a06', '43': '#c4a000',
  '44': '#3465a4', '45': '#75507b', '46': '#06989a', '47': '#d3d7cf',
}

// 【新增】转义 HTML
const escapeHtml = (text) => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// 【新增】ANSI 转 HTML
const ansiToHtml = (text) => {
  if (!text) return ''
  
  const ansiRegex = /\x1b\[([0-9;]+)m/g
  let html = ''
  let lastIndex = 0
  let styles = []
  
  let match
  while ((match = ansiRegex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      const textPart = text.slice(lastIndex, match.index)
      if (styles.length > 0) {
        html += `<span style="${styles.join(';')}">${escapeHtml(textPart)}</span>`
      } else {
        html += escapeHtml(textPart)
      }
    }
    
    const codes = match[1].split(';')
    const newStyles = []
    
    for (const code of codes) {
      if (code === '0') {
        styles = []
        break
      } else if (code === '1') {
        newStyles.push('font-weight:bold')
      } else if (code === '4') {
        newStyles.push('text-decoration:underline')
      } else if (code === '7') {
        newStyles.push('filter:invert(1)')
      } else if (ansiColorMap[code]) {
        newStyles.push(`color:${ansiColorMap[code]}`)
      } else if (code.startsWith('4') && code.length === 2 && ansiColorMap[code.slice(1)]) {
        newStyles.push(`background-color:${ansiColorMap[code.slice(1)]}`)
        newStyles.push('padding:0 2px')
      }
    }
    
    if (newStyles.length > 0 || codes.includes('0')) {
      styles = newStyles
    }
    
    lastIndex = match.index + match[0].length
  }
  
  if (lastIndex < text.length) {
    const textPart = text.slice(lastIndex)
    if (styles.length > 0) {
      html += `<span style="${styles.join(';')}">${escapeHtml(textPart)}</span>`
    } else {
      html += escapeHtml(textPart)
    }
  }
  
  return html || escapeHtml(text)
}

// 【新增】连接 WebSocket
const connectWebSocket = () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    return
  }
  
  try {
    ws = new WebSocket(WS_LOGS_URL)
    
    ws.onopen = () => {
      console.log('Log WebSocket connected')
      isConnected.value = true
      if (reconnectTimer) {
        clearTimeout(reconnectTimer)
        reconnectTimer = null
      }
      
      // 发送心跳
      const heartbeat = setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send('ping')
        } else {
          clearInterval(heartbeat)
        }
      }, 15000)
    }
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.type === 'clear') {
          logEntries.value = []
          return
        }
        
        if (data.type === 'ping') {
          return
        }
        
        // 转换 ANSI 颜色为 HTML
        data.formattedMessage = ansiToHtml(data.message)
        
        logEntries.value.push(data)
        
        // 限制日志条数
        if (logEntries.value.length > 2000) {
          logEntries.value.splice(0, 500)
        }
        
        // 自动滚动到底部
        nextTick(() => {
          if (logContainer.value) {
            const container = logContainer.value
            const shouldScroll = container.scrollHeight - container.scrollTop - container.clientHeight < 100
            if (shouldScroll) {
              container.scrollTop = container.scrollHeight
            }
          }
        })
      } catch (error) {
        console.error('Failed to parse log message:', error)
      }
    }
    
    ws.onerror = (error) => {
      console.error('Log WebSocket error:', error)
      isConnected.value = false
    }
    
    ws.onclose = () => {
      console.log('Log WebSocket disconnected, reconnecting...')
      isConnected.value = false
      ws = null
      reconnectTimer = setTimeout(connectWebSocket, 3000)
    }
  } catch (error) {
    console.error('Failed to connect WebSocket:', error)
    isConnected.value = false
    reconnectTimer = setTimeout(connectWebSocket, 3000)
  }
}

// 【新增】加载历史日志
const loadHistoryLogs = async () => {
  try {
    const response = await fetch(`${API_URL}/logs/history`)
    const result = await response.json()
    
    if (result.success && result.data) {
      logEntries.value = result.data.map(entry => ({
        ...entry,
        formattedMessage: ansiToHtml(entry.message)
      }))
      
      nextTick(() => {
        if (logContainer.value) {
          logContainer.value.scrollTop = logContainer.value.scrollHeight
        }
      })
    }
  } catch (error) {
    console.error('Failed to load history logs:', error)
  }
}

// 【新增】清空日志
const clearLogs = async () => {
  try {
    logEntries.value = []
    const response = await fetch(`${API_URL}/logs`, {
      method: 'DELETE' 
    })
    const result = await response.json()
    if (result.success) {
      ElMessage.success('Logs cleared')
    }
  } catch (error) {
    console.error('Failed to clear logs:', error)
  }
}

// 【修改】复制日志功能
const copyLog = async () => {
  try {
    // 提取纯文本
    const plainText = logEntries.value
      .map(entry => `[${entry.timestamp}] [${entry.level}] ${entry.message}`)
      .join('\n')
    
    await navigator.clipboard.writeText(plainText)
    ElMessage.success('Log copied to clipboard')
  } catch (error) {
    ElMessage.error('Failed to copy log')
  }
}

// 【新增】生命周期钩子
onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
  }
  if (ws) {
    ws.close()
  }
})
</script>

<style scoped>
.log-viewer-card {
  width: 100%;
  height: 24em;
}

.log-viewer-card :deep(.el-card__header) {
  padding: 12px 20px;
}

.log-viewer-card :deep(.el-card__body) {
  padding: 10px 20px;
  height: calc(22em - 60px);
}

.card-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
}

/* 【修改】日志容器样式 */
.log-container {
  height: 100%;
  overflow-y: auto;
  background-color: #1e1e1e;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #d4d4d4;
}

/* 【新增】日志条目样式 */
.log-entry {
  margin-bottom: 2px;
  display: flex;
  align-items: flex-start;
  word-break: break-word;
}

.log-time {
  color: #858585;
  margin-right: 8px;
  flex-shrink: 0;
  font-size: 12px;
}

.log-level {
  font-weight: bold;
  margin-right: 8px;
  flex-shrink: 0;
  min-width: 65px;
  font-size: 12px;
}

/* 【新增】日志级别颜色 */
.level-debug { color: #858585; }
.level-info { color: #4ec9b0; }
.level-warning { color: #dcdcaa; }
.level-error { color: #f48771; }
.level-success { color: #98c379; }

.log-message {
  flex: 1;
  white-space: pre-wrap;
  word-break: break-word;
  color: #d4d4d4;
}

/* 【新增】保持 v-html 中的样式 */
.log-message :deep(span) {
  font-family: inherit;
  line-height: inherit;
}

/* 【修改】空状态样式 */
.empty-log {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background-color: transparent;
}

.empty-log :deep(.el-empty__description) {
  color: #858585;
}

/* 【新增】滚动条样式 */
.log-container::-webkit-scrollbar {
  width: 10px;
}

.log-container::-webkit-scrollbar-track {
  background: #2d2d30;
  border-radius: 4px;
}

.log-container::-webkit-scrollbar-thumb {
  background: #3e3e42;
  border-radius: 4px;
}

.log-container::-webkit-scrollbar-thumb:hover {
  background: #4e4e52;
}
</style>