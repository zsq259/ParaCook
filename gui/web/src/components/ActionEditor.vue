<template>
  <el-card shadow="hover" class="action-editor-card">
    <template #header>
      <div class="card-header-flex">
        <span class="card-header">Action Editor</span>
        <el-button 
          size="small" 
          type="primary" 
          @click="formatJson"
        >
          Format JSON
        </el-button>
      </div>
    </template>

    <div class="editor-container">
      <!-- JSON 编辑器 -->
      <div class="json-editor-wrapper">
        <el-input
          v-model="jsonString"
          type="textarea"
          :rows="10"
          placeholder="Editable Action List (JSON format)"
          class="json-editor"
          @blur="handleJsonChange"
        />
        <el-alert
          v-if="jsonError"
          :title="jsonError"
          type="error"
          :closable="false"
          show-icon
        />
      </div>

      <!-- 动作列表预览 -->
      <el-divider content-position="left" class="preview-divider">
        Action List Preview
      </el-divider>

      <div v-if="Object.keys(localActions).length === 0" class="empty-state">
        <el-empty 
          description="No actions yet. Add some actions below!"
          :image-size="80"
        />
      </div>

      <div v-else class="action-list">
        <el-collapse v-model="activeAgents" accordion>
          <el-collapse-item 
            v-for="(actionList, agent) in localActions" 
            :key="agent"
            :name="agent"
          >
            <template #title>
              <div class="collapse-title">
                <el-tag type="primary" effect="dark" size="small">{{ agent }}</el-tag>
                <el-badge 
                  :value="actionList.length" 
                  class="action-count"
                  type="info"
                />
              </div>
            </template>

            <div class="action-list-container">
              <el-card 
                v-for="(action, index) in actionList"
                :key="index"
                shadow="hover" 
                class="action-item"
              >
                <div class="action-content">
                  <span class="action-index">{{ index + 1 }}</span>
                  <el-tag :type="getActionTypeColor(action.action)" size="small">
                    {{ action.action }}
                  </el-tag>
                  <div class="action-params">
                    <span v-if="action.target !== undefined">
                      Target: 
                      <el-text type="primary">
                        {{ formatTarget(action.target) }}
                      </el-text>
                    </span>
                    <span v-if="action.duration !== undefined">
                      Duration: 
                      <el-text type="primary">{{ action.duration }}</el-text>
                    </span>
                  </div>
                  <el-button
                    type="danger"
                    size="small"
                    text
                    @click="removeAction(agent, index)"
                  >
                    Remove
                  </el-button>
                </div>
              </el-card>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  actions: {
    type: Object,
    required: true
  },
  agentNames: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:actions'])

const localActions = computed({
  get: () => props.actions,
  set: (val) => emit('update:actions', val)
})

const jsonString = ref('')
const jsonError = ref('')
const activeAgents = ref([])

// 初始化 JSON 字符串
watch(() => props.actions, (newVal) => {
  if (!jsonError.value) {
    jsonString.value = JSON.stringify(newVal, null, 2)
  }
}, { immediate: true, deep: true })

// 处理 JSON 变化
const handleJsonChange = () => {
  try {
    const parsed = JSON.parse(jsonString.value)
    localActions.value = parsed
    jsonError.value = ''
  } catch (error) {
    jsonError.value = 'Invalid JSON format: ' + error.message
  }
}

// 格式化 JSON
const formatJson = () => {
  try {
    const parsed = JSON.parse(jsonString.value)
    jsonString.value = JSON.stringify(parsed, null, 2)
    jsonError.value = ''
    ElMessage.success('JSON formatted successfully')
  } catch (error) {
    ElMessage.error('Cannot format invalid JSON')
  }
}

// 移除动作
const removeAction = (agent, index) => {
  const newActions = { ...localActions.value }
  newActions[agent].splice(index, 1)
  if (newActions[agent].length === 0) {
    delete newActions[agent]
  }
  localActions.value = newActions
  ElMessage.success('Action removed')
}

// 获取动作类型颜色
const getActionTypeColor = (actionType) => {
  const colorMap = {
    'MoveTo': 'primary',
    'Wait': 'info',
    'Interact': 'success',
    'Process': 'warning',
    'Finish': 'danger'
  }
  return colorMap[actionType] || ''
}

// 格式化目标显示
const formatTarget = (target) => {
  if (Array.isArray(target)) {
    return `[${target.join(', ')}]`
  }
  return target
}
</script>

<style scoped>
.action-editor-card {
  width: 100%;
}

.action-editor-card :deep(.el-card__header) {
  padding: 12px 20px;
}

.action-editor-card :deep(.el-card__body) {
  padding: 15px 20px;
}

.card-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
}

.editor-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.json-editor-wrapper {
  width: 100%;
}

.json-editor :deep(textarea) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.preview-divider {
  margin: -0.1em;
}

.preview-divider :deep(.el-divider__text) {
  font-size: 13px;
}

.empty-state {
  height: 20.1em;
}

.action-list {
  height: 20.1em;
  overflow-y: auto;
  padding-right: 8px;
}

.action-list::-webkit-scrollbar {
  width: 8px;
}

.action-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.action-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.action-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.collapse-title {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.action-count {
  margin-left: auto;
}

.action-list-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-item {
  margin: -0.3em;
}

.action-item :deep(.el-card__body) {
  padding: 6px 12px;
}

.action-index {
  font-weight: 600;
  color: #909399;
  min-width: 20px;
}

.action-content {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.action-params {
  display: flex;
  gap: 15px;
  flex: 1;
  font-size: 14px;
}
</style>