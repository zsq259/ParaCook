<template>
  <el-dialog
    v-model="visible"
    title="📖 Help & Instructions"
    width="800px"
    :close-on-click-modal="false"
  >
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 快速开始 -->
      <el-tab-pane label="🚀 Quick Start" name="quickstart">
        <div class="help-content">
          <h3>How to Use ParaCook Testing GUI</h3>
          <el-steps direction="vertical" :active="5">
            <el-step title="Step 1: Check Connection">
              <template #description>
                <p>Ensure the WebSocket shows <el-tag type="success" size="small">🟢 Connected</el-tag> in the header.</p>
                <p>If disconnected, start the backend server first.</p>
              </template>
            </el-step>
            
            <el-step title="Step 2: View Current State">
              <template #description>
                <p><strong>Map Viewer:</strong> See the kitchen layout, agents, and items</p>
                <p><strong>Config Info:</strong> Check recipes and orders that need completion</p>
              </template>
            </el-step>
            
            <el-step title="Step 3: Plan Actions">
              <template #description>
                <p>Use <strong>Action Form</strong> or <strong>Action Editor</strong> to create action sequences:</p>
                <ul>
                  <li><strong>Action Form:</strong> User-friendly form interface</li>
                  <li><strong>Action Editor:</strong> Direct JSON editing for advanced users</li>
                </ul>
              </template>
            </el-step>
            
            <el-step title="Step 4: Execute">
              <template #description>
                <p>Click <el-tag type="success">Execute Action Plan</el-tag> button</p>
                <p>Monitor execution through:</p>
                <ul>
                  <li><strong>Map Viewer:</strong> Visual updates</li>
                  <li><strong>Log Viewer:</strong> Detailed execution logs</li>
                </ul>
              </template>
            </el-step>
            
            <el-step title="Step 5: Review & Iterate">
              <template #description>
                <p>Use <strong>History Player</strong> to replay and analyze execution</p>
                <p>Adjust actions and re-execute until all orders complete</p>
                <p>Success indicated by: <el-tag type="success" effect="dark">✅ All Orders Completed!</el-tag></p>
              </template>
            </el-step>
          </el-steps>
        </div>
      </el-tab-pane>

      <!-- 游戏规则 -->
      <el-tab-pane label="🎮 Game Rules" name="rules">
        <div class="help-content">
          <h3>ParaCook - Multi-Agent Cooking Simulation</h3>
          
          <el-alert
            title="Core Objective"
            type="success"
            :closable="false"
            style="margin-bottom: 20px;"
          >
            Complete all dish orders by coordinating multiple agents to acquire ingredients, process them, assemble dishes, and serve them in the correct order.
          </el-alert>

          <h4>🎯 Three Core Principles</h4>
          <ol>
            <li><strong>Maximize Efficiency:</strong> Minimize total time to complete all orders</li>
            <li><strong>Maximize Parallelism:</strong> Multiple agents should work simultaneously to reduce idle time</li>
            <li><strong>Ensure Accuracy:</strong> Follow all action definitions and environment constraints strictly</li>
          </ol>

          <h4>🤖 Agent Rules</h4>
          <ul>
            <li><strong>No Collision:</strong> Agents can overlap positions and paths freely</li>
            <li><strong>Single Item Hold:</strong> Each agent can hold only ONE item at a time (ingredient, pot, pan, or plate)</li>
            <li><strong>Positioning:</strong> Agents can only stand on empty floor tiles, never on station tiles</li>
            <li><strong>Adjacent Interaction:</strong> Agents can only interact with stations that are adjacent in four cardinal directions (up/down/left/right)</li>
          </ul>

          <h4>🏪 Environment & Station Rules</h4>
          <el-collapse style="margin-top: 10px;">
            <el-collapse-item title="Ingredient Dispensers" name="dispenser">
              <ul>
                <li>Each dispenser provides one specific type of ingredient</li>
                <li>Ingredients can only be taken when empty-handed</li>
                <li>All ingredients can be held directly without containers</li>
              </ul>
            </el-collapse-item>
            
            <el-collapse-item title="Stoves & Cooking" name="stove">
              <ul>
                <li>Stoves can only hold cookware (pots/pans), not ingredients directly</li>
                <li>Cooking starts automatically when cookware with ingredients is placed on a stove</li>
                <li>Picking up cookware pauses cooking; placing it back on any stove resumes it</li>
                <li>Cooked food must remain in its container; cannot be picked up by hand</li>
              </ul>
            </el-collapse-item>
            
            <el-collapse-item title="Cutting Boards & Processing" name="cutting">
              <ul>
                <li>Fixed stations (cutting boards, sinks) can only be used by one agent at a time</li>
                <li>Use Process action to chop ingredients on cutting boards</li>
              </ul>
            </el-collapse-item>
            
            <el-collapse-item title="Plates & Serving" name="serving">
              <ul>
                <li>All food items must be placed on a plate before serving</li>
                <li>Order of ingredients on plate doesn't matter</li>
                <li>Dishes must be served in the exact order specified in Orders list</li>
                <li>Ingredients already on a plate cannot be removed (only added to another plate or discarded)</li>
              </ul>
            </el-collapse-item>
            
            <el-collapse-item title="Dirty Plates & Washing" name="plates">
              <ul>
                <li>Dirty plates return to the return station automatically after serving</li>
                <li>Dirty plates cannot hold items and must be washed at a sink</li>
                <li>Pick up dirty plates from return station when empty-handed</li>
                <li>Process dirty plates at sink to get clean plates</li>
              </ul>
            </el-collapse-item>
          </el-collapse>

          <h4>⚡ Available Actions</h4>
          <el-table :data="actionTypes" border style="width: 100%; margin-top: 10px;">
            <el-table-column prop="action" label="Action" width="100">
              <template #default="{ row }">
                <el-tag :type="row.color">{{ row.action }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="params" label="Parameters" width="150" />
            <el-table-column prop="description" label="Description" />
          </el-table>

          <h4>✅ Task Completion</h4>
          <p>The simulation is complete when all dish orders are fulfilled in the correct sequence. Success is indicated by a <el-tag type="success" effect="dark">✅ All Orders Completed!</el-tag> badge in the header.</p>
        </div>
      </el-tab-pane>

      <!-- 界面说明 -->
      <el-tab-pane label="🖥️ UI Guide" name="ui">
        <div class="help-content">
          <h3>User Interface Components</h3>
          
          <el-collapse accordion>
            <el-collapse-item title="📍 Map Viewer (Top Left)" name="1">
              <p><strong>Purpose:</strong> Visualizes the kitchen environment in real-time</p>
              <p><strong>Features:</strong></p>
              <ul>
                <li>Grid-based layout with coordinate axes (X and Y)</li>
                <li>Agents displayed as colored circles with images</li>
                <li>Shows kitchen equipment, ingredients, and dishes</li>
                <li>Hover over cells to see detailed information</li>
                <li>Live status indicator (green when connected)</li>
                <li>Manual refresh button to reload map data</li>
              </ul>
            </el-collapse-item>

            <el-collapse-item title="⚙️ Config Info (Top Right)" name="2">
              <p><strong>Purpose:</strong> Displays current test recipes and orders</p>
              <p><strong>Shows:</strong></p>
              <ul>
                <li><strong>Recipes:</strong> List of available recipes (green tags)</li>
                <li><strong>Orders:</strong> Current dish orders to complete (orange tags)</li>
                <li>Number count for both recipes and orders</li>
                <li>Live WebSocket connection status</li>
              </ul>
              <p><strong>Note:</strong> This is what agents need to complete to finish the task.</p>
            </el-collapse-item>

            <el-collapse-item title="✏️ Action Editor (Middle Left)" name="3">
              <p><strong>Purpose:</strong> Edit action plans in JSON format</p>
              <p><strong>Features:</strong></p>
              <ul>
                <li>Direct JSON editing in textarea</li>
                <li>"Format JSON" button to prettify JSON structure</li>
                <li>Auto-saves changes to backend when you click outside the editor</li>
                <li>Shows validation errors if JSON is invalid</li>
                <li>Expandable preview by agent with action counts</li>
                <li>Remove individual actions from preview</li>
              </ul>
              <p><strong>Format:</strong> <code>{ "agent_name": [action1, action2, ...] }</code></p>
            </el-collapse-item>

            <el-collapse-item title="➕ Action Form (Top Right)" name="4">
              <p><strong>Purpose:</strong> Add new actions via form interface</p>
              <p><strong>Usage:</strong></p>
              <ol>
                <li>Select target agent from dropdown</li>
                <li>Choose action type (MoveTo, Wait, Interact, Process, Finish)</li>
                <li>Fill in required parameters:
                  <ul>
                    <li><strong>MoveTo:</strong> X and Y coordinates</li>
                    <li><strong>Wait:</strong> Duration (number of steps)</li>
                    <li><strong>Interact/Process:</strong> Target object name</li>
                    <li><strong>Finish:</strong> No parameters needed</li>
                  </ul>
                </li>
                <li>Click "Add Action" button</li>
              </ol>
              <p><strong>Note:</strong> Form is disabled after task completion.</p>
            </el-collapse-item>

            <el-collapse-item title="📜 Log Viewer (Bottom Left)" name="5">
              <p><strong>Purpose:</strong> Real-time execution logs</p>
              <p><strong>Features:</strong></p>
              <ul>
                <li>Timestamped log entries with severity levels</li>
                <li>Color-coded messages (INFO, WARNING, ERROR, etc.)</li>
                <li>Supports ANSI color codes from backend</li>
                <li>Auto-scrolls to latest entry</li>
                <li>"Copy" button to copy all logs to clipboard</li>
                <li>"Clear" button to remove all log entries</li>
                <li>Shows total entry count in header</li>
              </ul>
            </el-collapse-item>

            <el-collapse-item title="⏯️ History Player (Bottom Right)" name="6">
              <p><strong>Purpose:</strong> Replay execution history step by step</p>
              <p><strong>Features:</strong></p>
              <ul>
                <li>Timeline slider to navigate through steps</li>
                <li>Play/Pause controls for automatic playback</li>
                <li>Adjustable playback speed (0.5x to 2x)</li>
                <li>Previous/Next step buttons</li>
                <li>Jump to start/end buttons</li>
                <li>Loop mode for continuous replay</li>
                <li>Shows current step number and timestamp</li>
                <li>Updates Map Viewer to show historical states</li>
              </ul>
              <p><strong>Note:</strong> Only appears after executing an action plan.</p>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-tab-pane>

      <!-- 故障排除 -->
      <el-tab-pane label="🔧 Troubleshooting" name="troubleshooting">
        <div class="help-content">
          <h3>Common Issues & Solutions</h3>
          
          <el-collapse>
            <el-collapse-item title="🔴 WebSocket Disconnected" name="1">
              <el-alert type="warning" :closable="false" style="margin-bottom: 10px;">
                Check the connection status indicator in the header - it should show green "🟢 Connected"
              </el-alert>
              <p><strong>Solutions:</strong></p>
              <ol>
                <li>Ensure the backend server is running (check terminal)</li>
                <li>Verify the WebSocket URL matches your server (default: ws://localhost:8765)</li>
                <li>Refresh the page to attempt reconnection</li>
                <li>Check browser console (F12) for connection errors</li>
              </ol>
            </el-collapse-item>
            
            <el-collapse-item title="⚠️ Actions Not Executing" name="2">
              <p><strong>Common causes:</strong></p>
              <ul>
                <li>WebSocket is not connected (check green indicator)</li>
                <li>Action format is invalid (check Action Editor for JSON errors)</li>
                <li>Action violates game rules (e.g., agent not adjacent to target station)</li>
                <li>Task has already been completed</li>
              </ul>
              <p><strong>Solutions:</strong></p>
              <ol>
                <li>Review Log Viewer for specific error messages</li>
                <li>Verify actions follow all environment constraints (see Game Rules tab)</li>
                <li>Use Action Form instead of JSON editor to avoid format errors</li>
                <li>Check that agent positions are on empty floor tiles adjacent to target stations</li>
              </ol>
            </el-collapse-item>
            
            <el-collapse-item title="🗺️ Map Not Updating" name="3">
              <p><strong>Possible causes:</strong></p>
              <ul>
                <li>WebSocket connection lost during execution</li>
                <li>Backend stopped sending map_update events</li>
                <li>Browser rendering issue</li>
              </ul>
              <p><strong>Solutions:</strong></p>
              <ol>
                <li>Check WebSocket connection status</li>
                <li>Click the "Refresh" button in Map Viewer header</li>
                <li>Open browser DevTools (F12) and check console for errors</li>
                <li>Click "Clear All States and Refresh" to fully reset</li>
              </ol>
            </el-collapse-item>

            <el-collapse-item title="❌ Invalid Action Error" name="4">
              <p><strong>Common mistakes:</strong></p>
              <ul>
                <li>Agent not adjacent to target station (must be in 4 cardinal directions)</li>
                <li>Agent position overlaps with station tile (agents can only stand on empty floor)</li>
                <li>Trying to Process a stove (cooking is automatic, use Interact instead)</li>
                <li>Holding multiple items (agents can only hold ONE item at a time)</li>
                <li>Trying to pick up ingredient when hands are full</li>
              </ul>
              <p><strong>Solutions:</strong></p>
              <ol>
                <li>Review Game Rules tab for detailed constraints</li>
                <li>Use MoveTo to position agent on empty floor adjacent to target</li>
                <li>Ensure agent is empty-handed before picking up items</li>
                <li>Check Log Viewer for specific error details</li>
              </ol>
            </el-collapse-item>

            <el-collapse-item title="📊 History Player Empty" name="5">
              <p><strong>Reason:</strong> No execution has been performed yet</p>
              <p><strong>Solution:</strong> Add actions and click "Execute Action Plan" first. History Player will appear after execution starts.</p>
            </el-collapse-item>

            <el-collapse-item title="🔒 Cannot Add Actions (Form Disabled)" name="6">
              <p><strong>Reason:</strong> Task has been completed successfully</p>
              <p><strong>Solution:</strong> Click "Clear All States and Refresh" button to start a new simulation</p>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <el-button type="primary" @click="visible = false">Got it!</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'

const visible = defineModel('visible', { type: Boolean, default: false })
const activeTab = ref('quickstart')

// 动作类型表格数据（基于 ActionForm.vue 和 instruction.py 的实际定义）
const actionTypes = [
  { 
    action: 'MoveTo', 
    params: 'target: [x, y]',
    description: 'Move to target empty floor coordinate (adjacent to station). Time cost: distance × 1 unit',
    color: 'primary'
  },
  { 
    action: 'Wait', 
    params: 'duration: number',
    description: 'Remain idle at current position for specified time units',
    color: 'info'
  },
  { 
    action: 'Interact', 
    params: 'target: station_name',
    description: 'Interact with adjacent station: pick up, place down, add ingredients, transfer contents, or serve dishes',
    color: 'success'
  },
  { 
    action: 'Process', 
    params: 'target: station_name',
    description: 'Perform continuous action at station (chop, wash). Cannot be used on stoves (cooking is automatic)',
    color: 'warning'
  },
  { 
    action: 'Finish', 
    params: 'None',
    description: 'Mark agent as completed - no further actions will be taken',
    color: 'danger'
  },
]
</script>

<style scoped>
.help-content {
  padding: 20px;
  max-height: 500px;
  overflow-y: auto;
}

.help-content h3 {
  color: #409eff;
  margin-top: 0;
}

.help-content h4 {
  color: #606266;
  margin-top: 20px;
  margin-bottom: 10px;
}

.help-content ul, .help-content ol {
  line-height: 1.8;
}

.help-content p {
  line-height: 1.6;
  color: #606266;
}

:deep(.el-descriptions__label) {
  width: 150px;
  font-weight: bold;
}
</style>