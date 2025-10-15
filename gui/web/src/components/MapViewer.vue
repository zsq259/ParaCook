<template>
  <el-card shadow="hover" class="map-card">
    <template #header>
      <div class="card-header-flex">
        <span class="card-header">Map Visualization</span>
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
            @click="loadMapData"
            :loading="loading"
            :icon="Refresh"
          >
            Refresh
          </el-button>
        </el-space>
      </div>
    </template>
    
    <div class="map-content" v-loading="loading">
      <!-- 地图网格（带坐标轴） -->
      <div v-if="mapData" class="map-grid-container" ref="mapContainer">
        <div class="map-with-axes">
          <!-- 左上角空白 -->
          <div class="axis-corner"></div>
          
          <!-- 上方 X 轴刻度 -->
          <div class="x-axis">
            <div 
              v-for="x in mapData.width" 
              :key="`x-${x-1}`"
              class="axis-label"
            >
              {{ x - 1 }}
            </div>
          </div>
          
          <!-- 左侧 Y 轴刻度 -->
          <div class="y-axis">
            <div 
              v-for="y in mapData.height" 
              :key="`y-${y-1}`"
              class="axis-label"
            >
              {{ y - 1 }}
            </div>
          </div>
          
          <!-- 地图网格 -->
          <div 
            class="map-grid"
            :style="{
              gridTemplateColumns: `repeat(${mapData.width}, 1fr)`,
              gridTemplateRows: `repeat(${mapData.height}, 1fr)`
            }"
          >
            <div
              v-for="(cell, index) in gridCells"
              :key="index"
              class="map-cell"
              :class="getCellClass(cell)"
              @mouseenter="handleCellHover($event, cell)"
              @mousemove="handleMouseMove"
              @mouseleave="hoveredCell = null"
            >
              <div class="cell-content">
                <!-- 使用图片 -->
                <img 
                  v-if="getCellImage(cell)" 
                  :src="getCellImage(cell)" 
                  class="cell-image"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 悬浮提示 -->
        <div 
          v-if="hoveredCell && hoveredCell.data" 
          class="cell-tooltip-wrapper"
          :style="tooltipStyle"
        >
          <el-card 
            class="cell-tooltip"
            shadow="always"
          >
            <template #header>
              <strong>
                {{ Array.isArray(hoveredCell.data) && hoveredCell.data.length > 1 
                    ? `Multiple Agents (${hoveredCell.data.length})` 
                    : (hoveredCell.data.name || hoveredCell.data[0]?.name || 'Empty') 
                }}
              </strong>
            </template>
            <div class="tooltip-content">
              <div><strong>Position:</strong> ({{ hoveredCell.x }}, {{ hoveredCell.y }})</div>
              <template v-if="Array.isArray(hoveredCell.data) && hoveredCell.data.length > 0">
                <div v-for="(agent, idx) in hoveredCell.data" :key="idx" class="agent-info">
                  <el-divider v-if="idx > 0" style="margin: 8px 0" />
                  <div><strong>Agent {{ idx + 1 }}:</strong> {{ agent.name }}</div>
                  <div v-if="agent.holding !== undefined">
                    <strong>Holding:</strong> {{ agent.holding || 'Nothing' }}
                  </div>
                  <div v-if="agent.current_action !== undefined">
                    <strong>Action:</strong> {{ agent.current_action || 'Idle' }}
                  </div>
                </div>
              </template>
              <template v-else-if="hoveredCell.data && !Array.isArray(hoveredCell.data)">
                <div v-if="hoveredCell.data.type">
                  <strong>Type:</strong> {{ hoveredCell.data.type }}
                </div>
                <div v-if="hoveredCell.data.provides">
                  <strong>Provides:</strong> {{ hoveredCell.data.provides }}
                </div>
                <div v-if="hoveredCell.data.holding !== undefined">
                  <strong>Holding:</strong> {{ hoveredCell.data.holding || 'Nothing' }}
                </div>
                <div v-if="hoveredCell.data.current_action !== undefined">
                  <strong>Action:</strong> {{ hoveredCell.data.current_action || 'Idle' }}
                </div>
                <div v-if="hoveredCell.data.item">
                  <strong>Item:</strong> {{ formatItem(hoveredCell.data.item) }}
                </div>
                <div v-if="hoveredCell.data.in_use">
                  <strong>In Use:</strong> {{ hoveredCell.data.current_user || 'Yes' }}
                </div>
                <div v-if="hoveredCell.data.dirty_plates_sum !== undefined">
                  <strong>Dirty Plates:</strong> {{ hoveredCell.data.dirty_plates_sum }}
                </div>
              </template>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 无数据提示 -->
      <div v-else class="map-placeholder">
        <el-empty 
          description="No map data available. Waiting for world updates..."
          :image-size="150"
        />
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { wsService } from '@/services/websocket'
import { getWorld } from '@/api/actions'

