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
            @click="loadData"
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
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Files, Document } from '@element-plus/icons-vue'
import { wsService } from '@/services/websocket'
import { getRecipes, getOrders } from '@/api/actions'

// 移除 props，不再需要 autoRefresh 和 refreshInterval
// const props = defineProps({ ... })

const recipes = ref([])
const orders = ref([])
const loading = ref(false)
const isConnected = ref(false)
const unsubscribers = []

// 加载数据（手动刷新时调用）
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

// 通过 WebSocket 更新配置（父组件或自动推送调用）
const updateConfig = (data) => {
  console.log('⚙️ Updating config from WebSocket push:', data)
  
  // 从 config_update 消息中提取数据
  // 注意：后端的 config_update 包含统计信息，不包含完整的 recipes 和 orders
  // 我们需要保留当前的 recipes 和 orders，或者从其他 WebSocket 消息获取
  
  // 如果后端发送了 recipes_count 和 orders_count，我们只更新显示
  // 实际的 recipes 和 orders 列表需要通过初始数据或专门的 WebSocket 消息获取
}

// 从世界状态更新中提取 recipes 和 orders
const updateFromWorldState = (data) => {
  console.log('🌍 Updating from world state')
  
  // 当接收到完整的世界状态时，可能包含 recipes 和 orders
  if (data.recipes !== undefined) {
    recipes.value = data.recipes || []
  }
  
  if (data.orders !== undefined) {
    orders.value = data.orders || []
  }
}

// 生命周期钩子
onMounted(() => {
  // 订阅连接状态
  const unsubscribeConnected = wsService.subscribe('connected', (data) => {
    isConnected.value = data.connected
  })
  unsubscribers.push(unsubscribeConnected)
  
  // 订阅配置更新（WebSocket 推送）
  const unsubscribeConfigUpdate = wsService.subscribe('config_update', (data) => {
    console.log('⚙️ Config update received via WebSocket')
    updateConfig(data)
  })
  unsubscribers.push(unsubscribeConfigUpdate)
  
  // 订阅地图更新（因为地图更新可能包含完整的世界状态）
  const unsubscribeMapUpdate = wsService.subscribe('map_update', (data) => {
    // 地图更新时也可能需要更新 recipes 和 orders
    // 取决于后端发送的数据结构
  })
  unsubscribers.push(unsubscribeMapUpdate)
  
  // 初始化连接状态
  isConnected.value = wsService.getConnectionState()
  
  // 初次加载数据（如果 WebSocket 还没发送初始数据）
  loadData()
})

onUnmounted(() => {
  // 清理所有订阅
  unsubscribers.forEach(unsub => unsub())
})

// 暴露方法给父组件
defineExpose({
  updateConfig,
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