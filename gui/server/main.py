from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from collections import deque
from enum import Enum
from datetime import datetime
import json
import asyncio

config_path = "config/gui_config.json"
with open(config_path, 'r') as f:
    config = json.load(f)

API_HOST = config['api']['host']
API_PORT = config['api']['port']

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket 消息类型
class WSMessageType(str, Enum):
    """WebSocket 消息类型"""
    LOG = "log"
    TASK_STATUS = "task_status"
    MAP_UPDATE = "map_update"
    CONFIG_UPDATE = "config_update"
    AGENTS_UPDATE = "agents_update"
    ACTIONS_UPDATE = "actions_update"
    SYSTEM_RESET = "system_reset"
    PING = "ping"
    PONG = "pong"
    CONNECTED = "connected"

# 全局状态
class ServerState:
    def __init__(self):
        self.current_actions: Dict[str, List[Dict[str, Any]]] = {}
        self.world_state: Optional[dict] = None
        self.agents: List[str] = []
        self.recipes: List[str] = []
        self.orders: List[str] = []
        self.logs: deque = deque(maxlen=1000)
        self.should_execute = False
        self.completed = False
        self.should_reset = False

state = ServerState()

# 数据模型
class Action(BaseModel):
    action: str
    target: Optional[Any] = None
    duration: Optional[int] = None

class ActionsData(BaseModel):
    actions: Dict[str, List[Dict[str, Any]]]

class WorldState(BaseModel):
    world: dict
    agents: List[str]
    recipes: List[str]
    orders: List[str]

class LogMessage(BaseModel):
    level: str
    message: str
    timestamp: Optional[str] = None