import agentImg from '@/assets/images/agent.png'
import agent1Img from '@/assets/images/agent1.png'
import agent2Img from '@/assets/images/agent2.png'
import agent3Img from '@/assets/images/agent3.png'
import breadImg from '@/assets/images/ingredients/bread.png'
import fish from '@/assets/images/ingredients/fish.png'
import lettuceImg from '@/assets/images/ingredients/lettuce.png'
import meatImg from '@/assets/images/ingredients/meat.png'
import mushroomImg from '@/assets/images/ingredients/mushroom.png'
import pastaImg from '@/assets/images/ingredients/pasta.png'
import prawnImg from '@/assets/images/ingredients/prawn.png'
import tomatoImg from '@/assets/images/ingredients/tomato.png'
import panImg from '@/assets/images/items/pan.png'
import plateImg from '@/assets/images/items/plate.png'
import potImg from '@/assets/images/items/pot.png'
import chopping_boardImg from '@/assets/images/stations/chopping_board.png'
import plate_returnImg from '@/assets/images/stations/plate_return.png'
import serving_windowImg from '@/assets/images/stations/serving_window.png'
import sinkImg from '@/assets/images/stations/sink.png'
import stoveImg from '@/assets/images/stations/stove.png'
import tableImg from '@/assets/images/stations/table.png'
import wallImg from '@/assets/images/stations/wall.png'

// 移除 props，不再需要 autoRefresh 和 refreshInterval
// const props = defineProps({ ... })

const mapData = ref(null)
const loading = ref(false)
const hoveredCell = ref(null)
const isConnected = ref(false)
const unsubscribers = []

const mapContainer = ref(null)
const mousePosition = ref({ x: 0, y: 0 })
const tooltipStyle = computed(() => {
  if (!hoveredCell.value || !mapContainer.value) return {}
  
  const offsetX = 15 // 基础水平偏移
  const offsetY = 15 // 基础垂直偏移
  const tooltipWidth = 320 // 提示框估计宽度
  const tooltipHeight = 200 // 提示框估计高度
  
  const containerRect = mapContainer.value.getBoundingClientRect()
  const containerWidth = containerRect.width
  const containerHeight = containerRect.height
  
  let left = mousePosition.value.x + offsetX
  let top = mousePosition.value.y - tooltipHeight - offsetY
  
  // 水平方向调整：如果右侧空间不足，显示在鼠标左侧
  if (left + tooltipWidth > containerWidth) {
    left = mousePosition.value.x - tooltipWidth - offsetX
  }
  
  // 垂直方向调整：如果上方空间不足，显示在鼠标下方
  if (top < 0) {
    top = mousePosition.value.y + offsetY
  }
  
  // 确保不会完全超出左边界
  if (left < 0) {
    left = offsetX
  }
  
  // 确保不会完全超出下边界
  if (top + tooltipHeight > containerHeight) {
    top = containerHeight - tooltipHeight - offsetY
  }
  
  return {
    left: `${left}px`,
    top: `${top}px`,
  }
})

const handleCellHover = (event, cell) => {
  hoveredCell.value = cell
  updateMousePosition(event)
}

const handleMouseMove = (event) => {
  if (hoveredCell.value) {
    updateMousePosition(event)
  }
}

const updateMousePosition = (event) => {
  if (!mapContainer.value) return
  
  const rect = mapContainer.value.getBoundingClientRect()
  mousePosition.value = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }
}

// 加载地图数据（手动刷新时调用）
const loadMapData = async () => {
  loading.value = true
  try {
    const result = await getWorld()
    if (result.success && result.data) {
      mapData.value = result.data.world
    } else {
      console.warn('No map data available')
    }
  } catch (error) {
    console.error('Failed to load map data:', error)
    ElMessage.error('Failed to load map data')
  } finally {
    loading.value = false
  }
}

// 通过 WebSocket 更新地图（父组件或自动推送调用）
const updateMap = (data) => {
  console.log('📍 Updating map from WebSocket push')
  mapData.value = data
}

