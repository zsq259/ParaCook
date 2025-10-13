<template>
  <el-container class="app-container">
    <el-header height="60px">
      <div class="header-content">
        <h1>ParaCook Testing GUI</h1>
        <el-space>
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
        <el-col :span="12">
          <div class="left-panel">
            <MapViewer 
              ref="mapViewerRef"
              :auto-refresh="!taskCompleted"
              :refresh-interval="3000"
            />
            <!-- 日志查看器 -->
            <LogViewer />
          </div>
        </el-col>

        <!-- 右侧：动作编辑区域 -->
        <el-col :span="12">
          <!-- <el-space direction="vertical" :size="18" style="width: 100%"> -->
            <div class="right-panel">
            <!-- 配置信息 -->
            <ConfigInfo 
              ref="configInfoRef"
              :auto-refresh="true" 
              :refresh-interval="5000" 
            />

            <!-- 动作编辑器 -->
            <ActionEditor 
              v-model:actions="actions"
              :agent-names="agentNames"
            />

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
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted  } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoPlay } from '@element-plus/icons-vue'  // 【新增】导入图标
import MapViewer from './components/MapViewer.vue'
import ConfigInfo from './components/ConfigInfo.vue'
import ActionEditor from './components/ActionEditor.vue'
import ActionForm from './components/ActionForm.vue'
import LogViewer from './components/LogViewer.vue'
import { 
  executeActions, 
  clearActions, 
  saveActions, 
  getAgents,
  getTaskStatus,
  resetTask,
  resetAll
} from './api/actions'

// 状态管理
const mapViewerRef = ref(null)
const agentNames = ref([])
const actions = ref({})
const configInfoRef = ref(null)
const executing = ref(false)
const loading = ref(false)
const taskCompleted = ref(false)

let statusCheckTimer = null

const refreshConfig = () => {
  if (taskCompleted.value) return
  configInfoRef.value?.loadData()
  mapViewerRef.value?.loadMapData()
  loadAgents()
}

const checkTaskStatus = async () => {
  try {
    const result = await getTaskStatus()
    if (result.success && result.completed && !taskCompleted.value) {
      taskCompleted.value = true
      ElMessage({
        message: '🎉 All orders completed successfully!',
        type: 'success',
        duration: 0,  // 不自动关闭
        showClose: true
      })
      
      // 停止自动刷新
      if (statusCheckTimer) {
        clearInterval(statusCheckTimer)
        statusCheckTimer = null
      }
    }
  } catch (error) {
    // 忽略错误，避免在服务器关闭时报错
  }
}

const loadAgents = async () => {
  if (taskCompleted.value) return
  loading.value = true
  try {
    const result = await getAgents()
    if (result.success && result.data) {
      agentNames.value = result.data
    } else {
      ElMessage.warning('No agents found')
    }
  } catch (error) {
    console.error('Failed to load agents:', error)
    ElMessage.error('Failed to load agent list')
    // 如果加载失败，使用空列表
    agentNames.value = []
    
  } finally {
    loading.value = false
  }
}

// 添加动作
const handleAddAction = async (actionData) => {
  const { agent, action } = actionData
  
  if (!actions.value[agent]) {
    actions.value[agent] = []
  }
  
  actions.value[agent].push(action)
  
    // 【新增】自动保存到服务器
  try {
    await saveActions(actions.value)
    ElMessage.success(`Successfully added action for ${agent}`)
  } catch (error) {
    console.error('Failed to save actions:', error)
    ElMessage.error('Failed to save action to server')
  }
  refreshConfig()
}

// 执行动作计划
const handleExecute = async () => {  // 【修改】改为 async，并添加完整逻辑
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
      ElMessage.error(result.message || 'Failed to execute')
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
    taskCompleted.value = false
    
    // 【新增】清除服务器状态
    try {
      await clearActions()
      await resetTask()
      const result = await resetAll()

      if (result.success) {
        ElMessage.success('System reset successfully!')
        if (!statusCheckTimer) {
          statusCheckTimer = setInterval(checkTaskStatus, 2000)
        }
        
        refreshConfig()
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

onMounted(() => {
  loadAgents()
  refreshConfig()
  checkTaskStatus()
  statusCheckTimer = setInterval(checkTaskStatus, 2000)
})

onUnmounted(() => {
  if (statusCheckTimer) {
    clearInterval(statusCheckTimer)
  }
})
</script>

<style scoped>
.app-container {
  height: 60.3em;
  background-color: #f5f7fa;
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