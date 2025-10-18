# simulator.py - Action Scheduling System

from copy import deepcopy
from typing import Dict, List
from heapq import heappop, heappush


from src.game.world_state import World
from src.game.object import *
from src.game.const import *
from src.utils.logger_config import logger, COLOR_CODES, RESET

class ActionExecutionError(Exception):
    """Custom exception for action execution errors"""
    pass

class TimePoint:
    """Represents a time point, recording which agents complete actions at this time point"""
    def __init__(self, time: int):
        self.time = time
        self.agents: List[str] = []  # List of agents completing actions at this time point

    def __lt__(self, other):
        return self.time < other.time

class Simulator:
    def __init__(self, world: World):
        self.world: World = world
        self.current_time = 0

        self.event_queue: List[TimePoint] = []
        time0 = TimePoint(0)
        for agent_name in self.world.agents:
            time0.agents.append(agent_name)
        self.event_queue.append(time0)
        self.state_history: List[dict] = []  # To record the state at each time point
        self.finished_agents = set()

    def rollback_plan(self):
        """Rollback the plan of all agents to last loaded state"""
        for agent_name, agent in self.world.agents.items():
            agent.rollback_actions()

    def load_plan(self, plan: Dict[str, List[Dict]]):
        """Load action plans for all agents"""
        for agent_name, action_list in plan.items():
            if agent_name in self.world.agents:
                agent = self.world.agents[agent_name]
                if not isinstance(action_list, list):
                    raise ValueError(f"Action plan for Agent {agent_name} is not a list")
                agent.load_actions(action_list)
            else:
                raise ValueError(f"Agent {agent_name} does not exist in the world")
        
        logger.info(f"{COLOR_CODES['CYAN']}Loaded action plans for {len(plan)} agents{RESET}")

    def _get_station_for_action(self, agent_name, target_name) -> Station:
        """Get the specified workstation for an agent"""
        target_obj = self.world.get_object_by_name(target_name)
        if not target_obj:
            raise ActionExecutionError(f"Agent {agent_name} tried to interact with non-existent object {target_name}")
        if not isinstance(target_obj, Station):
            raise ActionExecutionError(f"Agent {agent_name} tried to interact with non-station object {target_name}")
        return target_obj

    def get_action_duration_for_agent(self, agent_name: str, action: Dict) -> int:
        """Calculate action execution time for a specific agent"""
        action_type = action["action"]
        
        if action_type == "MoveTo":
            agent = self.world.agents[agent_name]
            target_pos = tuple(action["target"])
            current_pos = (agent.x, agent.y)
            return self.world.find_path(current_pos, target_pos)[0]
        elif action_type == "Wait":
            return action.get("duration", 1)
        elif action_type == "Interact":
            return INTERACT_TIME
        elif action_type == "Process":
            target_name = action["target"]
            station: Station = self._get_station_for_action(agent_name, target_name)
            if isinstance(station, ChoppingBoard):
                return PROCESS_CUT_TIME
            elif isinstance(station, Stove):
                if station.item:
                    if isinstance(station.item, Pot):
                        return PROCESS_POT_COOK_TIME
                    elif isinstance(station.item, Pan):
                        return PROCESS_PAN_COOK_TIME
                raise ActionExecutionError(f"Agent {agent_name} tried to process on empty stove without any cookware on it")
            elif isinstance(station, Sink):
                return PROCESS_WASH_PLATE_TIME
            else:
                raise ActionExecutionError(f"Agent {agent_name} tried to process on unsupported workstation {target_name}")
        elif action_type == "Finish":
            return 0
        else:
            raise ActionExecutionError(f"Unknown action type: {action_type}")
    
    def assign_next_action(self, agent_name: str):
        """Assign the next action for the specified agent"""
        agent = self.world.agents[agent_name]
        
        if not agent.is_idle:
            return  # Still executing current action

        if len(agent.action_queue) == 0:
            agent.start_next_action(self.current_time, 0)
            logger.info(f"{COLOR_CODES['GREEN']}Agent {agent_name} has completed all actions{RESET}")
            return
        
        next_action = agent.action_queue[0]  # Preview next action
        duration = self.get_action_duration_for_agent(agent_name, next_action)
        if duration < 0:
            raise ActionExecutionError(f"Agent {agent_name} cannot execute action {next_action}")
        
        reserved_station = None
        started = False
        
        if next_action["action"] in ["Interact", "Process"]:
            target_name = next_action["target"]
            station: Station = self._get_station_for_action(agent_name, target_name)
            if not self.world.is_adjacent((agent.x, agent.y), (station.x, station.y)):
                raise ActionExecutionError(f"Agent {agent_name} tried to {next_action['action']} with workstation {target_name} that is not nearby")
            reserved_station = station
            station.use(agent_name)

        try:
            agent.start_next_action(self.current_time, duration)
            started = True
            logger.info(f"Time {self.current_time}: Agent {agent_name} starts executing action {next_action}, expected completion time {agent.finish_time}")
        finally:
            if not started and reserved_station:
                reserved_station.release()

    def complete_current_action(self, agent_name: str):
        """Complete the current action for the specified agent"""
        agent = self.world.agents[agent_name]
        
        if agent.is_idle or agent.current_action is None:
            return  # No action being executed

        action = agent.current_action
        logger.info(f"{COLOR_CODES['PURPLE']}Action to complete: {action}{RESET}")

        station: Station | None = None
        
        # Execute action effects
        try:
            if action["action"] == "MoveTo":
                target_pos = tuple(action["target"])
                time, path = self.world.find_path((agent.x, agent.y), target_pos)
                agent.x, agent.y = path[-1]

            elif action["action"] == "Interact":
                target_name = action["target"]
                station = self._get_station_for_action(agent_name, target_name)
                if not self.world.is_adjacent((agent.x, agent.y), (station.x, station.y)):
                    raise ActionExecutionError(f"Agent {agent_name} tried to interact with workstation {target_name} that is not nearby")
                station.interact(agent_name, self.world, self.current_time)
                station.release()
            elif action["action"] == "Process":
                target_name = action["target"]
                station = self._get_station_for_action(agent_name, target_name)
                if not self.world.is_adjacent((agent.x, agent.y), (station.x, station.y)):
                    raise ActionExecutionError(f"Agent {agent_name} tried to process on workstation {target_name} that is not nearby")
                station.process(agent_name)
                station.release()
            elif action["action"] == "Wait":
                pass
            elif action["action"] == "Finish":
                agent.all_finished = True
                self.finished_agents.add(agent_name)

            agent.is_idle = True
            agent.current_action = None
            # Already removed current action from queue
            # agent.action_queue.pop(0)  # This step is done in start_next_action
            logger.info(f"Time {self.current_time}: Agent {agent_name} completed action {action}")
        finally:
            if station:
                station.release()
        

    def update_stations(self, current_time: int):
        """Check the status of all workstations"""
        for obj in self.world.objects.values():
            if isinstance(obj, Stove) and obj.item:
                if isinstance(obj.item, Pan) or isinstance(obj.item, Pot):
                    obj.item.update_cooking(current_time)
            elif isinstance(obj, PlateReturn):
                obj.update(current_time)

    def run_simulation(self, raise_on_error: bool = False):
        """Run the complete simulation"""
        logger.info("=== Starting Simulation ===")
        logger.info(f"Initial state:")
        logger.info(self.status())
        # logger.info(self.world.to_json())

        while self.event_queue:
            try:
                self.step()
            except ActionExecutionError as e:
                logger.error(f"{COLOR_CODES['RED']}Simulation error: {e}{RESET}")
                if raise_on_error:
                    raise e
                return
            except Exception as e:
                logger.error(f"{COLOR_CODES['RED']}Simulation unexpected error: {e}{RESET}")
                if raise_on_error:
                    raise e
                return

        logger.info(f"\n=== Simulation Ended, Total Time {self.current_time} ===")

    def update_event_queue(self):
        """Update event queue, ensuring each agent's next action completion time is in the queue"""
        for agent_name, agent in self.world.agents.items():
            if not agent.is_idle and agent.current_action:
                finish_time = agent.finish_time
                have_tp = False
                for tp in self.event_queue:
                    if tp.time == finish_time:
                        if agent_name not in tp.agents:
                            tp.agents.append(agent_name)
                        have_tp = True
                        break
                if not have_tp:
                    new_tp = TimePoint(finish_time)
                    new_tp.agents.append(agent_name)
                    heappush(self.event_queue, new_tp)

    def resolve_instant_actions(self):
        """Resolve all instant actions (actions with zero duration)"""
        for agent_name, agent in self.world.agents.items():
            self.assign_next_action(agent_name)
            while agent.finish_time == self.current_time and not agent.is_idle:
                self.complete_current_action(agent_name)
                self.assign_next_action(agent_name)
        self.update_event_queue()

    def submit_plan(self, actions: Dict[str, List]):
        """Submit action plans for all agents"""
        self.load_plan(actions)
        self.resolve_instant_actions()

    def step(self):
        """Advance to the next time point, process one time point in the event queue"""
        if not self.event_queue:
            return

        current_time_point = heappop(self.event_queue)
        self.current_time = current_time_point.time
        logger.info(f"\n--- Time Advanced to {self.current_time} ---")
        self.update_stations(self.current_time)
        have_agent_finished = False
        for agent_name in current_time_point.agents:
            agent = self.world.agents[agent_name]
            if current_time_point.time:
                # have_agent_finished = True
                self.complete_current_action(agent_name)
            self.assign_next_action(agent_name)
            while agent.finish_time == self.current_time and not agent.is_idle:
                self.complete_current_action(agent_name)
                self.assign_next_action(agent_name)
            if not agent.all_finished and len(agent.action_queue) == 0 and agent.is_idle:
                have_agent_finished = True
            if not agent.current_action:
                continue

        self.update_event_queue()
        
        self.state_history.append({
            "time": self.current_time,
            "world": deepcopy(self.world.to_json())
        })

        logger.info(f"{COLOR_CODES['PURPLE']}Observation:{RESET}")
        logger.info(self.status())
        # logger.info(self.world.to_json())

        return have_agent_finished
    
    def next_decision_step(self):
        """Advance simulation to the next decision point where at least one agent needs to make a decision"""
        need_decision_agents = self.get_decision_agents()
        while not need_decision_agents and self.event_queue:
            self.step()
            need_decision_agents = self.get_decision_agents()
        return need_decision_agents
        

    def get_observation(self) -> Dict:
        """Get the current observation of the world state"""
        world_json = deepcopy(self.world.to_json())
        agent_runtimes = {}
        for agent_name, agent in self.world.agents.items():
            agent_runtimes[agent_name] = {
                "position": (agent.x, agent.y),
                "is_idle": agent.is_idle,
                "current_action": agent.current_action,
                "finish_time": agent.finish_time,
                "remaining_actions": len(agent.action_queue),
            }
        return {
            "current_time": self.current_time,
            "world": world_json,
            "agent_runtimes": agent_runtimes,
            "pending_orders": self.world.orders,
            "agent_status_text": self.status(),
        }
    
    
    def get_finished_agents(self) -> List[str]:
        """Return a list of agents that have completed all their actions"""
        return list(self.finished_agents)

    def get_decision_agents(self) -> List[str]:
        """Return a list of agents that need to make decisions (do not have actions assigned but not finished)"""
        decision_agents = []
        for agent_name, agent in self.world.agents.items():
            if agent.is_idle and not agent.all_finished and len(agent.action_queue) == 0:
                decision_agents.append(agent_name)
        return decision_agents

    def status(self):
        """Return the status of all agents"""
        status = ""
        status += f"Current time: {self.current_time}\n"
        for agent_name, agent in self.world.agents.items():
            if agent.is_idle:
                status += f"Agent {agent_name}: vacant (remaining actions: {len(agent.action_queue)})\n"
            else:
                if agent.current_action:
                    status += f"Agent {agent_name}: executing {agent.current_action}, finish at: {agent.finish_time}, remaining actions: {len(agent.action_queue)}\n"
                    for act in agent.action_queue:
                        status += f"{act}, "
                    status = status.rstrip(", ") + "\n"
                else:
                    # raise ValueError(f"Agent {agent_name} is not idle but has no current action")
                    logger.warning(f"{COLOR_CODES['YELLOW']}Agent {agent_name} is not idle but has no current action{RESET}")
                    exit(1)

        return status
    
    def is_done(self) -> bool:
        """Check if all orders are completed"""
        return len(self.world.orders) == 0