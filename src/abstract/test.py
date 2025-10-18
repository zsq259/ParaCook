from operator import not_
import os, json
from collections import deque

from src.data.cpsat import solve_task_scheduling
from src.abstract.instruction import INSTRUCTION
from src.utils.utils import get_model_wrapper, extract_json
from src.agent.model.model import PredictConfig


def check_task_dependencies(task, finished_tasks):
    max_dep_finish = 0
    for dep_name, delay in task['dependencies'].items():
        this_dep_met = False
        for name, time in finished_tasks:
            if name == dep_name:
                this_dep_met = True
                max_dep_finish = max(max_dep_finish, time + delay)
        if not this_dep_met:
            return False, 0
    return True, max_dep_finish


def process_agent_task(agent_id, task_index, schedule, task_map, finished_tasks, current_time):
    if task_index >= len(schedule[agent_id]):
        return False, None
    task_name = schedule[agent_id][task_index]
    task = task_map[task_name]
    dep_met, max_dep_finish = check_task_dependencies(task, finished_tasks)
    if dep_met:
        current_time[agent_id] = max(current_time[agent_id], max_dep_finish) + task['time']
        finished_tasks.add((task_name, current_time[agent_id]))
        return True, task_index + 1
    else:
        return False, task_index

def check_dependencies(tasks, schedule:list[list[str]]) -> tuple[bool, int]:
    finished_tasks = set()
    current_time = [0] * len(schedule)
    task_map = {task['name']: task for task in tasks}
    task_queue = deque()
    for agent_id, task_list in enumerate(schedule):
        done, next_index = process_agent_task(agent_id, 0, schedule, task_map, finished_tasks, current_time)
        if done:
            task_queue.append((agent_id, next_index))
        else:
            task_queue.append((agent_id, 0))

    queue_changed = True
    not_changed_count = 0
    max_not_changed = len(schedule) # all agents not changed
    while task_queue:
        agent_id, task_index = task_queue.popleft()
        queue_changed = False
        done, next_index = process_agent_task(agent_id, task_index, schedule, task_map, finished_tasks, current_time)
        if next_index is None:
            continue
        if done:
            task_queue.append((agent_id, next_index))
            queue_changed = True
            not_changed_count = 0
        else:
            task_queue.append((agent_id, task_index))
            not_changed_count += 1
            if not_changed_count > max_not_changed:
                break
            
    if len(finished_tasks) == len(tasks):
        return True, max(current_time)
    else:
        return False, -1


def test_subtasks(agent_num, subtasks, model, result_path, result_name):
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    # If exists result, skip
    if not os.path.exists(result_path):
        results = {}
    else:
        with open(result_path, 'r') as f:
            results = json.load(f)
    if result_name in results:
        print(f"Result for {result_name} already exists, skipping.")
        return
    print(f"Processing {result_name} with model {model}...")

    answer = [[""]]
    if model == "cp_sat":
        min_time, schedule, status = solve_task_scheduling(subtasks, agent_num)
        if not schedule:
            raise ValueError(f"No solution found for {result_path}!")
        print(schedule)
        
        # set anser to empty lists for each agent
        answer = [[] for _ in range(agent_num)]
        for i in range(agent_num):
            for subtask in schedule:
                if subtask.get('agent', 0) == i:
                    answer[i].append(subtask['task'])
        print(answer)
        # exit(1)
        is_valid, total_time = check_dependencies(subtasks, answer)
        assert(total_time == min_time)
        
    else:
        model_wrapper = get_model_wrapper(model)
        model = model_wrapper(model)
        prompt = INSTRUCTION.format(agent_num=agent_num, subtasks=json.dumps(subtasks, indent=4))
        response = model.predict(PredictConfig(prompt=prompt, temperature=0))
        print("Model response:", response)
        try:
            answer = extract_json(response)
            if not isinstance(answer, list) or not all(isinstance(agent_tasks, list) for agent_tasks in answer):
                raise ValueError("Invalid format: answer should be a list of lists.")
        except Exception as e:
            print(f"Failed to parse model output as JSON: {e}")
            print(f"Original model output: {response}")
            return
    
    is_valid, total_time = check_dependencies(subtasks, answer)
    
    results[result_name] = {
        "done": is_valid,
        "time": total_time,
        "answer": answer
    }
    with open(result_path, 'w') as f:
        json.dump(results, f, indent=4)


if __name__ == "__main__":
    data_dir = "data/abstract"
    resule_dir = "results/abstract"
    recipes = ["sashimi", "salad", "sushi", "burger", "pasta", "burrito"]
    # models = ["cp_sat", "gpt-5", "gemini-2.5-pro", "claude-opus-4-1-20250805", "qwen3-max-preview"]
    models = ["deepseek-reasoner"]
    agent_nums = [2, 3]
    orders_nums = [3, 4]
    seeds = [42]
    for recipe in recipes:
        for model in models:
            for agent_num in agent_nums:
                for orders_num in orders_nums:
                    for seed in seeds:
                        file_path = f"{data_dir}/{recipe}/seed_{seed}/orders_num_{orders_num}.json"
                        if not os.path.exists(file_path):
                            raise ValueError(f"File {file_path} does not exist!")
                        subtasks = json.load(open(file_path, 'r'))
                        result_path = f"{resule_dir}/{model}.json"
                        result_name = f"{recipe}/seed_{seed}/agent_num_{agent_num}/orders_num_{orders_num}"
                        test_subtasks(agent_num, subtasks, model, result_path, result_name)
    print("All tests completed.")