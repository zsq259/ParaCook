input = """
Map JSON:
{
    "name": "kitchen_burger_8x6",
    "width": 8,
    "height": 6,
    "agents": [
        {"name": "agent1", "x": 1, "y": 4},
        {"name": "agent2", "x": 6, "y": 4}
    ],
    "tiles": [
        {"x": 0, "y": 0, "type": "obstacle", "name": "wall"},
        {"x": 1, "y": 0, "type": "station", "name": "dispenser1", "provides": "bread"},
        {"x": 2, "y": 0, "type": "station", "name": "dispenser2", "provides": "meat"},
        {"x": 3, "y": 0, "type": "station", "name": "dispenser3", "provides": "lettuce"},
        {"x": 4, "y": 0, "type": "station", "name": "dispenser4", "provides": "tomato"},
        {"x": 5, "y": 0, "type": "station", "name": "chopping_board1"},
        {"x": 6, "y": 0, "type": "station", "name": "chopping_board2"},
        {"x": 7, "y": 0, "type": "obstacle", "name": "wall"},
        {"x": 0, "y": 1, "type": "obstacle", "name": "wall"},
        {"x": 7, "y": 1, "type": "obstacle", "name": "wall"},
        {"x": 0, "y": 2, "type": "obstacle", "name": "wall"},
        {"x": 7, "y": 2, "type": "obstacle", "name": "wall"},
        {"x": 0, "y": 3, "type": "obstacle", "name": "wall"},
        {"x": 7, "y": 3, "type": "obstacle", "name": "wall"},
        {"x": 0, "y": 4, "type": "obstacle", "name": "wall"},
        {"x": 7, "y": 4, "type": "obstacle", "name": "wall"},
        {"x": 0, "y": 5, "type": "obstacle", "name": "wall"},
        {"x": 1, "y": 5, "type": "station", "name": "sink"},
        {"x": 2, "y": 5, "type": "station", "name": "plate_return"},
        {"x": 3, "y": 5, "type": "station", "name": "table1", "item": "plate"},
        {"x": 4, "y": 5, "type": "station", "name": "serving_window"},
        {"x": 5, "y": 5, "type": "station", "name": "stove", "item": "pan"},
        {"x": 6, "y": 5, "type": "station", "name": "table3"},
        {"x": 7, "y": 5, "type": "obstacle", "name": "wall"}
    ]
}

Recipes:
- burger_basic: First chop the meat and cook it. Then put the cooked meat with a piece of bread on a plate to make a basic burger.

Orders:
[burger_basic]
"""