// 生成网格单元格数据
const gridCells = computed(() => {
  if (!mapData.value) return []
  
  const cells = []
  const { width, height, agents = [], tiles = [] } = mapData.value
  
  // 创建位置索引
  const tileMap = {}
  tiles.forEach(tile => {
    const key = `${tile.x},${tile.y}`
    tileMap[key] = tile
  })
  
  const agentMap = {}
  agents.forEach(agent => {
    const key = `${agent.x},${agent.y}`
    if (!agentMap[key]) {
      agentMap[key] = []
    }
    agentMap[key].push(agent)
  })
  
  // 生成所有格子（从上到下，从左到右）
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const key = `${x},${y}`
      const agentsAtPos = agentMap[key] || []
      const tile = tileMap[key]
      
      cells.push({
        x,
        y,
        agents: agentsAtPos,  // ✅ 改为 agents（复数）
        tile,
        data: agentsAtPos.length > 0 ? agentsAtPos : (tile || null)
      })
    }
  }
  
  return cells
})

// 获取格子的样式类
const getCellClass = (cell) => {
  if (cell.agents && cell.agents.length > 0) return 'cell-agent'
  
  if (cell.tile) {
    if (cell.tile.type === 'obstacle') return 'cell-wall'
    if (cell.tile.name.includes('dispenser')) return 'cell-dispenser'
    if (cell.tile.name.includes('chopping')) return 'cell-chopping'
    if (cell.tile.name.includes('stove')) return 'cell-stove'
    if (cell.tile.name.includes('table')) return 'cell-table'
    if (cell.tile.name.includes('serving')) return 'cell-serving'
    if (cell.tile.name.includes('sink')) return 'cell-sink'
    if (cell.tile.name.includes('plate_return')) return 'cell-plate-return'
    return 'cell-station'
  }
  return 'cell-empty'
}

// 获取格子显示的图片
const getCellImage = (cell) => {
  if (cell.agents && cell.agents.length > 0) {
    const agent = cell.agents[0]  // 取第一个 agent
    if (agent.name.includes('1')) return agent1Img
    if (agent.name.includes('2')) return agent2Img
    if (agent.name.includes('3')) return agent3Img
    return agentImg
  }
  
  if (cell.tile) {
    if (cell.tile.type === 'obstacle') return wallImg
    if (cell.tile.name.includes('dispenser')) {
      // 根据提供的物品返回不同图片
      if (cell.tile.provides === 'bread') return breadImg
      if (cell.tile.provides === 'fish') return fish
      if (cell.tile.provides === 'lettuce') return lettuceImg
      if (cell.tile.provides === 'meat') return meatImg
      if (cell.tile.provides === 'mushroom') return mushroomImg
      if (cell.tile.provides === 'pasta') return pastaImg
      if (cell.tile.provides === 'prawn') return prawnImg
      if (cell.tile.provides === 'tomato') return tomatoImg
      if (cell.tile.provides === 'pan') return panImg
      if (cell.tile.provides === 'plate') return plateImg
      if (cell.tile.provides === 'pot') return potImg
    }
    if (cell.tile.name.includes('chopping')) return chopping_boardImg
    if (cell.tile.name.includes('stove')) {
      if (cell.tile.item && cell.tile.item.name === 'pan') return panImg
      if (cell.tile.item && cell.tile.item.name === 'pot') return potImg
      return stoveImg
    }
    if (cell.tile.name.includes('table')) {
      if (cell.tile.item && cell.tile.item.name === 'pan') return panImg
      if (cell.tile.item && cell.tile.item.name === 'pot') return potImg
      if (cell.tile.item && cell.tile.item.name === 'plate') return plateImg
      return tableImg
    }
    if (cell.tile.name.includes('serving')) return serving_windowImg
    if (cell.tile.name.includes('sink')) return sinkImg
    if (cell.tile.name.includes('plate_return')) return plate_returnImg
  }
  
  return null
}

// 格式化物品信息
const formatItem = (item) => {
  if (!item) return 'None'
  if (typeof item === 'string') return item
  if (item.name) {
    let info = item.name
    if (item.contents && item.contents.length > 0) {
      info += ` (${item.contents.join(', ')})`
    }
    if (item.finished) info += ' ✓'
    if (item.is_cooking) info += ' 🔥'
    return info
  }
  return JSON.stringify(item)
}

