<template>
  <el-container class="app-container">
    <el-header height="60px">
      <div class="header-content">
        <h1>ParaCook Testing GUI</h1>
        <el-space>
          <!-- WebSocket 连接状态指示器 -->
          <el-tag :type="isConnected ? 'success' : 'danger'" size="small">
            {{ isConnected ? '🟢 Connected' : '🔴 Disconnected' }}
          </el-tag>
          
          <el-tag v-if="taskCompleted" type="success" size="large" effect="dark">
            ✅ All Orders Completed!
          </el-tag>
          <el-button type="danger" @click="handleClearAll">
            Clear All States and Refresh
          </el-button>
        </el-space>
      </div>
    </el-header>

    <el-main style="padding: 10px 20px">
      <el-row :gutter="20">
        <!-- 左侧：地图区域 -->
        <el-col :span="9">
          <div class="left-panel">
            <MapViewer ref="mapViewerRef" />
            <!-- 日志查看器 -->
            <LogViewer />
          </div>
        </el-col>

        <!-- 右侧：动作编辑区域 -->
        <el-col :span="15">
          <div class="right-panel">
            <!-- 配置信息 -->
            <ConfigInfo ref="configInfoRef" />

            <!-- 动作编辑和表单区域 -->
            <el-row :gutter="20">
              <!-- 左侧：动作编辑器 -->
              <el-col :span="14">
                <ActionEditor 
                  v-model:actions="actions"
                  :agent-names="agentNames"
                />
              </el-col>

              <!-- 右侧：动作表单和执行按钮 -->
              <el-col :span="10">
                <div style="display: flex; flex-direction: column; gap: 20px;">
                  <!-- 添加动作表单 -->
                  <ActionForm 
                    :agent-names="agentNames"
                    @add-action="handleAddAction"
                    :disabled="taskCompleted"
                  />

                  <!-- 执行按钮 -->
                  <el-button 
                    type="success" 
                    size="large" 
                    style="width: 100%"
                    @click="handleExecute"
                    :loading="executing"
                    :disabled="taskCompleted || Object.keys(actions).length === 0"
                  >
                    <template v-if="!executing">
                      <el-icon style="margin-right: 8px"><VideoPlay /></el-icon>
                      {{ taskCompleted ? 'Task Completed' : 'Execute Action Plan' }}
                    </template>
                    <template v-else>
                      Executing...
                    </template>
                  </el-button>

                  <HistoryPlayer 
                    :history="executionHistory"
                    @step-change="handleHistoryStepChange"
                  />
                </div>
              </el-col>
            </el-row>
          </div>
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoPlay } from '@element-plus/icons-vue'
import MapViewer from './components/MapViewer.vue'
import ConfigInfo from './components/ConfigInfo.vue'
import ActionEditor from './components/ActionEditor.vue'
import ActionForm from './components/ActionForm.vue'
import LogViewer from './components/LogViewer.vue'
import HistoryPlayer from './components/HistoryPlayer.vue'
import { useWebSocket } from './composables/useWebSocket'
import { 
  executeActions, 
  clearActions, 
  saveActions,
  resetAll
} from './api/actions'

// ========== 开发环境日志开关 ==========
const DEBUG = import.meta.env.DEV
const log = (...args) => DEBUG && console.log(...args)

// WebSocket 连接
const { isConnected, subscribe, getStats } = useWebSocket()

// 状态管理
const mapViewerRef = ref(null)
const configInfoRef = ref(null)
const agentNames = ref([])
const actions = ref({})
const executing = ref(false)
const taskCompleted = ref(false)
const subscriptionsSetup = ref(false)
const executionHistory = ref([])

// ========== 通用错误处理 ==========
const handleApiError = (error, defaultMessage) => {
  console.error(defaultMessage, error)
  ElMessage.error(error.message || defaultMessage)
}

