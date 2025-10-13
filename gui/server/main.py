from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from collections import deque
import json
import asyncio

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        self.active_connections: List[WebSocket] = []
        self.log_connections: set = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def connect_log(self, websocket: WebSocket):
        await websocket.accept()
        self.log_connections.add(websocket)

    def disconnect_log(self, websocket: WebSocket):
        self.log_connections.discard(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

    async def broadcast_log(self, log_entry: dict):
        disconnected = set()
        for ws in self.log_connections:
            try:
                await ws.send_json(log_entry)
            except:
                disconnected.add(ws)
        self.log_connections.difference_update(disconnected)

manager = ConnectionManager()

# ============= API 路由 =============

@app.get("/")
async def root():
    return {
        "message": "ParaCook Human Agent API Server",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/actions")
async def get_actions():
    """获取当前的动作列表"""
    return {"success": True, "data": state.current_actions}

@app.post("/api/actions")
async def save_actions(data: ActionsData):
    """保存动作列表"""
    state.current_actions = data.actions
    await manager.broadcast({
        "type": "actions_updated",
        "data": state.current_actions
    })
    return {"success": True, "message": "Actions saved"}

@app.post("/api/actions/add")
async def add_action(agent: str, action: Action):
    """为指定 agent 添加一个动作"""
    if agent not in state.current_actions:
        state.current_actions[agent] = []
    
    action_dict = action.model_dump(exclude_none=True)
    state.current_actions[agent].append(action_dict)
    
    await manager.broadcast({
        "type": "action_added",
        "agent": agent,
        "action": action_dict
    })
    
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
    
    await manager.broadcast({
        "type": "action_removed",
        "agent": agent,
        "index": index
    })
    
    return {"success": True, "data": state.current_actions}

@app.delete("/api/actions")
async def clear_actions():
    """清空所有动作"""
    state.current_actions = {}
    await manager.broadcast({"type": "actions_cleared"})
    return {"success": True, "message": "All actions cleared"}

@app.post("/api/actions/execute")
async def execute_actions():
    """触发执行动作计划"""
    if not state.current_actions:
        return {"success": False, "message": "No actions to execute"}
    
    state.should_execute = True
    await manager.broadcast({
        "type": "execute_triggered",
        "data": state.current_actions
    })
    
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
        state.world_state = data.world  # 这里应该包含完整的地图数据
        state.agents = data.agents
        state.recipes = data.recipes
        state.orders = data.orders
        
        # 广播世界状态更新
        await manager.broadcast({
            "type": "world_updated",
            "data": data.world
        })
        
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
    state.logs.append(log_entry)
    
    # 【修改】通过 WebSocket 广播日志，而不是普通广播
    await manager.broadcast_log(log_entry)
    
    return {"success": True}

@app.delete("/api/logs")
async def clear_logs():
    """清空日志"""
    state.logs.clear()
    # 【修改】通知所有日志客户端清空
    await manager.broadcast_log({"type": "clear"})
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
    await manager.broadcast({
        "type": "task_completed",
        "message": "All orders completed successfully!"
    })
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
        
        # 广播重置消息
        await manager.broadcast_log({"type": "clear"})

        await manager.broadcast({
            "type": "system_reset",
            "message": "System has been reset to initial state"
        })
        
        return {"success": True, "message": "Reset signal sent"}
    except Exception as e:
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

# 日志专用 WebSocket 端点
@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket 端点用于实时日志推送"""
    await manager.connect_log(websocket)
    
    try:
        # 首先发送缓冲区中的历史日志
        for log_entry in state.logs:
            await websocket.send_json(log_entry)
        
        # 保持连接，接收心跳
        while True:
            try:
                # 接收心跳消息(避免连接超时)
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                # 发送 ping 保持连接
                await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        manager.disconnect_log(websocket)

# WebSocket 端点
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 连接，用于实时推送"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server on http://0.0.0.0:5000")
    uvicorn.run(app, host="0.0.0.0", port=5000)