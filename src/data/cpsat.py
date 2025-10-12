from ortools.sat.python import cp_model

def solve_task_scheduling(tasks, num_agents=1, time_limit_seconds=60):
    """
    Solve task scheduling problem using Google OR-Tools CP-SAT (supports single or multiple agents)
    
    Parameters:
    tasks: List of tasks, each containing name, time, dependencies
    num_agents: Number of agents, default is 1 (single agent mode)
    time_limit_seconds: Time limit for solving (seconds)
    
    Returns:
    min_time: Minimum completion time
    schedule: Task execution plan (includes agent assignment in multi-agent mode)
    status: Solution status
    """
    
    model = cp_model.CpModel()
    
    # Build task index
    task_dict = {task['name']: i for i, task in enumerate(tasks)}
    n = len(tasks)
    
    # Estimate time upper bound
    max_delay = 0
    for task in tasks:
        for delay in task['dependencies'].values():
            max_delay = max(max_delay, delay)
    horizon = sum(task['time'] for task in tasks) + max_delay
    
    # Decision variables: start time and end time for each task
    starts = {}
    ends = {}
    agent_assignments = {} if num_agents > 1 else None
    
    for i, task in enumerate(tasks):
        start_var = model.NewIntVar(0, horizon, f'start_{task["name"]}')
        end_var = model.NewIntVar(0, horizon, f'end_{task["name"]}')
        
        starts[i] = start_var
        ends[i] = end_var
        
        # Ensure end = start + duration
        model.Add(ends[i] == starts[i] + task['time'])
        
        # Multi-agent mode: add agent assignment variable
        if num_agents > 1:
            agent_var = model.NewIntVar(0, num_agents - 1, f'agent_{task["name"]}')
            agent_assignments[i] = agent_var
    
    # Constraint 1: Dependency constraints (valid across agents)
    for i, task in enumerate(tasks):
        for dep_name, delay in task['dependencies'].items():
            dep_idx = task_dict[dep_name]
            model.Add(starts[i] >= ends[dep_idx] + delay)
    
    # Constraint 2: No overlap constraint for tasks
    if num_agents == 1:
        # Single agent mode: all tasks globally non-overlapping
        intervals = []
        for i, task in enumerate(tasks):
            interval_var = model.NewIntervalVar(
                starts[i], task['time'], ends[i], f'interval_{task["name"]}'
            )
            intervals.append(interval_var)
        model.AddNoOverlap(intervals)
    else:
        # Multi-agent mode: tasks on same agent don't overlap
        for agent_id in range(num_agents):
            agent_intervals = []
            
            for i, task in enumerate(tasks):
                # Create boolean variable: whether task i is assigned to current agent
                is_on_agent = model.NewBoolVar(f'task_{i}_on_agent_{agent_id}')
                model.Add(agent_assignments[i] == agent_id).OnlyEnforceIf(is_on_agent)
                model.Add(agent_assignments[i] != agent_id).OnlyEnforceIf(is_on_agent.Not())
                
                # Create optional interval: only active when task is assigned to current agent
                optional_interval = model.NewOptionalIntervalVar(
                    starts[i], task['time'], ends[i], is_on_agent,
                    f'opt_interval_{task["name"]}_agent_{agent_id}'
                )
                agent_intervals.append(optional_interval)
            
            # All tasks on this agent don't overlap
            model.AddNoOverlap(agent_intervals)
    
    # Objective: minimize makespan
    makespan = model.NewIntVar(0, horizon, 'makespan')
    model.AddMaxEquality(makespan, list(ends.values()))
    model.Minimize(makespan)
    
    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_seconds
    solver.parameters.log_search_progress = False
    
    status = solver.Solve(model)
    
    # Parse results
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        min_time = solver.Value(makespan)
        
        # Build schedule
        schedule = []
        for i, task in enumerate(tasks):
            item = {
                'task': task['name'],
                'start': solver.Value(starts[i]),
                'finish': solver.Value(ends[i]),
                'duration': task['time']
            }
            
            # Multi-agent mode: add agent information
            if num_agents > 1:
                item['agent'] = solver.Value(agent_assignments[i])
            
            schedule.append(item)
        
        # Sort: multi-agent by agent and start time, single agent by start time
        if num_agents > 1:
            schedule.sort(key=lambda x: (x['agent'], x['start']))
        else:
            schedule.sort(key=lambda x: x['start'])
        
        status_str = "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE"
        return min_time, schedule, status_str
    else:
        return None, None, "NO_SOLUTION"


