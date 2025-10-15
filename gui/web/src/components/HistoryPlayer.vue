<template>
  <el-card v-if="hasHistory" shadow="hover" class="history-player-card">
    <template #header>
      <div class="card-header">
        <span>
          Execution History Player
        </span>
        <el-tag type="info" size="default">{{ historyLength }} steps</el-tag>
      </div>
    </template>
    
    <div class="history-player">
      <!-- 时间轴滑块 -->
      <div class="timeline-section">
        <el-slider
          v-model="currentIndex"
          :min="0"
          :max="maxIndex"
          :marks="timelineMarks"
          :format-tooltip="formatTooltip"
          @change="handleSliderChange"
        />
      </div>
      
      <!-- 当前时间信息 -->
      <div class="time-info">
        <el-tag type="primary" effect="plain" size="default">
          Step: {{ currentIndex + 1 }} / {{ historyLength }}
        </el-tag>
        <el-tag v-if="currentSnapshot" type="success" effect="plain" size="default">
          Time: {{ currentSnapshot.time }}
        </el-tag>
        <el-tag v-if="isPlaying" type="warning" effect="dark" size="default">
          <el-icon class="is-loading"><Loading /></el-icon>
          Playing
        </el-tag>
      </div>
      
      <!-- 控制按钮 -->
      <div class="player-controls">
        <div class="control-buttons">
          <!-- 跳转到开始 -->
          <el-button 
            @click="jumpToStart"
            :disabled="currentIndex === 0"
            size="default"
            circle
          >
          <el-icon><DArrowLeft /></el-icon>
          </el-button>
          
          <!-- 上一步 -->
          <el-button 
            @click="handlePrevStep"
            :disabled="currentIndex === 0"
            size="default"
          >
          <el-icon style="margin-right: 5px"><ArrowLeft /></el-icon>
            Previous
          </el-button>
          
          <!-- 播放/暂停 -->
          <el-button 
            @click="handlePlayPause"
            :type="isPlaying ? 'warning' : 'primary'"
            size="default"
          >
            <el-icon style="margin-right: 5px">
              <VideoPause v-if="isPlaying" />
              <VideoPlay v-else />
            </el-icon>
            {{ isPlaying ? 'Pause' : 'Play' }}
          </el-button>
          
          <!-- 下一步 -->
          <el-button 
            @click="handleNextStep"
            :disabled="currentIndex === maxIndex"
            size="default"
          >
            Next
            <el-icon style="margin-left: 5px"><ArrowRight /></el-icon>
          </el-button>
          
          <!-- 跳转到结束 -->
          <el-button 
            @click="jumpToEnd"
            :disabled="currentIndex === maxIndex"
            size="default"
            circle
          >
            <el-icon><DArrowRight /></el-icon>
          </el-button>
        </div>
        
        <div class="control-options">
          <!-- 播放速度选择 -->
          <el-select 
            v-model="playSpeed" 
            placeholder="Speed"
            size="default"
            style="width: 90px"
          >
            <el-option label="0.25x" :value="2000" />
            <el-option label="0.5x" :value="1000" />
            <el-option label="1x" :value="500" />
            <el-option label="2x" :value="250" />
            <el-option label="4x" :value="125" />
          </el-select>
          
          <!-- 跳转到最新 -->
          <el-button 
            @click="jumpToEnd"
            type="info"
            size="default"
            :disabled="currentIndex === maxIndex"
          >
            Latest
          </el-button>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { 
  Clock, 
  VideoPlay, 
  VideoPause, 
  ArrowLeft, 
  ArrowRight,
  DArrowLeft,
  DArrowRight,
  Loading
} from '@element-plus/icons-vue'

// Props
const props = defineProps({
  history: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['step-change'])

// 状态
const currentIndex = ref(0)
const isPlaying = ref(false)
const playSpeed = ref(500) // 默认 1x 速度
const playTimer = ref(null)

// 计算属性
const hasHistory = computed(() => props.history.length > 0)
const historyLength = computed(() => props.history.length)
const maxIndex = computed(() => Math.max(0, props.history.length - 1))
const currentSnapshot = computed(() => props.history[currentIndex.value])

const timelineMarks = computed(() => {
  if (props.history.length === 0) return {}
  
  return {
    0: 'Start',
    [maxIndex.value]: 'End'
  }
})

// Tooltip 格式化
const formatTooltip = (val) => {
  const snapshot = props.history[val]
  return snapshot ? `Step ${val + 1} (Time: ${snapshot.time})` : ''
}

// 显示指定步骤
const showStep = (index) => {
  if (index >= 0 && index <= maxIndex.value) {
    currentIndex.value = index
    const snapshot = props.history[index]
    if (snapshot) {
      emit('step-change', snapshot.world)
    }
  }
}

// 控制函数
const handlePrevStep = () => {
  stopAutoPlay()
  if (currentIndex.value > 0) {
    showStep(currentIndex.value - 1)
  }
}

const handleNextStep = () => {
  stopAutoPlay()
  if (currentIndex.value < maxIndex.value) {
    showStep(currentIndex.value + 1)
  }
}

const handlePlayPause = () => {
  if (isPlaying.value) {
    stopAutoPlay()
  } else {
    startAutoPlay()
  }
}

const handleSliderChange = (value) => {
  stopAutoPlay()
  showStep(value)
}

const jumpToStart = () => {
  stopAutoPlay()
  showStep(0)
}

const jumpToEnd = () => {
  stopAutoPlay()
  showStep(maxIndex.value)
}

// 自动播放
const startAutoPlay = () => {
  if (props.history.length === 0) return
  
  // 如果已经在最后一步,从头开始
  if (currentIndex.value === maxIndex.value) {
    currentIndex.value = 0
  }
  
  isPlaying.value = true
  playTimer.value = setInterval(() => {
    if (currentIndex.value < maxIndex.value) {
      showStep(currentIndex.value + 1)
    } else {
      stopAutoPlay() // 播放完毕
    }
  }, playSpeed.value)
}

const stopAutoPlay = () => {
  isPlaying.value = false
  if (playTimer.value) {
    clearInterval(playTimer.value)
    playTimer.value = null
  }
}

// 监听播放速度变化
watch(playSpeed, (newSpeed) => {
  if (isPlaying.value) {
    stopAutoPlay()
    startAutoPlay() // 用新速度重新开始
  }
})

// 监听历史数据变化
watch(() => props.history, (newHistory) => {
  if (newHistory.length > 0) {
    // 新历史加载时,停止播放并跳转到最后一步
    stopAutoPlay()
    showStep(newHistory.length - 1)  // 改为跳转到最后一步
  }
}, { immediate: true })

// 组件卸载时清理定时器
onUnmounted(() => {
  stopAutoPlay()
})
</script>

<style scoped>
/* 与 ActionForm 保持一致的卡片样式 */
.history-player-card {
  width: 100%;
  height: 19.3em;
}

.history-player-card :deep(.el-card__header) {
  padding: 12px 20px;
}

.history-player-card :deep(.el-card__body) {
  padding: 10px 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

.history-player {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.timeline-section {
  margin-bottom: 12px;
  padding: 0 5px;
}

.time-info {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 16px;
  margin-bottom: 12px;
  padding: 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.player-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.control-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
  flex: 1;
}

.control-options {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .control-buttons {
    flex-wrap: wrap;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .player-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .control-buttons,
  .control-options {
    justify-content: center;
    width: 100%;
  }
}
</style>