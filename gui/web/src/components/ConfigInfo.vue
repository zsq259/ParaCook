<template>
  <el-card shadow="hover" class="config-card" v-loading="loading">
    <template #header>
      <div class="card-header-flex">
        <span class="card-header">Current Test Recipes and Orders</span>
        <el-space>
          <!-- WebSocket 连接状态指示器 -->
          <el-tag 
            :type="isConnected ? 'success' : 'danger'" 
            size="small"
            effect="plain"
          >
            {{ isConnected ? '● Live' : '● Disconnected' }}
          </el-tag>
          <el-button 
            size="small" 
            @click="handleRefresh"
            :loading="loading"
            :icon="Refresh"
          >
            Refresh
          </el-button>
        </el-space>
      </div>
    </template>
    <div class="config-info">
      <div class="config-section">
        <div class="section-title">
          <el-icon><Files /></el-icon>
          <span>Recipes ({{ recipes.length }})</span>
        </div>
        <div class="config-content scrollable">
          <template v-if="recipes.length > 0">
            <el-tag 
              v-for="(recipe, index) in recipes" 
              :key="index"
              type="success"
              effect="plain"
              class="recipe-tag"
            >
              {{ recipe }}
            </el-tag>
          </template>
          <div v-else class="empty-state">
            <el-icon><Document /></el-icon>
            <span>No recipes configured</span>
          </div>
        </div>
      </div>
      
      <el-divider />
      
      <div class="config-section">
        <div class="section-title">
          <el-icon><Document /></el-icon>
          <span>Orders ({{ orders.length }})</span>
        </div>
        <div class="config-content scrollable">
          <template v-if="orders.length > 0">
            <el-tag 
              v-for="(order, index) in orders" 
              :key="index"
              type="warning"
              effect="plain"
              class="order-tag"
            >
              {{ order }}
            </el-tag>
          </template>
          <div v-else class="empty-state">
            <el-icon><Files /></el-icon>
            <span>No orders configured</span>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Files, Document } from '@element-plus/icons-vue'
import { wsService } from '@/services/websocket'
import { getRecipes, getOrders } from '@/api/actions'

const recipes = ref([])
const orders = ref([])
const loading = ref(false)
const isConnected = ref(false)
const unsubscribers = []

// 加载数据（手动刷新或重连时调用）
const loadData = async (showMessage = false) => {
  loading.value = true
  try {
    // 并行请求 recipes 和 orders
    const [recipesResult, ordersResult] = await Promise.all([
      getRecipes(),
      getOrders()
    ])
    
    if (recipesResult.success) {
      recipes.value = recipesResult.data || []
      console.log(`📋 Loaded ${recipes.value.length} recipes`)
    } else if (showMessage) {
      ElMessage.warning('Failed to load recipes')
    }
    
    if (ordersResult.success) {
      orders.value = ordersResult.data || []
      console.log(`📦 Loaded ${orders.value.length} orders`)
    } else if (showMessage) {
      ElMessage.warning('Failed to load orders')
    }
    
    if (showMessage && recipesResult.success && ordersResult.success) {
      ElMessage.success('Config data refreshed')
    }
  } catch (error) {
    console.error('Failed to load config data:', error)
    if (showMessage) {
      ElMessage.error('Failed to load recipes and orders')
    }
  } finally {
    loading.value = false
  }
}

// 手动刷新按钮点击处理
const handleRefresh = () => {
  loadData(true)
}

// 通过 WebSocket 更新配置
const updateConfig = (data) => {
  console.log('⚙️ Config update received via WebSocket:', data)
  
  let updated = false
  
  if (data.recipes !== undefined) {
    recipes.value = data.recipes || []
    console.log(`  📋 Updated recipes: ${recipes.value.length} items`)
    updated = true
  }
  
  if (data.orders !== undefined) {
    orders.value = data.orders || []
    console.log(`  📦 Updated orders: ${orders.value.length} items`)
    updated = true
  }
  
  if (!updated && (data.recipes_count !== undefined || data.orders_count !== undefined)) {
    console.log(`  ℹ️ Received count info: recipes=${data.recipes_count}, orders=${data.orders_count}`)
  }
}

// 清空数据（系统重置时调用）
const clearData = () => {
  console.log('🧹 Clearing config data')
  recipes.value = []
  orders.value = []
}

// 生命周期钩子
onMounted(() => {
  console.log('📊 ConfigInfo component mounted')
  
  // 1. 订阅连接状态
  const unsubscribeConnected = wsService.subscribe('connected', (data) => {
    const wasDisconnected = !isConnected.value
    isConnected.value = data.connected
    
    if (data.connected) {
      console.log('✅ WebSocket connected, waiting for initial data push')
      if (wasDisconnected) {
        console.log('🔄 Reconnected, initial data will be pushed by server')
      }
    } else {
      console.log('⚠️ WebSocket disconnected')
    }
  })
  unsubscribers.push(unsubscribeConnected)
  
  // 2. 订阅配置更新（最重要的数据源）
  const unsubscribeConfigUpdate = wsService.subscribe('config_update', (data) => {
    console.log('📨 Config update message received')
    updateConfig(data)
  })
  unsubscribers.push(unsubscribeConfigUpdate)
  
  // 3. 订阅系统重置
  const unsubscribeReset = wsService.subscribe('system_reset', () => {
    console.log('🔄 System reset received')
    clearData()
    ElMessage.info('System has been reset')
  })
  unsubscribers.push(unsubscribeReset)
  
  // 初始化连接状态
  isConnected.value = wsService.getConnectionState()
  console.log(`Initial connection state: ${isConnected.value ? 'connected' : 'disconnected'}`)
  
  // 初次加载数据（作为备用）
  if (!isConnected.value) {
    console.log('WebSocket not connected, loading data via HTTP API')
    loadData(false)
  } else {
    console.log('WebSocket connected, waiting for server push')
  }
})

onUnmounted(() => {
  console.log('📊 ConfigInfo component unmounting, cleaning up subscriptions')
  unsubscribers.forEach(unsub => unsub())
})

// 暴露方法给父组件
defineExpose({
  loadData,
  updateConfig,
  clearData,
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
  padding: 6px 10px;
}

.config-card :deep(.el-card__body) {
  padding: 6px 10px;
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
  gap: 12px;
  flex-direction: column;
}

.config-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
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

/* 添加滚动样式 */
.config-content.scrollable {
  max-height: 56px; /* 最大高度约4行标签 */
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 4px; /* 为滚动条留出空间 */
}

/* 美化滚动条 */
.config-content.scrollable::-webkit-scrollbar {
  width: 6px;
}

.config-content.scrollable::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.config-content.scrollable::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.config-content.scrollable::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

.recipe-tag,
.order-tag {
  font-size: 13px;
}

.empty-state {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
  font-size: 13px;
  font-style: italic;
}

.empty-state .el-icon {
  font-size: 14px;
}

:deep(.el-divider--horizontal) {
  margin: 0 0;
}
</style>