def print_schedule(min_time, schedule, status, num_agents=1):
    """Print scheduling results"""
    if schedule is None:
        print(f"Solution status: {status} - No feasible solution found")
        return
    

    print(f"Solution status: {status}")
    print(f"Minimum completion time: {min_time}")
    
    if num_agents > 1:
        print(f"\nTask execution plan (sorted by agent and start time):")
        print("-" * 70)
        for item in schedule:
            print(f"{item['task']:12} | Agent {item['agent']} | Start: {item['start']:3} | Finish: {item['finish']:3} | Duration: {item['duration']:2}")
        print("-" * 70)
        
        # Gantt chart grouped by agent
        print("\nGantt chart (grouped by agent):")
        for agent_id in range(num_agents):
            print(f"\nAgent {agent_id}:")
            agent_tasks = [item for item in schedule if item['agent'] == agent_id]
            if not agent_tasks:
                print("  (No tasks)")
            for item in agent_tasks:
                bar = ' ' * item['start'] + '█' * item['duration']
                print(f"  {item['task']:12} | {bar}")
    else:
        print(f"\nTask execution plan (sorted by start time):")
        print("-" * 60)
        for item in schedule:
            print(f"{item['task']:12} | Start: {item['start']:3} | Finish: {item['finish']:3} | Duration: {item['duration']:2}")
        print("-" * 60)
        
        # Simple Gantt chart visualization
        print("\nGantt chart (text version):")
        for item in schedule:
            bar = ' ' * item['start'] + '█' * item['duration']
            print(f"{item['task']:12} | {bar}")


def verify_dependencies(tasks, schedule, num_agents=1):
    """Verify if dependency relationships are satisfied"""
    print("\n" + "=" * 70)
    print("Dependency verification:")
    print("=" * 70)
    
    if num_agents > 1:
        task_info = {item['task']: (item['start'], item['finish'], item['agent']) 
                     for item in schedule}
    else:
        task_info = {item['task']: (item['start'], item['finish']) 
                     for item in schedule}
    
    all_satisfied = True
    for task in tasks:
        task_name = task['name']
        
        if num_agents > 1:
            task_start, task_finish, task_agent = task_info[task_name]
            print(f"\n{task_name} (Agent {task_agent}):")
        else:
            task_start, task_finish = task_info[task_name]
            print(f"\n{task_name}:")
        
        if not task['dependencies']:
            print("  No dependencies")
        else:
            for dep_name, delay in task['dependencies'].items():
                if num_agents > 1:
                    dep_start, dep_finish, dep_agent = task_info[dep_name]
                    actual_gap = task_start - dep_finish
                    satisfied = actual_gap >= delay
                    status_icon = "✓" if satisfied else "✗"
                    print(f"  Depends on {dep_name} (Agent {dep_agent}, delay≥{delay}): actual gap={actual_gap} {status_icon}")
                else:
                    dep_start, dep_finish = task_info[dep_name]
                    actual_gap = task_start - dep_finish
                    satisfied = actual_gap >= delay
                    status_icon = "✓" if satisfied else "✗"
                    print(f"  Depends on {dep_name} (delay≥{delay}): actual gap={actual_gap} {status_icon}")
                
                if not satisfied:
                    all_satisfied = False
    
    print("\n" + "=" * 70)
    if all_satisfied:
        print("✓ All dependencies satisfied!")
    else:
        print("✗ Some dependencies not satisfied!")
    print("=" * 70)


# Test cases
if __name__ == "__main__":
    tasks = [
        {"name": "subtask1", "time": 4, "dependencies": {}},
        {"name": "subtask2", "time": 1, "dependencies": {}},
        {"name": "subtask3", "time": 9, "dependencies": {"subtask2": 0}},
        {"name": "subtask4", "time": 4, "dependencies": {"subtask3": 0}},
        {"name": "subtask5", "time": 8, "dependencies": {"subtask4": 0}},
        {"name": "subtask6", "time": 8, "dependencies": {}},
        {"name": "subtask7", "time": 15, "dependencies": {"subtask1": 0, "subtask5": 24, "subtask6": 0}}
    ]
    
    # Test single agent
    print("=" * 70)
    print("Single Agent Task Scheduling Problem")
    print("=" * 70)
    
    min_time_1, schedule_1, status_1 = solve_task_scheduling(tasks, num_agents=1)
    print_schedule(min_time_1, schedule_1, status_1, num_agents=1)
    verify_dependencies(tasks, schedule_1, num_agents=1)
    
    # Test 2 agents
    print("\n\n" + "=" * 70)
    print("Multi-Agent Task Scheduling Problem - 2 Agents")
    print("=" * 70)
    
    min_time_2, schedule_2, status_2 = solve_task_scheduling(tasks, num_agents=2)
    print_schedule(min_time_2, schedule_2, status_2, num_agents=2)
    verify_dependencies(tasks, schedule_2, num_agents=2)
    
    # Test 3 agents
    print("\n\n" + "=" * 70)
    print("Multi-Agent Task Scheduling Problem - 3 Agents")
    print("=" * 70)
    
    min_time_3, schedule_3, status_3 = solve_task_scheduling(tasks, num_agents=3)
    print_schedule(min_time_3, schedule_3, status_3, num_agents=3)
    verify_dependencies(tasks, schedule_3, num_agents=3)