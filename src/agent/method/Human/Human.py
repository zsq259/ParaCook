from src.agent.model.model import Model
from src.agent.method.agent import Agent
from src.game.const import *
from src.game.world_state import World
from src.game.simulator import Simulator
from src.utils.logger_config import logger, COLOR_CODES, RESET

import json
from copy import deepcopy
import subprocess
import sys
import os
import time
import requests
from typing import Optional
import threading
import logging
import asyncio
import websockets
from concurrent.futures import ThreadPoolExecutor

config_path = "config/gui_config.json"
with open(config_path, 'r') as f:
    config = json.load(f)

API_URL = f"http://{config['api']['host']}:{config['api']['port']}"
WEB_URL = f"http://{config['web']['host']}:{config['web']['port']}"
WS_URL = f"ws://{config['api']['host']}:{config['api']['port']}/ws/agent"

class HumanAgent(Agent):
    def __init__(self, model: Model, api_url: str = API_URL):
        super().__init__(model)
        self.api_url = api_url
        self.ws_url = WS_URL
        self.session = requests.Session()
        self.log_handler = None
        self.should_stop_logging = False
        
        # WebSocket 事件标志
        self.execute_event = threading.Event()
        self.reset_event = threading.Event()
        self.current_actions = {}
        self.ws_thread = None
        self.ws_running = False
        
    def _call_api(self, method: str, endpoint: str, data: dict = {}, retries: int = 3) -> Optional[dict]:
        """调用 API 的辅助方法"""
        url = f"{self.api_url}{endpoint}"
        for attempt in range(retries):
            try:
                if method == "GET":
                    response = self.session.get(url, timeout=5)
                elif method == "POST":
                    response = self.session.post(url, json=data, timeout=5)
                elif method == "DELETE":
                    response = self.session.delete(url, timeout=5)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == retries - 1:
                    logger.error(f"API call failed after {retries} attempts: {e}")
                    return None
                time.sleep(0.5)
        
        return None
    
    def update_world_state(self, simulator: Simulator):
        """更新服务器上的世界状态"""
        world = simulator.world
        data = {
            "world": world.to_json(),
            "agents": list(world.agents.keys()),
            "recipes": [recipe["recipe"] for recipe in world.recipes] if world.recipes else [],
            "orders": world.orders
        }
        result = self._call_api("POST", "/api/world/update", data)
        if result and result.get("success"):
            pass
        else:
            logger.warning("Failed to update world state on server")
    
    def get_actions(self) -> Optional[dict]:
        """从服务器获取当前动作列表"""
        result = self._call_api("GET", "/api/actions")
        if result and result.get("success"):
            return result.get("data", {})
        return None
    
    def send_log(self, level: str, message: str):
        """发送日志到服务器（保留原始 ANSI 颜色代码）"""
        data = {
            "level": level,
            "message": message,
            "timestamp": time.strftime("%H:%M:%S")
        }
        self._call_api("POST", "/api/logs", data)
    
    def clear_logs(self):
        """清空服务器日志"""
        self._call_api("DELETE", "/api/logs")
    
    def start_log_forwarding(self):
        """启动日志转发线程"""
        class LogForwarder(logging.Handler):
            def __init__(self, human_agent):
                super().__init__()
                self.human_agent = human_agent
                
            def emit(self, record):
                try:
                    level = record.levelname
                    message = self.format(record)
                    self.human_agent.send_log(level, message)
                except:
                    pass
        
        # 创建并保存 handler 引用
        self.log_handler = LogForwarder(self)
        self.log_handler.setLevel(logging.DEBUG)
        
        # 使用与文件日志相同的格式
        formatter = logging.Formatter('%(message)s')
        self.log_handler.setFormatter(formatter)
        
        # 添加到 logger
        logger.addHandler(self.log_handler)
        logger.info("Log forwarding started")
    
    def stop_log_forwarding(self):
        """停止日志转发"""
        if self.log_handler:
            logger.removeHandler(self.log_handler)
            self.log_handler = None

    def wait_for_server(self, timeout: int = 30) -> bool:
        """等待 API 服务器启动"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.api_url}/", timeout=2)
                if response.status_code == 200:
                    logger.info(f"API server is ready at {self.api_url}")
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        logger.error(f"API server did not start within {timeout} seconds")
        return False
    
    def _run_websocket_loop(self):
        """在独立线程中运行 WebSocket 连接"""
        async def connect_and_listen():
            retry_count = 0
            max_retries = 5
            
            while self.ws_running and retry_count < max_retries:
                try:
                    logger.info(f"Connecting to WebSocket: {self.ws_url}")
                    async with websockets.connect(self.ws_url) as websocket:
                        logger.info("✅ WebSocket connected to agent endpoint")
                        retry_count = 0  # 重置重试计数
                        
                        # 持续接收消息
                        async for message in websocket:
                            if not self.ws_running:
                                break
                                
                            try:
                                data = json.loads(message)
                                msg_type = data.get('type')
                                
                                if msg_type == 'execute':
                                    logger.info("📨 Received execute command via WebSocket")
                                    self.current_actions = data.get('data', {})
                                    self.execute_event.set()
                                    
                                elif msg_type == 'reset':
                                    logger.info("📨 Received reset command via WebSocket")
                                    self.reset_event.set()
                                    
                            except json.JSONDecodeError as e:
                                logger.error(f"Failed to parse WebSocket message: {e}")
                                
                except websockets.exceptions.WebSocketException as e:
                    if self.ws_running:
                        retry_count += 1
                        logger.warning(f"WebSocket connection lost, retrying ({retry_count}/{max_retries})...")
                        await asyncio.sleep(2)
                except Exception as e:
                    if self.ws_running:
                        logger.error(f"WebSocket error: {e}")
                        await asyncio.sleep(2)
            
            if retry_count >= max_retries:
                logger.error("WebSocket connection failed after maximum retries")
        
        # 创建新的事件循环并运行
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(connect_and_listen())
        finally:
            loop.close()
    
    def start_websocket(self):
        """启动 WebSocket 连接"""
        self.ws_running = True
        self.ws_thread = threading.Thread(target=self._run_websocket_loop, daemon=True)
        self.ws_thread.start()
        logger.info("WebSocket connection thread started")
    
    def stop_websocket(self):
        """停止 WebSocket 连接"""
        self.ws_running = False
        if self.ws_thread:
            self.ws_thread.join(timeout=5)
            logger.info("WebSocket connection stopped")
    
    def run_test(self, simulator: Simulator, recipes: list, examples: list = [], retries=3) -> dict:
        """
        Start a Vue.js web GUI for human interaction to control agents in the simulator.
        """
        # 启动 FastAPI 服务器
        server_path = os.path.join(os.path.dirname(__file__), '../../../../gui/server/main.py')
        server_path = os.path.abspath(server_path)
        
        output = sys.stdout if os.environ.get("DEBUG") else subprocess.DEVNULL

        server_proc = subprocess.Popen(
            [sys.executable, server_path],
            stdout=output,
            stderr=output,
        )
        
        # 等待服务器启动
        if not self.wait_for_server():
            server_proc.terminate()
            raise RuntimeError("Failed to start API server")
        
        # 启动 WebSocket 连接
        self.start_websocket()
        time.sleep(2)  # 给 WebSocket 一些时间建立连接
        
        # 启动日志转发
        self.start_log_forwarding()
        
        # 初始化服务器状态
        self.clear_logs()
        self.update_world_state(simulator)
        
        # 启动 Vue.js 前端（开发模式）
        web_path = os.path.join(os.path.dirname(__file__), '../../../../gui/web')
        web_path = os.path.abspath(web_path)
        
        logger.info("=" * 60)
        logger.info(f"Starting API server: {server_path}")
        logger.info(f"Starting Vue.js web interface from: {web_path}")
        
        # 启动 npm run dev
        web_proc = subprocess.Popen(
            ['npm', 'run', 'dev'],
            cwd=web_path,
            stdout=output,
            stderr=output,
        )
        
        # 保存模拟器副本
        simulator_copy = deepcopy(simulator)
        final_result = None
        
        try:
            logger.info("Human Agent Interface Started")
            logger.info(f"API Server: {self.api_url}")
            logger.info(f"WebSocket: {self.ws_url}")
            logger.info(f"Web Interface: {WEB_URL}")
            logger.info("Press Ctrl+C to stop")
            logger.info("=" * 60)

            while True:
                # 检查前端进程
                if web_proc.poll() is not None:
                    logger.warning("Frontend process has stopped unexpectedly")
                    break
                
                # 等待重置事件（非阻塞，超时 0.1 秒）
                if self.reset_event.wait(timeout=0.1):
                    self.reset_event.clear()
                    
                    logger.info("=" * 60)
                    logger.info("🔄 Resetting simulator to initial state...")
                    logger.info("=" * 60)
                    
                    # 重置模拟器
                    simulator = deepcopy(simulator_copy)
                    
                    # 更新服务器状态
                    self.clear_logs()
                    self.update_world_state(simulator)
                    
                    logger.info("Simulator reset complete")
                    continue
                
                # 等待执行事件（非阻塞，超时 0.1 秒）
                if self.execute_event.wait(timeout=0.1):
                    self.execute_event.clear()
                    
                    # 清空日志
                    self.clear_logs()
                    logger.info("=" * 60)
                    logger.info("Received new actions, executing simulation...")
                    logger.info("=" * 60)
                    
                    # 重新加载模拟器并执行
                    simulator = deepcopy(simulator_copy)
                    try:
                        simulator.load_plan(self.current_actions)
                    except Exception as e:
                        logger.error(f"Failed to load actions: {e}")
                        continue
                    
                    simulator.run_simulation()
                    # 更新世界状态
                    self.update_world_state(simulator)
                    
                    # 检查是否完成所有订单
                    remaining_orders = len(simulator.world.orders)
                    logger.info(f"Simulation completed. Remaining orders: {remaining_orders}")
                    
                    if remaining_orders == 0:
                        logger.info("=" * 60)
                        logger.info("🎉 All orders completed successfully! 🎉")
                        logger.info("=" * 60)
                        self.send_log("SUCCESS", "All orders completed successfully!")
                        self._call_api("POST", "/api/task/complete")
                        final_result = self.create_result(simulator, 0)
                        time.sleep(3)
                        break
                
                time.sleep(0.1)  # 短暂休眠，避免 CPU 占用过高
        
        except KeyboardInterrupt:
            logger.info("\n" + "=" * 60)
            logger.info("Received interrupt signal, shutting down...")
            logger.info("=" * 60)
        
        finally:
            # 停止 WebSocket
            self.stop_websocket()
            
            # 清理日志转发
            for handler in logger.handlers[:]:
                if handler.__class__.__name__ == 'LogForwarder':
                    logger.removeHandler(handler)
            
            logger.info("Cleaning up processes...")
            time.sleep(1)
            web_proc.terminate()
            server_proc.terminate()
            
            try:
                web_proc.wait(timeout=5)
                server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Processes did not terminate gracefully, forcing kill...")
                web_proc.kill()
                server_proc.kill()
            
            logger.info("Shutdown complete")
        
        return final_result if final_result else self.create_result(simulator, 0)