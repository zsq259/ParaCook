<template>
  <div class="config-panel card">
    <h2>Current Test Configuration</h2>
    
    <div class="config-content">
      <div class="config-item">
        <div class="config-label">
          <i class="icon">📋</i>
          <span>Recipes:</span>
        </div>
        <div class="config-value">
          {{ recipes || 'None' }}
        </div>
      </div>

      <div class="config-item">
        <div class="config-label">
          <i class="icon">📦</i>
          <span>Orders:</span>
        </div>
        <div class="config-value">
          {{ orders || 'None' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfigPanel',
  props: {
    recipes: {
      type: String,
      default: ''
    },
    orders: {
      type: String,
      default: ''
    }
  }
};
</script>

<style scoped>
.config-panel {
  background: #fff;
}

.config-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.config-item {
  padding: 12px;
  background: #f5f5f5;
  border-radius: 5px;
  border-left: 4px solid #4CAF50;
}

.config-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #555;
  margin-bottom: 6px;
}

.config-label .icon {
  font-size: 1.2em;
}

.config-value {
  color: #333;
  padding-left: 28px;
  line-height: 1.5;
}
</style>