input = """
Map JSON:
{
    "name": "kitchen_salad_8x6",
    "width": 8,
    "height": 6,
    "agents": [
        {"name": "agent1", "x": 1, "y": 4},
        {"name": "agent2", "x": 6, "y": 4}
    ],
    "tiles": [
        {"x": 0, "y": 0, "type": "obstacle", "name": "wall"},
        {"x": 1, "y": 0, "type": "station", "name": "dispenser1", "provides": "lettuce"},
        {"x": 2, "y": 0, "type": "station", "name": "dispenser2", "provides": "tomato"},
        {"x": 3, "y": 0, "type": "station", "name": "chopping_board1"},
        {"x": 4, "y": 0, "type": "station", "name": "chopping_board2"},
        {"x": 5, "y": 0, "type": "station", "name": "table1", "item": "plate"},
        {"x": 6, "y": 0, "type": "station", "name": "serving_window"},
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
        {"x": 3, "y": 5, "type": "station", "name": "table2"},
        {"x": 4, "y": 5, "type": "station", "name": "table3"},
        {"x": 5, "y": 5, "type": "station", "name": "table4"},
        {"x": 6, "y": 5, "type": "station", "name": "table5"},
        {"x": 7, "y": 5, "type": "obstacle", "name": "wall"}
    ]
}

Recipes:
- salad_advanced: Put chopped lettuce and chopped tomato together to a plate to make a salad.

Orders:
[salad_advanced]
"""

output = """
```json
{
    "reasoning": "**Task Analysis:**\nWe need to prepare a salad that requires chopped lettuce and chopped tomato placed on a plate. Analyzing the map layout, this is an 8x6 kitchen with lettuce dispenser, tomato dispenser, two chopping boards, a table with a plate, and serving window on the top row (y=0), and sink with several empty tables on the bottom row (y=5).\n\n**Initial Agent Positions:**\n- agent1 is at (1,4), closer to the lettuce dispenser\n- agent2 is at (6,4), closer to the tomato dispenser and chopping board 2\n\n**Task Allocation Strategy:**\nBased on the convenience of initial positions, I decided to assign agent1 to handle lettuce processing and final salad assembly/serving, while agent2 handles tomato processing. This avoids conflicts between the two agents in the same area and enables parallel work.\n\n**Detailed Execution Plan:**\n\n**Agent1's Task Path:**\n1. Move from (1,4) to (1,1) to approach lettuce dispenser, distance 3, takes 3 time units, current time 3\n2. Interact with dispenser to get lettuce, interaction takes 0 time, current time 3\n3. Move to (3,1) to approach chopping board 1, distance 2, takes 2 time units, current time 5\n4. Place lettuce on chopping board 1, interaction takes 0 time, current time 5\n5. Process lettuce on chopping board 1, takes 4 time units, current time 9\n6. Pick up chopped lettuce, interaction takes 0 time, current time 9\n7. Move to (5,1) to approach table with plate, distance 2, takes 2 time units, current time 11\n8. Place chopped lettuce into the plate on table, interaction takes 0 time, current time 11\n9. Pick up the plate with lettuce, interaction takes 0 time, current time 11\n10. Move to (4,1) to approach chopping board 2, distance 1, takes 1 time unit, current time 12\n11. Wait 1 time unit to ensure agent2 completes tomato chopping, current time 13\n12. Take chopped tomato from chopping board 2 and place into plate, interaction takes 0 time, current time 13\n13. Move to (6,1) to approach serving window, distance 2, takes 2 time units, current time 15\n14. Submit completed salad at serving window, interaction takes 0 time, current time 15\n\n**Agent2's Task Path:**\n1. Move from (6,4) to (2,1) to approach tomato dispenser, distance 7, takes 7 time units, current time 7\n2. Interact with dispenser to get tomato, interaction takes 0 time, current time 7\n3. Move to (4,1) to approach chopping board 2, distance 2, takes 2 time units, current time 9\n4. Place tomato on chopping board 2, interaction takes 0 time, current time 9\n5. Process tomato on chopping board 2, takes 4 time units, current time 13\n\n**Time Synchronization and Coordination:**\n- Agent1 completes lettuce chopping at time 9, while agent2 starts tomato chopping at the same time\n- Agent1 reaches chopping board 2 area at time 12, when agent2 is still chopping tomato (will finish at time 13)\n- Agent1 waits 1 time unit until time 13 to ensure agent2 completes tomato chopping\n- This design prevents both agents from competing for the same chopping board and achieves efficient parallel processing\n\n**Optimization Considerations:**\n- Utilizes both chopping boards for parallel processing, avoiding resource conflicts\n- Agent1 handles final salad assembly since it needs to process lettuce first, while agent2 focuses on tomato processing\n- Uses reasonable waiting time to ensure ingredient preparation synchronization\n- Total completion time is 15 time units, which is a relatively efficient solution",
    "plan": {
        "agent1": [
            {"action": "MoveTo", "target": [1, 1]},
            {"action": "Interact", "target": "dispenser1"},
            {"action": "MoveTo", "target": [3, 1]},
            {"action": "Interact", "target": "chopping_board1"},
            {"action": "Process", "target": "chopping_board1"},
            {"action": "Interact", "target": "chopping_board1"},
            {"action": "MoveTo", "target": [5, 1]},
            {"action": "Interact", "target": "table1"},
            {"action": "Interact", "target": "table1"},
            {"action": "MoveTo", "target": [4, 1]},
            {"action": "Wait", "duration": 1},
            {"action": "Interact", "target": "chopping_board2"},
            {"action": "MoveTo", "target": [6, 1]},
            {"action": "Interact", "target": "serving_window"}
        ],
        "agent2": [
            {"action": "MoveTo", "target": [2, 1]},
            {"action": "Interact", "target": "dispenser2"},
            {"action": "MoveTo", "target": [4, 1]},
            {"action": "Interact", "target": "chopping_board2"},
            {"action": "Process", "target": "chopping_board2"}
        ]
    }
}
```
"""