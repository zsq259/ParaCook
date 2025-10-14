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
import { useWebSocket } from './composables/useWebSocket'
import { 
  executeActions, 
  clearActions, 
  saveActions, 
  resetTask,
  resetAll
} from './api/actions'

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

// ========== WebSocket 事件订阅 ==========

const setupSubscriptions = () => {
  if (subscriptionsSetup.value) {
    console.log('⚠️ Subscriptions already set up, skipping...')
    return
  }
  
  console.log('✅ Setting up WebSocket subscriptions...')
  console.log('📊 WebSocket stats:', getStats())
  
  // 订阅任务状态更新
  subscribe('task_status', (data) => {
    console.log('📊 Task status update:', data)
    
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
  })

  // 订阅地图更新
  subscribe('map_update', (data) => {
    console.log('🗺️ Map update received:', data)
    mapViewerRef.value?.updateMap(data)
  })

  // 订阅配置更新
  subscribe('config_update', (data) => {
    console.log('⚙️ Config update received:', data)
    configInfoRef.value?.updateConfig(data)
  })

  // 订阅 agent 列表更新
  subscribe('agents_update', (data) => {
    console.log('👥 Agents update received:', data)
    agentNames.value = data
  })

  // 订阅动作更新
  subscribe('actions_update', (data) => {
    console.log('🎬 Actions update received:', data)
    actions.value = data.actions
  })

  // 订阅系统重置
  subscribe('system_reset', (data) => {
    console.log('🔄 System reset received:', data)
    taskCompleted.value = false
    actions.value = {}
    ElMessage.success('System has been reset to initial state')
  })

  // 连接成功后的处理
  subscribe('connected', (data) => {
    if (data.connected) {
      console.log('✅ WebSocket connected event received')
    }
  })
  
  subscriptionsSetup.value = true
  console.log('✅ All subscriptions set up')
  console.log('📊 Final stats:', getStats())
}


// 监听连接状态，连接后立即设置订阅
watch(isConnected, (newVal) => {
  console.log(`🔌 Connection status: ${newVal}`)
  if (newVal && !subscriptionsSetup.value) {
    console.log('🎯 Connection established, setting up subscriptions...')
    setupSubscriptions()
  }
}, { immediate: true })

onMounted(() => {
  console.log('🚀 App.vue mounted')
  console.log('🔌 Initial connection status:', isConnected.value)
  
  // 如果已经连接，立即设置订阅
  if (isConnected.value) {
    setupSubscriptions()
  }
})

// ========== 动作处理 ==========

// 添加动作
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
    console.error('Failed to save actions:', error)
    ElMessage.error('Failed to save action to server')
  }
}

// 执行动作计划
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
    
    if (result.success) {
      ElMessage.success('Action plan submitted for execution!')
    } else {
      ElMessage.error(result.message || 'Failed to execute action plan')
    }
  } catch (error) {
    console.error('Execute error:', error)
    ElMessage.error('Failed to execute action plan')
  } finally {
    executing.value = false
  }
}

// 清除所有状态
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
      await resetTask()
      const result = await resetAll()

      if (result.success) {
        ElMessage.success('System reset successfully!')
        // WebSocket 会自动推送更新，无需手动刷新
      } else {
        ElMessage.error('Failed to reset system')
      }
    } catch (error) {
      console.error('Failed to reset system:', error)
      ElMessage.error('Failed to reset system states')
    }
  } catch {
    // 用户取消
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