<template>
  <el-card shadow="hover" class="action-form-card" v-loading="loading">
    <template #header>
      <span class="card-header">Add New Action</span>
    </template>

    <el-form 
      ref="formRef"
      :model="formData" 
      :rules="rules"
      label-width="140px"
      label-position="left"
    >
      <!-- 选择 Agent -->
      <el-form-item label="Choose Agent" prop="agent">
        <el-select 
          v-model="formData.agent" 
          placeholder="Select an agent"
          style="width: 100%"
        >
          <el-option
            v-for="agent in agentNames"
            :key="agent"
            :label="agent"
            :value="agent"
          />
        </el-select>
      </el-form-item>

      <!-- 选择动作类型 -->
      <el-form-item label="Action Type" prop="actionType">
        <el-radio-group v-model="formData.actionType" size="small">
          <el-radio-button 
            v-for="type in actionTypes" 
            :key="type"
            :label="type"
          >
            {{ type }}
          </el-radio-button>
        </el-radio-group>
      </el-form-item>

      <!-- MoveTo 参数 -->
      <el-form-item 
        v-if="formData.actionType === 'MoveTo'" 
        label="Target Coordinates"
        prop="coordinates"
      >
        <el-row :gutter="10">
          <el-col :span="11">
            <el-input-number 
              v-model="formData.x" 
              placeholder="X"
              style="width: 100%"
              :controls="false"
            />
          </el-col>
          <el-col :span="2" style="text-align: center; line-height: 32px">
            ,
          </el-col>
          <el-col :span="11">
            <el-input-number 
              v-model="formData.y" 
              placeholder="Y"
              style="width: 100%"
              :controls="false"
            />
          </el-col>
        </el-row>
      </el-form-item>

      <!-- Wait 参数 -->
      <el-form-item 
        v-if="formData.actionType === 'Wait'" 
        label="Wait Duration"
        prop="duration"
      >
        <el-input-number 
          v-model="formData.duration"
          :min="1"
          :step="1"
          style="width: 100%"
        />
      </el-form-item>

      <!-- Interact/Process 参数 -->
      <el-form-item 
        v-if="['Interact', 'Process'].includes(formData.actionType)" 
        label="Target Object"
        prop="target"
      >
        <el-input 
          v-model="formData.target"
          placeholder="Enter target object name"
        />
      </el-form-item>

      <!-- 提交按钮 -->
      <el-form-item>
        <el-button 
          type="primary" 
          @click="handleSubmit"
          style="width: 100%"
        >
          <el-icon style="margin-right: 5px">
            <Plus />
          </el-icon>
          Add Action
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { addAction as apiAddAction } from '@/api/actions'  // 新增这行

const props = defineProps({
  agentNames: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['add-action'])

const formRef = ref(null)
const actionTypes = ['MoveTo', 'Wait', 'Interact', 'Process', 'Finish']

const formData = reactive({
  agent: '',
  actionType: 'MoveTo',
  x: null,
  y: null,
  duration: 1,
  target: ''
})

// 监听 agent 列表变化，自动选择第一个
watch(() => props.agentNames, (newVal) => {
  if (newVal.length > 0 && !formData.agent) {
    formData.agent = newVal[0]
  }
}, { immediate: true })

// 表单验证规则
const rules = {
  agent: [
    { required: true, message: 'Please select an agent', trigger: 'change' }
  ],
  actionType: [
    { required: true, message: 'Please select an action type', trigger: 'change' }
  ],
  coordinates: [
    {
      validator: (rule, value, callback) => {
        if (formData.actionType === 'MoveTo') {
          if (formData.x === null || formData.y === null) {
            callback(new Error('Please enter both X and Y coordinates'))
          } else {
            callback()
          }
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  duration: [
    { 
      required: true, 
      message: 'Please enter wait duration', 
      trigger: 'blur',
      type: 'number'
    }
  ],
  target: [
    { 
      required: true, 
      message: 'Please enter target object name', 
      trigger: 'blur' 
    }
  ]
}

// 构建动作对象
const buildAction = () => {
  const action = {
    action: formData.actionType
  }

  switch (formData.actionType) {
    case 'MoveTo':
      action.target = [formData.x, formData.y]
      break
    case 'Wait':
      action.duration = formData.duration
      break
    case 'Interact':
    case 'Process':
      action.target = formData.target
      break
  }

  return action
}

const loading = ref(false)  // 新增

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    
    const action = buildAction()
    
    loading.value = true
    const result = await apiAddAction(formData.agent, action)
    
    if (result.success) {
      // emit('add-action', {
      //   agent: formData.agent,
      //   action: action
      // })
      emit('action-added')
      
      ElMessage.success('Action added successfully')
      resetForm()
    }
  } catch (error) {
    if (error.response) {
      ElMessage.error('Failed to add action: ' + error.response.data.detail)
    } else {
      console.error('Validation failed:', error)
    }
  } finally {
    loading.value = false
  }
}

// 重置表单
const resetForm = () => {
  formData.x = null
  formData.y = null
  formData.duration = 1
  formData.target = ''
}
</script>

<style scoped>
.action-form-card {
  width: 100%;
  /* margin-bottom: 1em; */
  height: 16em;
}

.action-form-card :deep(.el-card__header) {
  padding: 12px 20px;
}

.action-form-card :deep(.el-card__body) {
  padding: 10px 20px;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
}

:deep(.el-form-item) {
  margin-bottom: 18px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-radio-button) {
  margin-right: 0;
}
</style>