output = """
```json
{
    "reasoning": "**Task Analysis:**\nWe need to prepare a basic burger that requires chopped and cooked meat, then combine the cooked meat with bread on a plate. Analyzing the map layout, this is an 8x6 kitchen with bread dispenser, meat dispenser, lettuce dispenser, tomato dispenser, and two chopping boards on the top row (y=0), and sink, table with plate, serving window, stove with pan, and other equipment on the bottom row (y=5).\n\n**Initial Agent Positions:**\n- agent1 is at (1,4), very close to the bread dispenser\n- agent2 is at (6,4), closer to the meat dispenser and chopping boards\n\n**Task Allocation Strategy:**\nConsidering the complexity of burger preparation, I decided to assign agent1 to handle the simple bread preparation task, while agent2 takes on the more complex meat processing tasks (chopping meat, cooking meat) as well as final burger assembly and serving. This division of labor maximizes the parallel working capability of both agents while avoiding conflicts at critical equipment.\n\n**Dependency Graph Analysis:**\nThe burger preparation has a clear dependency chain:\n1. get_bread (no dependencies) - agent1 retrieves bread from dispenser\n2. get_meat (no dependencies) - agent2 retrieves meat from dispenser  \n3. chop_meat (depends on get_meat) - agent2 chops meat on chopping board\n4. cook_meat (depends on chop_meat) - agent2 places chopped meat in pan on stove\n5. get_plate (no dependencies) - agent2 retrieves plate from table\n6. assemble_burger (depends on cook_meat, get_bread, get_plate) - agent2 transfers cooked meat to plate with bread\n7. serve_burger (depends on assemble_burger) - agent2 submits completed burger at serving window\n\n**Critical Path Calculation:**\nThe critical path is: get_meat → chop_meat → cook_meat → assemble_burger → serve_burger\nTotal critical path time: 7 + 6 + 24 + 3 + 1 = 41 time units\n\nParallel path (agent1): get_bread = 3 time units (completes well before critical path)\n\n**Detailed Execution Timeline:**\n\nAgent1's Task Path (Bread Preparation):\n- Time 0-3: Move from (1,4) to (1,1), distance 3, takes 3 time units\n- Time 3: Interact with dispenser1 to get bread, takes 0 time (instant interaction)\n- Time 3-7: Move from (1,1) to (3,4), distance 4, takes 4 time units\n- Time 7: Interact with table1 to place bread on plate, takes 0 time\n- Agent1 completes at time 7\n\nAgent2's Task Path (Meat Processing and Assembly):\n- Time 0-7: Move from (6,4) to (2,1), distance 5 right + 3 up = 8 tiles... wait, let me recalculate: from (6,4) to (2,1) is |6-2| + |4-1| = 4 + 3 = 7, takes 7 time units\n- Time 7: Interact with dispenser2 to get meat, takes 0 time\n- Time 7-10: Move from (2,1) to (5,1), distance 3, takes 3 time units\n- Time 10: Interact with chopping_board1 to place meat, takes 0 time\n- Time 10-14: Process (chop) meat on chopping_board1, takes 4 time units\n- Time 14: Interact with chopping_board1 to pick up chopped meat, takes 0 time\n- Time 14-17: Move from (5,1) to (5,4), distance 3, takes 3 time units\n- Time 17: Interact with stove to place chopped meat in pan, takes 0 time. Pan cooking starts automatically and takes 24 time units (completion at time 41)\n- Time 17-19: Move from (5,4) to (3,4), distance 2, takes 2 time units\n- Time 19: Interact with table1 to pick up plate with bread, takes 0 time\n- Time 19-21: Move from (3,4) to (5,4), distance 2, takes 2 time units\n- Time 21-41: Wait 20 time units for meat to finish cooking (cooking started at time 17, completes at time 41)\n- Time 41: Interact with stove to transfer cooked meat from pan to plate, takes 0 time\n- Time 41-42: Move from (5,4) to (4,4), distance 1, takes 1 time unit\n- Time 42: Interact with serving_window to submit burger, takes 0 time\n- Agent2 completes at time 42\n\n**Time Synchronization and Coordination:**\n- Agent1 completes bread preparation at time 7, exactly when agent2 has just obtained meat and starts processing\n- Agent2's critical path is the bottleneck: meat chopping (4 units) + cooking (24 units) dominates\n- During the meat cooking waiting period (time 21-41), agent2 has already retrieved the plate with bread, making efficient use of idle time\n- Total completion time is 42 time units\n\n**Optimization Considerations:**\n- Reasonable task division avoids resource competition at critical stations (chopping board, stove)\n- Agent1 handles simple, fast task (bread) while agent2 handles complex, long task (meat + assembly)\n- Full utilization of parallelism: both agents work simultaneously\n- Makes full use of meat cooking waiting time to retrieve plate beforehand",
    "graph": {
        "START": ["get_bread", "get_meat"],
        "get_bread": ["assemble_burger"],
        "get_meat": ["chop_meat"],
        "chop_meat": ["cook_meat"],
        "cook_meat": ["assemble_burger"],
        "get_plate": ["assemble_burger"],
        "assemble_burger": ["serve_burger"],
        "serve_burger": ["END"],
        "END": []
    },
    "time_dict": {
        "START": 0,
        "get_bread": 3,
        "get_meat": 7,
        "chop_meat": 4,
        "cook_meat": 24,
        "get_plate": 0,
        "assemble_burger": 0,
        "serve_burger": 0,
        "END": 0
    }
    "plan": {
        "agent1": [
            {"action": "MoveTo", "target": [1, 1]},
            {"action": "Interact", "target": "dispenser1"},
            {"action": "MoveTo", "target": [3, 4]},
            {"action": "Interact", "target": "table1"},
            {"action": "Finish"}
        ],
        "agent2": [
            {"action": "MoveTo", "target": [2, 1]},
            {"action": "Interact", "target": "dispenser2"},
            {"action": "MoveTo", "target": [5, 1]},
            {"action": "Interact", "target": "chopping_board1"},
            {"action": "Process", "target": "chopping_board1"},
            {"action": "Interact", "target": "chopping_board1"},
            {"action": "MoveTo", "target": [5, 4]},
            {"action": "Interact", "target": "stove"},
            {"action": "MoveTo", "target": [3, 4]},
            {"action": "Interact", "target": "table1"},
            {"action": "MoveTo", "target": [5, 4]},
            {"action": "Wait", "duration": 20},
            {"action": "Interact", "target": "stove"},
            {"action": "MoveTo", "target": [4, 4]},
            {"action": "Interact", "target": "serving_window"},
            {"action": "Finish"}
        ]
    }
}
```
"""