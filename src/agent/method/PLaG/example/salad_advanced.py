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
    "reasoning": "**Task Analysis:**\nWe need to prepare a salad that requires chopped lettuce and chopped tomato placed on a plate. Analyzing the map layout, this is an 8x6 kitchen with lettuce dispenser, tomato dispenser, two chopping boards, a table with a plate, and serving window on the top row (y=0), and sink with several empty tables on the bottom row (y=5).\n\n**Initial Agent Positions:**\n- agent1 is at (1,4), closer to the lettuce dispenser\n- agent2 is at (6,4), closer to the tomato dispenser and chopping board 2\n\n**Task Allocation Strategy:**\nBased on the convenience of initial positions, I decided to assign agent1 to handle lettuce processing and final salad assembly/serving, while agent2 handles tomato processing. This avoids conflicts between the two agents in the same area and enables parallel work.\n\n**Dependency Graph Analysis:**\nThe salad preparation has two parallel processing chains that merge at assembly:\n1. get_lettuce → chop_lettuce → prepare_lettuce_on_plate (agent1)\n2. get_tomato → chop_tomato (agent2)\nBoth chains must complete before final assembly and serving:\n3. assemble_salad (depends on both chains) → serve_salad\n\n**Critical Path Calculation:**\nPath 1 (agent1 - lettuce): get_lettuce(3) + move_to_chop1(2) + chop_lettuce(4) + move_to_plate(2) + place_lettuce(0) = 11 time units\nPath 2 (agent2 - tomato): get_tomato(7) + move_to_chop2(2) + chop_tomato(4) = 13 time units\nPath 3 (merge + assembly): max(11, 13) + wait_sync(0) + get_tomato_from_board(0) + serve(2) = 15 time units\n\nCritical path: get_tomato → chop_tomato → assemble_salad → serve_salad = 7 + 2 + 4 + 0 + 0 + 2 + 0 = 15 time units\n\n**Detailed Execution Timeline:**\n\nAgent1's Task Path (Lettuce Processing and Assembly):\n- Time 0-3: Move from (1,4) to (1,1), distance 3, takes 3 time units\n- Time 3: Interact with dispenser1 to get lettuce\n- Time 3-5: Move from (1,1) to (3,1), distance 2, takes 2 time units\n- Time 5: Interact with chopping_board1 to place lettuce\n- Time 5-9: Process (chop) lettuce on chopping_board1, takes 4 time units\n- Time 9: Interact with chopping_board1 to pick up chopped lettuce\n- Time 9-11: Move from (3,1) to (5,1), distance 2, takes 2 time units\n- Time 11: Interact with table1 to place chopped lettuce on plate\n- Time 11: Interact with table1 to pick up plate with lettuce\n- Time 11-12: Move from (5,1) to (4,1), distance 1, takes 1 time unit\n- Time 12-13: Wait 1 time unit for agent2 to complete tomato chopping\n- Time 13: Interact with chopping_board2 to transfer chopped tomato to plate\n- Time 13-15: Move from (4,1) to (6,1), distance 2, takes 2 time units\n- Time 15: Interact with serving_window to submit completed salad\n- Agent1 completes at time 15\n\nAgent2's Task Path (Tomato Processing):\n- Time 0-7: Move from (6,4) to (2,1), distance |6-2| + |4-1| = 4 + 3 = 7, takes 7 time units\n- Time 7: Interact with dispenser2 to get tomato\n- Time 7-9: Move from (2,1) to (4,1), distance 2, takes 2 time units\n- Time 9: Interact with chopping_board2 to place tomato\n- Time 9-13: Process (chop) tomato on chopping_board2, takes 4 time units\n- Agent2 completes chopping at time 13 (waits for agent1 to pick up)\n\n**Time Synchronization and Coordination:**\n- Agent2 completes tomato chopping at time 13\n- Agent1 reaches chopping_board2 at time 12 and waits 1 time unit\n- At time 13, agent1 retrieves the chopped tomato and adds it to the plate\n- Both agents achieve efficient parallel processing with minimal idle time\n- Total completion time: 15 time units\n\n**Optimization Considerations:**\n- Utilizes both chopping boards for parallel processing, avoiding resource conflicts\n- Agent1 handles both lettuce processing and final salad assembly since it finishes lettuce first\n- Agent2 focuses on tomato processing, which takes longer due to travel distance\n- Strategic waiting at time 12-13 ensures proper synchronization without resource conflicts\n- Achieves near-optimal parallelism by keeping both agents working simultaneously",
    "graph": {
        "START": ["get_lettuce", "get_tomato"],
        "get_lettuce": ["move_to_chop1"],
        "move_to_chop1": ["chop_lettuce"],
        "chop_lettuce": ["pick_lettuce"],
        "pick_lettuce": ["move_to_plate"],
        "move_to_plate": ["place_lettuce_on_plate"],
        "place_lettuce_on_plate": ["pick_plate"],
        "get_tomato": ["move_to_chop2"],
        "move_to_chop2": ["chop_tomato"],
        "chop_tomato": ["wait_for_sync"],
        "pick_plate": ["wait_for_sync"],
        "wait_for_sync": ["get_tomato_from_board"],
        "get_tomato_from_board": ["move_to_serving"],
        "move_to_serving": ["serve_salad"],
        "serve_salad": ["END"],
        "END": []
    },
    "time_dict": {
        "START": 0,
        "get_lettuce": 3,
        "move_to_chop1": 2,
        "chop_lettuce": 4,
        "pick_lettuce": 0,
        "move_to_plate": 2,
        "place_lettuce_on_plate": 0,
        "pick_plate": 0,
        "get_tomato": 7,
        "move_to_chop2": 2,
        "chop_tomato": 4,
        "wait_for_sync": 1,
        "get_tomato_from_board": 0,
        "move_to_serving": 2,
        "serve_salad": 0,
        "END": 0
    },
    
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
            {"action": "Interact", "target": "serving_window"},
            {"action": "Finish"}
        ],
        "agent2": [
            {"action": "MoveTo", "target": [2, 1]},
            {"action": "Interact", "target": "dispenser2"},
            {"action": "MoveTo", "target": [4, 1]},
            {"action": "Interact", "target": "chopping_board2"},
            {"action": "Process", "target": "chopping_board2"},
            {"action": "Finish"}
        ]
    }
}
```
"""