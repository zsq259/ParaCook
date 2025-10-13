<template>
  <el-card shadow="hover" class="config-card" v-loading="loading">
    <template #header>
      <div class="card-header-flex">
        <span class="card-header">Current Test Recipes and Orders</span>
        <el-button 
          size="small" 
          @click="loadData"
          :loading="loading"
          :icon="Refresh"
        >
          Refresh
        </el-button>
      </div>
    </template>
    <div class="config-info">
      <div class="config-section">
        <div class="section-title">
          <el-icon><Files /></el-icon>
          <span>Recipes ({{ recipes.length }})</span>
        </div>
        <div class="config-content">
          <el-tag 
            v-for="(recipe, index) in recipes" 
            :key="index"
            type="success"
            effect="plain"
            class="recipe-tag"
          >
            {{ recipe }}
          </el-tag>
          <span v-if="recipes.length === 0" class="empty-text">No recipes</span>
        </div>
      </div>
      
      <el-divider />
      
      <div class="config-section">
        <div class="section-title">
          <el-icon><Document /></el-icon>
          <span>Orders ({{ orders.length }})</span>
        </div>
        <div class="config-content">
          <el-tag 
            v-for="(order, index) in orders" 
            :key="index"
            type="warning"
            effect="plain"
            class="order-tag"
          >
            {{ order }}
          </el-tag>
          <span v-if="orders.length === 0" class="empty-text">No orders</span>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Files, Document } from '@element-plus/icons-vue'
import { getRecipes, getOrders } from '@/api/actions'

const props = defineProps({
  autoRefresh: {
    type: Boolean,
    default: false
  },
  refreshInterval: {
    type: Number,
    default: 5000 // 5秒自动刷新
  }
})

const recipes = ref([])
const orders = ref([])
const loading = ref(false)
let refreshTimer = null

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    // 并行请求 recipes 和 orders
    const [recipesResult, ordersResult] = await Promise.all([
      getRecipes(),
      getOrders()
    ])
    if (recipesResult.success) {
      recipes.value = recipesResult.data || []
    }
    
    if (ordersResult.success) {
      orders.value = ordersResult.data || []
    }
  } catch (error) {
    console.error('Failed to load config data:', error)
    ElMessage.error('Failed to load recipes and orders')
  } finally {
    loading.value = false
  }
}

// 启动自动刷新
const startAutoRefresh = () => {
  if (props.autoRefresh && !refreshTimer) {
    refreshTimer = setInterval(() => {
      loadData()
    }, props.refreshInterval)
  }
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 监听 autoRefresh 变化
watch(() => props.autoRefresh, (newVal) => {
  if (newVal) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
})

// 组件挂载时加载数据
onMounted(() => {
  loadData()
  if (props.autoRefresh) {
    startAutoRefresh()
  }
})

// 组件卸载时清理定时器
onUnmounted(() => {
  stopAutoRefresh()
})

// 暴露方法给父组件
defineExpose({
  loadData,
  recipes,
  orders
})
</script>

<style scoped>
.config-card {
  width: 100%;
  margin-bottom: 1em;
}

.config-card :deep(.el-card__header) {
  padding: 12px 20px;
}

.config-card :deep(.el-card__body) {
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

.config-info {
  display: flex;
  gap: 20px;
  flex-direction: column;
}

.config-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-top: -0.6em;
  margin-bottom: -0.3em;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #606266;
  font-size: 14px;
}

.section-title .el-icon {
  font-size: 16px;
}

.config-content {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: flex-start;
  min-height: 32px;
}

.recipe-tag,
.order-tag {
  font-size: 13px;
}

.empty-text {
  color: #909399;
  font-style: italic;
  font-size: 13px;
}

:deep(.el-divider--horizontal) {
  margin: -0.5em;
}
</style>