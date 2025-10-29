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
    "reasoning": "**Task Analysis:**\nWe need to prepare a basic burger that requires chopped and cooked meat, then combine the cooked meat with bread on a plate. Analyzing the map layout, this is an 8x6 kitchen with bread dispenser, meat dispenser, lettuce dispenser, tomato dispenser, and two chopping boards on the top row (y=0), and sink, table with plate, serving window, stove with pan, and other equipment on the bottom row (y=5).\n\n**Initial Agent Positions:**\n- agent1 is at (1,4), very close to the bread dispenser\n- agent2 is at (6,4), closer to the meat dispenser and chopping boards\n\n**Task Allocation Strategy:**\nConsidering the complexity of burger preparation, I decided to assign agent1 to handle the simple bread preparation task, while agent2 takes on the more complex meat processing tasks (chopping meat, cooking meat) as well as final burger assembly and serving. This division of labor maximizes the parallel working capability of both agents while avoiding conflicts at critical equipment.\n\n**Detailed Execution Plan:**\n\n**Agent1's Task Path (Bread Preparation):**\n1. Move from (1,4) to (1,1) to approach bread dispenser, distance 3, takes 3 time units, current time 3\n2. Interact with dispenser to get bread, interaction takes 0 time, current time 3\n3. Move to (3,4) to approach table with plate, distance 4, takes 4 time units, current time 7\n4. Place bread into the plate on table, interaction takes 0 time, current time 7\n\n**Agent2's Task Path (Meat Processing and Final Assembly):**\n1. Move from (6,4) to (2,1) to approach meat dispenser, distance 7, takes 7 time units, current time 7\n2. Interact with dispenser to get meat, interaction takes 0 time, current time 7\n3. Move to (5,1) to approach chopping board 1, distance 3, takes 3 time units, current time 10\n4. Place meat on chopping board 1, interaction takes 0 time, current time 10\n5. Process meat on chopping board 1, takes 4 time units, current time 14\n6. Pick up chopped meat, interaction takes 0 time, current time 14\n7. Move to (5,4) to approach stove, distance 3, takes 3 time units, current time 17\n8. Place chopped meat into pan on stove to start cooking, interaction takes 0 time, current time 17 (pan cooking takes 24 time units, expected completion at time 41)\n9. Move to (3,4) to approach table with plate, distance 2, takes 2 time units, current time 19\n10. Pick up the plate with bread, interaction takes 0 time, current time 19\n11. Move to (5,4) to approach stove, distance 2, takes 2 time units, current time 21\n12. Wait 20 time units until meat is cooked, current time 41\n13. Take cooked meat from pan and place into plate, interaction takes 0 time, current time 41\n14. Move to (4,4) to approach serving window, distance 1, takes 1 time unit, current time 42\n15. Submit completed burger at serving window, interaction takes 0 time, current time 42\n\n**Time Synchronization and Coordination:**\n- Agent1 completes bread preparation at time 7, exactly when agent2 has just obtained meat and starts processing\n- Agent2 needs to go through lengthy meat processing including chopping (4 time units) and cooking (24 time units)\n- During the meat cooking period, agent2 utilizes the waiting time to retrieve the plate with bread, making effective use of time\n- Agent2 completes final assembly at the exact moment when meat is cooked (time 41)\n\n**Optimization Considerations:**\n- Reasonable task division avoids resource competition, with agent1 focusing on simple tasks and agent2 handling complex tasks\n- Makes full use of meat cooking waiting time for other necessary operations\n- Total completion time is 42 time units, which is an efficient solution considering the 24 time unit constraint for pan cooking",
    "plan": {
        "agent1": [
            {"action": "MoveTo", "target": [1, 1]},
            {"action": "Interact", "target": "dispenser1"},
            {"action": "MoveTo", "target": [3, 4]},
            {"action": "Interact", "target": "table1"}
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
            {"action": "Interact", "target": "serving_window"}
        ]
    }
}
```
"""