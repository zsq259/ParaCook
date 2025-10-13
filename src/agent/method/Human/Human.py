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

class HumanAgent(Agent):
    def __init__(self, model: Model, api_url: str = "http://localhost:5000"):
        super().__init__(model)
        self.api_url = api_url
        self.session = requests.Session()
        self.log_handler = None
        self.should_stop_logging = False
        
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
            "message": message,  # 保留原始消息，包含 ANSI 代码
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
        self.log_handler.setLevel(logging.DEBUG)  # 捕获所有级别
        
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
    
    def check_should_execute(self) -> Optional[dict]:
        """检查是否应该执行，并获取动作"""
        result = self._call_api("GET", "/api/actions/should_execute")
        if result and result.get("success") and result.get("should_execute"):
            return result.get("data", {})
        return None

    def check_should_reset(self) -> bool:
        """检查是否应该重置"""
        result = self._call_api("GET", "/api/should_reset")
        if result and result.get("success") and result.get("should_reset"):
            # 确认重置
            self._call_api("POST", "/api/reset/confirm")
            return True
        return False
    
    def run_test(self, simulator: Simulator, recipes: list, examples: list = [], retries=3) -> dict:
        """
        Start a Vue.js web GUI for human interaction to control agents in the simulator.
        """
        # 启动 FastAPI 服务器
        server_path = os.path.join(os.path.dirname(__file__), '../../../../gui/server/main.py')
        server_path = os.path.abspath(server_path)
        
        # logger.info(f"Starting API server: {server_path}")
        server_proc = subprocess.Popen(
            [sys.executable, server_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 等待服务器启动
        if not self.wait_for_server():
            server_proc.terminate()
            raise RuntimeError("Failed to start API server")
        
        # 启动日志转发
        self.start_log_forwarding()
        
        # 初始化服务器状态
        self.clear_logs()
        self.update_world_state(simulator)
        
        # 启动 Vue.js 前端（开发模式）
        web_path = os.path.join(os.path.dirname(__file__), '../../../../gui/web')
        web_path = os.path.abspath(web_path)
        
        logger.info("=" * 60)
        logger.info(f"Starting Vue.js web interface from: {web_path}")
        
        # 启动 npm run dev
        web_proc = subprocess.Popen(
            ['npm', 'run', 'dev'],
            cwd=web_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 保存模拟器副本
        simulator_copy = deepcopy(simulator)
        final_result = None
        
        try:
            logger.info("Human Agent Interface Started")
            logger.info(f"API Server: {self.api_url}")
            logger.info("Web Interface: http://localhost:5173")
            logger.info("Press Ctrl+C to stop")
            logger.info("=" * 60)

            while True:
                # 从服务器获取动作
                if web_proc.poll() is not None:
                    print("Warning: Frontend process has stopped unexpectedly")
                    break
                
                if self.check_should_reset():
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
                
                actions = self.check_should_execute()

                if actions:
                    # 清空日志
                    self.clear_logs()
                    logger.info("=" * 60)
                    logger.info("Received new actions, executing simulation...")
                    logger.info("=" * 60)
                    
                    # 重新加载模拟器并执行
                    simulator = deepcopy(simulator_copy)
                    try:
                        simulator.load_plan(actions)
                    except Exception as e:
                        logger.error(f"Failed to load actions: {e}")
                        exit(1)
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
                        time.sleep(3)  # 给用户时间查看
                        break
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("\n" + "=" * 60)
            logger.info("Received interrupt signal, shutting down...")
            logger.info("=" * 60)
        
        finally:
            # 清理进程
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