// 生命周期钩子
onMounted(() => {
  // 订阅连接状态
  const unsubscribeConnected = wsService.subscribe('connected', (data) => {
    isConnected.value = data.connected
  })
  unsubscribers.push(unsubscribeConnected)
  
  // 订阅地图更新（WebSocket 推送）
  const unsubscribeMapUpdate = wsService.subscribe('map_update', (data) => {
    console.log('🗺️ Map update received via WebSocket')
    updateMap(data)
  })
  unsubscribers.push(unsubscribeMapUpdate)
  
  // 初始化连接状态
  isConnected.value = wsService.getConnectionState()
  
  // 初次加载地图数据（如果 WebSocket 还没发送初始数据）
  if (!mapData.value) {
    loadMapData()
  }
})

onUnmounted(() => {
  // 清理所有订阅
  unsubscribers.forEach(unsub => unsub())
})

// 暴露方法给父组件
defineExpose({
  updateMap,
  loadMapData,
  mapData
})
</script>

<style scoped>
.map-card {
  height: auto;
  width: 100%;
}

.map-card :deep(.el-card__header) {
  padding: 12px 20px;
}

.map-card :deep(.el-card__body) {
  padding: 10px;
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

.map-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.map-grid-container {
  position: relative;
  display: flex;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 8px;
}

.agent-info {
  padding: 4px 0;
}

.agent-info > div {
  margin: 4px 0;
}

/* 带坐标轴的地图布局 */
.map-with-axes {
  display: grid;
  grid-template-columns: auto 1fr;
  grid-template-rows: auto 1fr;
  gap: 5px;
}

.x-axis {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: 1fr;
  gap: 2px;
  padding: 0 2px;
}

.y-axis {
  display: grid;
  grid-auto-flow: row;
  grid-auto-rows: 1fr;
  gap: 2px;
  padding: 2px 0;
}

.axis-label {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #606266;
  min-width: 40px;
  min-height: 40px;
  max-width: 60px;
  max-height: 60px;
  aspect-ratio: 1;
}

.map-grid {
  display: grid;
  gap: 2px;
  background: #dcdfe6;
  padding: 2px;
  border-radius: 4px;
}

.map-cell {
  background: white;
  aspect-ratio: 1;
  min-width: 40px;
  min-height: 40px;
  max-width: 60px;
  max-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 20px;
  position: relative;
  border-radius: 2px;
}

.map-cell:hover {
  transform: scale(1.15);
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}

.cell-content {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.cell-image {
  width: 32px;
  height: 32px;
  object-fit: contain;
  pointer-events: none;
}

.cell-empty {
  background: #f5f5f5;
  opacity: 0.6;
}

.cell-agent {
  background: #f5f5f5;
  font-size: 24px;
}

.cell-wall {
  background: #909399;
  opacity: 0.8;
}

.cell-dispenser {
  background: linear-gradient(135deg, #ecae1e 0%, #c08b10 100%);
  border: 2px solid #bf7103;
}

.cell-chopping {
  background: linear-gradient(135deg, #fdf6ec 0%, #faecd8 100%);
  border: 2px solid #e6a23c;
}

.cell-stove {
  background: linear-gradient(135deg, #fff0f0 0%, #ffe6e6 100%);
  border: 2px solid #409eff;
}

.cell-table {
  background: linear-gradient(135deg, #f4f4f5 0%, #e9e9eb 100%);
  border: 2px solid #e8bb28;
}

.cell-station {
  background: linear-gradient(135deg, #f0f9ff 0%, #e1f3ff 100%);
  border: 2px solid #409eff;
}

.cell-serving,
.cell-sink,
.cell-plate-return {
  background: linear-gradient(135deg, #e1f3d8 0%, #d4edda 100%);
  border: 2px solid #67c23a;
}

.cell-tooltip-wrapper {
  position: absolute;
  z-index: 1000;
  pointer-events: none;
}

.cell-tooltip {
  max-width: 320px;
  min-width: 250px;
  font-size: 13px;
  box-shadow: 0 8px 16px rgba(0,0,0,0.15);
  pointer-events: auto;
}

.cell-tooltip :deep(.el-card__header) {
  padding: 12px 15px;
  background: #f5f7fa;
}

.cell-tooltip :deep(.el-card__body) {
  padding: 12px 15px;
}

.tooltip-content > div {
  margin: 6px 0;
  line-height: 1.8;
  word-break: break-word;
}

.tooltip-content strong {
  color: #303133;
  margin-right: 5px;
}

.map-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  padding: 60px 20px;
  min-height: 300px;
  gap: 15px;
}
</style>