# WebSocket 连接管理
class ConnectionManager:
    def __init__(self):
        self.connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """接受新的 WebSocket 连接"""
        await websocket.accept()
        self.connections.add(websocket)
        print(f"WebSocket connected. Total connections: {len(self.connections)}")
        
        # 发送初始数据给新连接
        await self.send_initial_data(websocket)

    def disconnect(self, websocket: WebSocket):
        """断开 WebSocket 连接"""
        self.connections.discard(websocket)
        print(f"WebSocket disconnected. Total connections: {len(self.connections)}")

    async def send_initial_data(self, websocket: WebSocket):
        """向新连接发送当前所有状态"""
        try:
            print("="*60)
            print("📤 Sending initial data to new WebSocket client...")
            
            # 1. 发送连接成功消息
            print("  1️⃣ Sending connection confirmation...")
            await websocket.send_json({
                "type": WSMessageType.CONNECTED,
                "data": {
                    "message": "Connected to ParaCook server",
                    "connected": True
                },
                "timestamp": datetime.now().isoformat()
            })
            
            # 2. 发送历史日志
            log_count = len(state.logs)
            print(f"  2️⃣ Sending {log_count} log entries...")
            for log_entry in state.logs:
                await websocket.send_json({
                    "type": WSMessageType.LOG,
                    "data": log_entry,
                    "timestamp": datetime.now().isoformat()
                })
            
            # 3. 发送任务状态
            print(f"  3️⃣ Sending task status (completed={state.completed})...")
            await websocket.send_json({
                "type": WSMessageType.TASK_STATUS,
                "data": {
                    "completed": state.completed,
                    "should_execute": state.should_execute
                },
                "timestamp": datetime.now().isoformat()
            })
            
            # 4. 发送地图数据
            if state.world_state:
                print(f"  4️⃣ Sending world state (tiles={len(state.world_state.get('tiles', []))})...")
                await websocket.send_json({
                    "type": WSMessageType.MAP_UPDATE,
                    "data": state.world_state,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                print(f"  4️⃣ ⚠️ No world state available")
            
            # 5. 发送配置信息
            config_data = self._get_config_data()
            print(f"  5️⃣ Sending config (agents={config_data.get('num_agents')}, recipes={config_data.get('recipes_count')})...")
            await websocket.send_json({
                "type": WSMessageType.CONFIG_UPDATE,
                "data": config_data,
                "timestamp": datetime.now().isoformat()
            })
            
            # 6. 发送 agent 列表
            print(f"  6️⃣ Sending agents: {state.agents}")
            await websocket.send_json({
                "type": WSMessageType.AGENTS_UPDATE,
                "data": state.agents,
                "timestamp": datetime.now().isoformat()
            })
            
            # 7. 发送当前动作
            if state.current_actions:
                action_count = sum(len(acts) for acts in state.current_actions.values())
                print(f"  7️⃣ Sending actions ({action_count} total actions for {len(state.current_actions)} agents)...")
                await websocket.send_json({
                    "type": WSMessageType.ACTIONS_UPDATE,
                    "data": {"actions": state.current_actions},
                    "timestamp": datetime.now().isoformat()
                })
            else:
                print(f"  7️⃣ No actions to send")
            
            print("✅ Initial data sent successfully!")
            print(f"   Summary:")
            print(f"   - Logs: {log_count}")
            print(f"   - Agents: {state.agents}")
            print(f"   - Recipes: {state.recipes}")
            print(f"   - Orders: {state.orders}")
            print(f"   - Task completed: {state.completed}")
            print("="*60)
            
        except Exception as e:
            print(f"❌ Error sending initial data: {e}")
            import traceback
            traceback.print_exc()

    def _get_config_data(self) -> dict:
        """获取配置数据"""
        return {
            "num_agents": len(state.agents),
            "world_steps": len(state.logs),
            "actions_count": sum(len(acts) for acts in state.current_actions.values()),
            "status": "completed" if state.completed else "running",
            "recipes_count": len(state.recipes),
            "orders_count": len(state.orders),
            "recipes": state.recipes,
            "orders": state.orders
        }

    async def broadcast(self, message_type: WSMessageType, data: Any):
        """广播消息到所有连接"""
        if not self.connections:
            return
            
        message = {
            "type": message_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        disconnected = set()
        for ws in self.connections:
            try:
                await ws.send_json(message)
            except WebSocketDisconnect:
                disconnected.add(ws)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                disconnected.add(ws)
        
        # 移除断开的连接
        self.connections.difference_update(disconnected)
        
        if disconnected:
            print(f"Removed {len(disconnected)} disconnected clients")

    async def add_log(self, log_entry: dict):
        """添加日志并广播"""
        state.logs.append(log_entry)
        await self.broadcast(WSMessageType.LOG, log_entry)

manager = ConnectionManager()

# ============= API 路由 =============

@app.get("/")
async def root():
    return {
        "message": "ParaCook Human Agent API Server",
        "version": "1.0.0",
        "status": "running",
        "websocket_connections": len(manager.connections)
    }

@app.get("/api/actions")
async def get_actions():
    """获取当前的动作列表"""
    return {"success": True, "data": state.current_actions}

@app.post("/api/actions")
async def save_actions(data: ActionsData):
    """保存动作列表"""
    state.current_actions = data.actions
    
    # 广播动作更新
    await manager.broadcast(
        WSMessageType.ACTIONS_UPDATE,
        {"actions": state.current_actions}
    )
    
    # 广播配置更新（因为动作数量变了）
    config_data = manager._get_config_data()
    await manager.broadcast(
        WSMessageType.CONFIG_UPDATE,
        config_data
    )
    
    return {"success": True, "message": "Actions saved"}

@app.post("/api/actions/add")
async def add_action(agent: str, action: Action):
    """为指定 agent 添加一个动作"""
    if agent not in state.current_actions:
        state.current_actions[agent] = []
    
    action_dict = action.model_dump(exclude_none=True)
    state.current_actions[agent].append(action_dict)
    
    # 广播动作更新
    await manager.broadcast(
        WSMessageType.ACTIONS_UPDATE,
        {"actions": state.current_actions}
    )
    
    # 广播配置更新
    config_data = manager._get_config_data()
    await manager.broadcast(
        WSMessageType.CONFIG_UPDATE,
        config_data
    )
    
    return {
        "success": True, 
        "message": f"Action added to {agent}",
        "data": state.current_actions
    }

@app.delete("/api/actions/{agent}/{index}")
async def remove_action(agent: str, index: int):
    """删除指定动作"""
    if agent not in state.current_actions:
        raise HTTPException(status_code=404, detail=f"Agent {agent} not found")
    
    if index < 0 or index >= len(state.current_actions[agent]):
        raise HTTPException(status_code=404, detail=f"Invalid index {index}")
    
    state.current_actions[agent].pop(index)
    
    if len(state.current_actions[agent]) == 0:
        del state.current_actions[agent]
    
    # 广播动作更新
    await manager.broadcast(
        WSMessageType.ACTIONS_UPDATE,
        {"actions": state.current_actions}
    )
    
    # 广播配置更新
    config_data = manager._get_config_data()
    await manager.broadcast(
        WSMessageType.CONFIG_UPDATE,
        config_data
    )
    
    return {"success": True, "data": state.current_actions}

@app.delete("/api/actions")
async def clear_actions():
    """清空所有动作"""
    state.current_actions = {}
    
    # 广播动作更新
    await manager.broadcast(
        WSMessageType.ACTIONS_UPDATE,
        {"actions": {}}
    )
    
    # 广播配置更新
    config_data = manager._get_config_data()
    await manager.broadcast(
        WSMessageType.CONFIG_UPDATE,
        config_data
    )
    
    return {"success": True, "message": "All actions cleared"}

@app.post("/api/actions/execute")
async def execute_actions():
    """触发执行动作计划"""
    if not state.current_actions:
        return {"success": False, "message": "No actions to execute"}
    
    state.should_execute = True
    
    # 广播执行状态
    await manager.broadcast(
        WSMessageType.TASK_STATUS,
        {
            "completed": state.completed,
            "should_execute": state.should_execute,
            "executing": True
        }
    )
    
    return {"success": True, "message": "Execution triggered"}

@app.get("/api/actions/should_execute")
async def should_execute():
    """检查是否应该执行（供 Human.py 轮询）"""
    if state.should_execute:
        state.should_execute = False  # 重置标志
        return {
            "success": True, 
            "should_execute": True,
            "data": state.current_actions
        }
    return {"success": True, "should_execute": False}

@app.get("/api/world")
async def get_world():
    """获取当前世界状态（前端调用）"""
    if state.world_state:
        return {
            "success": True,
            "data": {
                "world": state.world_state,
                "agents": state.agents,
                "recipes": state.recipes,
                "orders": state.orders
            }
        }
    return {"success": False, "message": "World state not ready"}

@app.post("/api/world/update")
async def update_world(data: WorldState):
    """更新世界状态（由 Human.py 调用）"""
    try:
        print(f"Received world update: agents={data.agents}, orders count={len(data.orders)}")
        state.world_state = data.world
        state.agents = data.agents
        state.recipes = data.recipes
        state.orders = data.orders
        
        # 广播地图更新
        await manager.broadcast(
            WSMessageType.MAP_UPDATE,
            data.world
        )
        
        # 广播 agent 列表更新
        await manager.broadcast(
            WSMessageType.AGENTS_UPDATE,
            state.agents
        )
        
        # 广播配置更新
        config_data = manager._get_config_data()
        await manager.broadcast(
            WSMessageType.CONFIG_UPDATE,
            config_data
        )
        
        return {"success": True, "message": "World state updated"}
    except Exception as e:
        print(f"Error updating world: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents")
async def get_agents():
    """获取 agent 列表"""
    return {"success": True, "data": state.agents}

@app.get("/api/recipes")
async def get_recipes():
    """获取配方列表"""
    return {"success": True, "data": state.recipes}

@app.get("/api/orders")
async def get_orders():
    """获取订单列表"""
    return {"success": True, "data": state.orders}

@app.get("/api/logs")
async def get_logs(limit: int = 100):
    """获取日志"""
    logs = list(state.logs)[-limit:]
    return {"success": True, "data": logs}

@app.post("/api/logs")
async def add_log(log: LogMessage):
    """添加日志（由 Human.py 调用）"""
    log_entry = log.model_dump()
    await manager.add_log(log_entry)
    return {"success": True}

@app.delete("/api/logs")
async def clear_logs():
    """清空日志"""
    state.logs.clear()
    
    # 广播日志清空
    await manager.broadcast(
        WSMessageType.LOG,
        {"type": "clear"}
    )
    
    return {"success": True, "message": "Logs cleared"}

@app.get("/api/logs/history")
async def get_log_history():
    """获取历史日志"""
    return {
        "success": True,
        "data": list(state.logs)
    }

@app.post("/api/task/complete")
async def mark_task_complete():
    """标记任务完成（由 Human.py 调用）"""
    state.completed = True
    
    # 广播任务完成
    await manager.broadcast(
        WSMessageType.TASK_STATUS,
        {
            "completed": True,
            "message": "All orders completed successfully!"
        }
    )
    
    # 广播配置更新
    config_data = manager._get_config_data()
    await manager.broadcast(
        WSMessageType.CONFIG_UPDATE,
        config_data
    )
    
    return {"success": True}

@app.get("/api/task/status")
async def get_task_status():
    """获取任务状态"""
    return {
        "success": True,
        "completed": state.completed
    }

@app.post("/api/task/reset")
async def reset_task():
    """重置任务状态"""
    state.completed = False
    
    # 广播任务状态更新
    await manager.broadcast(
        WSMessageType.TASK_STATUS,
        {"completed": False}
    )
    
    return {"success": True}

@app.post("/api/reset")
async def reset_all():
    """重置所有状态到初始状态"""
    try:
        state.should_reset = True
        
        # 清空所有状态
        state.should_execute = False
        state.world_state = None
        state.logs.clear()
        state.completed = False
        state.current_actions = {}
        
        # 广播系统重置
        await manager.broadcast(
            WSMessageType.SYSTEM_RESET,
            {
                "message": "System has been reset to initial state",
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # 广播日志清空
        await manager.broadcast(
            WSMessageType.LOG,
            {"type": "clear"}
        )
        
        # 广播任务状态重置
        await manager.broadcast(
            WSMessageType.TASK_STATUS,
            {"completed": False, "reset": True}
        )
        
        # 广播配置更新
        config_data = manager._get_config_data()
        await manager.broadcast(
            WSMessageType.CONFIG_UPDATE,
            config_data
        )
        
        return {"success": True, "message": "Reset signal sent"}
    except Exception as e:
        print(f"Error in reset_all: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/should_reset")
async def should_reset():
    """检查是否应该重置"""
    return {
        "success": True,
        "should_reset": state.should_reset
    }

@app.post("/api/reset/confirm")
async def confirm_reset():
    """确认重置完成"""
    state.should_reset = False
    return {"success": True}

@app.get("/api/config")
async def get_config_info():
    """获取配置信息"""
    config_data = manager._get_config_data()
    return {"success": True, "data": config_data}

# 统一的 WebSocket 端点
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)  # 这里面已经调用了 send_initial_data
    
    try:
        while True:
            # 保持连接并处理 ping
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    print(f"Starting FastAPI server on http://{API_HOST}:{API_PORT}")
    print(f"WebSocket endpoint: ws://{API_HOST}:{API_PORT}/ws")
    uvicorn.run(app, host=API_HOST, port=API_PORT)