INSTRUCTION = """
You are given a list of abstract subtasks.
Each subtask has a name, a required execution time duration, and a set of dependency constraints.
A dependency `{{ "A": x }}` means that this subtask can only start **at least x time units after subtask A finishes**.

You can control **{agent_num} agent(s)** that can work independently in parallel.
Each agent can only execute **one subtask at a time**, and a subtask cannot be split across agents.

Your goal is to **assign the subtasks to each agent** and **determine the execution order of subtasks for each agent**,
so that the final completion time of all subtasks is minimized while satisfying all dependency and delay constraints.

Before giving the final answer, think step by step:
- Identify all dependency chains among subtasks.
- Determine which subtasks can be executed in parallel and which are blocked by dependencies.
- Estimate the earliest possible start and finish times of each subtask under the given constraints.
- Assign subtasks to agents to minimize idle time and total completion time.
- Finally, produce the ordered task list for each agent.

After reasoning, output only the final task allocation in the required format.

Output Format:

```json
[
    ["task_for_agent1_in_order"],
    ["task_for_agent2_in_order"],
    ...
]
```

Each inner list represents one agent's task sequence in execution order.
Do **not** include timestamps or explanations — just the task names.

Here is an example for your reference:

Input Example:

```json
[
    {{
        "name": "subtask1",
        "time": 4,
        "dependencies": {{}}
    }},
    {{
        "name": "subtask2",
        "time": 1,
        "dependencies": {{}}
    }},
    {{
        "name": "subtask3",
        "time": 9,
        "dependencies": {{
            "subtask2": 0
        }}
    }},
    {{
        "name": "subtask4",
        "time": 4,
        "dependencies": {{
            "subtask3": 0
        }}
    }},
    {{
        "name": "subtask5",
        "time": 8,
        "dependencies": {{
            "subtask4": 0
        }}
    }},
    {{
        "name": "subtask6",
        "time": 8,
        "dependencies": {{}}
    }},
    {{
        "name": "subtask7",
        "time": 15,
        "dependencies": {{
            "subtask1": 0,
            "subtask5": 24,
            "subtask6": 0
        }}
    }}
]
```

Output Example (for 1 agent):
```json
[
    ["subtask2", "subtask3", "subtask4", "subtask5", "subtask1", "subtask6", "subtask7"]
]
```

Output Example (for 2 agents):

```json
[
    ["subtask2", "subtask3", "subtask4", "subtask5", "subtask7"],
    ["subtask1", "subtask6"]
]
```

Now, please solve the following subtasks with {agent_num} agent(s):
{subtasks}
"""