// ========== WebSocket 事件订阅（优化版）==========
const setupSubscriptions = () => {
  if (subscriptionsSetup.value) {
    log('⚠️ Subscriptions already set up, skipping...')
    return
  }
  
  log('✅ Setting up WebSocket subscriptions...')
  log('📊 WebSocket stats:', getStats())
  
  // 集中管理所有订阅
  const subscriptions = {
    task_status: (data) => {
      log('📊 Task status update:', data)
      
      if (data.completed && !taskCompleted.value) {
        taskCompleted.value = true
        ElMessage({
          message: '🎉 All orders completed successfully!',
          type: 'success',
          duration: 0,
          showClose: true
        })
      }
      
      if (data.reset) {
        taskCompleted.value = false
      }
    },
    
    map_update: (data) => {
      log('🗺️ Map update received:', data)
      mapViewerRef.value?.updateMap(data)
    },
    
    config_update: (data) => {
      log('⚙️ Config update received:', data)
      configInfoRef.value?.updateConfig(data)
    },
    
    agents_update: (data) => {
      log('👥 Agents update received:', data)
      agentNames.value = data
    },
    
    actions_update: (data) => {
      log('🎬 Actions update received:', data)
      actions.value = data.actions
    },
    
    system_reset: (data) => {
      log('🔄 System reset received:', data)
      taskCompleted.value = false
      actions.value = {}
      ElMessage.success('System has been reset to initial state')
    },

    execution_history: (data) => {
      log('📊 Execution history received:', data.history?.length, 'steps')
      executionHistory.value = data.history || []
      
      if (executionHistory.value.length > 0) {
        ElMessage.success(`Loaded ${executionHistory.value.length} execution steps`)
      }
    },
    
    connected: (data) => {
      if (data.connected) {
        log('✅ WebSocket connected event received')
      }
    }
  }
  
  // 批量注册订阅
  Object.entries(subscriptions).forEach(([event, handler]) => {
    subscribe(event, handler)
  })
  
  subscriptionsSetup.value = true
  log('✅ All subscriptions set up')
  log('📊 Final stats:', getStats())
}

const handleHistoryStepChange = (worldState) => {
  log('🎬 History step changed, updating map with state:', worldState)
  mapViewerRef.value?.updateMap(worldState)
}

// 监听连接状态（优化版）
watch(isConnected, (newVal) => {
  log(`🔌 Connection status changed: ${newVal}`)
  if (newVal && !subscriptionsSetup.value) {
    log('🎯 Connection established, setting up subscriptions...')
    setupSubscriptions()
  }
}, { immediate: true })

onMounted(() => {
  log('🚀 App.vue mounted')
  log('🔌 Initial connection status:', isConnected.value)
  
  // 如果已经连接，立即设置订阅
  if (isConnected.value) {
    setupSubscriptions()
  }
})

// ========== 动作处理（优化版）==========

// 添加动作（带错误回滚）
const handleAddAction = async (actionData) => {
  const { agent, action } = actionData
  
  if (!actions.value[agent]) {
    actions.value[agent] = []
  }
  
  actions.value[agent].push(action)
  
  try {
    await saveActions(actions.value)
    ElMessage.success(`Successfully added action for ${agent}`)
  } catch (error) {
    handleApiError(error, 'Failed to save action to server')
    // 回滚操作
    actions.value[agent].pop()
  }
}

// 执行动作计划（统一错误处理）
const handleExecute = async () => {
  if (Object.keys(actions.value).length === 0) {
    ElMessage.warning('No actions to execute')
    return
  }

  executing.value = true
  
  try {
    // 先保存当前的动作到服务器
    await saveActions(actions.value)
    
    // 触发执行
    const result = await executeActions()
    
    result.success 
      ? ElMessage.success('Action plan submitted for execution!')
      : ElMessage.error(result.message || 'Failed to execute action plan')
  } catch (error) {
    handleApiError(error, 'Failed to execute action plan')
  } finally {
    executing.value = false
  }
}

// 清除所有状态（统一错误处理）
const handleClearAll = async () => {
  try {
    await ElMessageBox.confirm(
      'Are you sure you want to clear all states?',
      'Warning',
      {
        confirmButtonText: 'OK',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    )
    
    // 清除本地状态
    actions.value = {}
    
    try {
      await clearActions()
      const result = await resetAll()

      result.success 
        ? ElMessage.success('System reset successfully!')
        : ElMessage.error('Failed to reset system')
    } catch (error) {
      handleApiError(error, 'Failed to reset system states')
    }
  } catch {
    // 用户取消操作
  }
}
</script>

<style scoped>
.app-container {
  height: 98.4vh;
  background-color: #f5f7fa;
  overflow: hidden;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.header-content h1 {
  margin: 0;
  color: #303133;
  font-size: 28px;
}

.left-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
}
</style>