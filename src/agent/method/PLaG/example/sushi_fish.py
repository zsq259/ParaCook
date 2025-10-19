input = """
Map JSON:
{
    "name": "kitchen_sushi_8x6",
    "width": 8,
    "height": 6,
    "agents": [
        {"name": "agent1", "x": 1, "y": 4},
        {"name": "agent2", "x": 6, "y": 4}
    ],
    "tiles": [
        {"x": 0, "y": 0, "type": "obstacle", "name": "wall"},
        {"x": 1, "y": 0, "type": "station", "name": "dispenser1", "provides": "fish"},
        {"x": 2, "y": 0, "type": "station", "name": "dispenser2", "provides": "shrimp"},
        {"x": 3, "y": 0, "type": "station", "name": "dispenser3", "provides": "rice"},
        {"x": 4, "y": 0, "type": "station", "name": "dispenser4", "provides": "nori"},
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
        {"x": 5, "y": 5, "type": "station", "name": "stove", "item": "pot"},
        {"x": 6, "y": 5, "type": "station", "name": "table3"},
        {"x": 7, "y": 5, "type": "obstacle", "name": "wall"}
    ]
}

Recipes:
- sushi_fish: First chop the fish and cook the rice. Then put the chopped fish and cooked rice and a piece of nori on a plate to make a fish sushi.

Orders:
[sushi_fish]
"""

output = """
```json
{
    "reasoning": "**Task Analysis:**\nWe need to prepare a fish sushi that requires chopped fish and cooked rice, then combine the chopped fish, cooked rice, and a piece of nori on a plate. Analyzing the map layout, this is an 8x6 kitchen with fish dispenser, shrimp dispenser, rice dispenser, nori dispenser, and two chopping boards on the top row (y=0), and sink, table with plate, serving window, stove with pot, and other equipment on the bottom row (y=5).\n\n**Initial Agent Positions:**\n- agent1 is at (1,4), very close to the fish dispenser\n- agent2 is at (6,4), closer to the rice and nori dispensers\n\n**Task Allocation Strategy:**\nConsidering the complexity of sushi preparation, I assigned agent1 to handle fish processing (obtaining and chopping), while agent2 handles rice cooking and nori preparation, as well as final sushi assembly and serving. This division enables parallel processing, with agent2 taking on more time management responsibilities since rice cooking requires a longer duration (16 time units).\n\n**Dependency Graph Analysis:**\nThe sushi preparation has two major parallel processing chains:\n1. get_fish → chop_fish → place_fish_on_plate (agent1)\n2. get_rice → cook_rice (agent2)\nPlus a secondary chain:\n3. get_nori → combine with other ingredients (agent2)\nAll chains merge at final assembly:\n4. assemble_sushi (depends on chop_fish, cook_rice, get_nori) → serve_sushi\n\n**Critical Path Calculation:**\nPath 1 (agent1 - fish): get_fish(3) + move_to_chop1(4) + chop_fish(4) + move_to_plate(4) = 15 time units\nPath 2 (agent2 - rice): get_rice(7) + move_to_stove(6) + cook_rice(16) = 29 time units  \nPath 3 (agent2 - nori): get_nori(1) + move_to_plate(4) = 5 time units\nMerge point: max(15, 29, 5) = 29 time units\nFinal assembly + serve: move_to_stove(3) + wait_sync(8) + transfer_rice(0) + move_to_serving(1) + serve(0) = 12 time units\n\nCritical path: get_rice → cook_rice → transfer_rice_to_plate → serve_sushi = 7 + 6 + 16 + 3 + 8 + 0 + 1 + 0 = 41 time units\n\n**Detailed Execution Timeline:**\n\nAgent1's Task Path (Fish Processing):\n- Time 0-3: Move from (1,4) to (1,1), distance 3, takes 3 time units\n- Time 3: Interact with dispenser1 to get fish\n- Time 3-7: Move from (1,1) to (5,1), distance 4, takes 4 time units\n- Time 7: Interact with chopping_board1 to place fish\n- Time 7-11: Process (chop) fish on chopping_board1, takes 4 time units\n- Time 11: Interact with chopping_board1 to pick up chopped fish\n- Time 11-15: Move from (5,1) to (3,4), distance |5-3| + |1-4| = 2 + 3 = 5... recalculating: actually needs to be adjacent to table1, so move to (3,4) is distance 5, takes 5 time units. Let me correct: from (5,1) to (3,4) is |5-3| + |1-4| = 2 + 3 = 5, but we need an adjacent position. Table1 is at (3,5), so we approach from (3,4), distance from (5,1) is 5, takes 5 time units, current time 16\n- Time 16: Interact with table1 to place chopped fish on plate\n\nAgent2's Task Path (Rice Cooking, Nori Preparation, and Assembly):\n- Time 0-7: Move from (6,4) to (3,1), distance |6-3| + |4-1| = 3 + 3 = 6... recalculating: from (6,4) to (3,1) is |6-3| + |4-1| = 3 + 3 = 6, takes 6 time units, current time 6. Need to be adjacent to dispenser3 at (3,0), so approach from (3,1), distance is 6, takes 6 time units\n- Time 6: Interact with dispenser3 to get rice\n- Time 6-12: Move from (3,1) to (5,4), distance |3-5| + |1-4| = 2 + 3 = 5, but need to be adjacent to stove at (5,5), so approach from (5,4), distance is 5, takes 5 time units, current time 11\n- Time 11: Interact with stove to place rice in pot, cooking starts and takes 16 time units (completion at time 27)\n- Time 11-13: Move from (5,4) to (4,1), distance |5-4| + |4-1| = 1 + 3 = 4, takes 4 time units, current time 15\n- Time 15: Interact with dispenser4 to get nori\n- Time 15-19: Move from (4,1) to (3,4), distance |4-3| + |1-4| = 1 + 3 = 4, takes 4 time units, current time 19\n- Time 19: Interact with table1 to place nori on plate (plate already has fish from agent1)\n- Time 19: Interact with table1 to pick up plate with fish and nori\n- Time 19-23: Move from (3,4) to (5,4), distance 2, takes 2 time units, current time 21\n- Time 21-27: Wait 6 time units for rice to finish cooking (started at time 11, completes at time 27)\n- Time 27: Interact with stove to transfer cooked rice from pot to plate\n- Time 27-28: Move from (5,4) to (4,4), distance 1, takes 1 time unit, current time 28\n- Time 28: Interact with serving_window to submit completed sushi\n- Agent2 completes at time 28\n\n**Time Synchronization and Coordination:**\n- Agent1 completes fish chopping and places it on plate by time 16\n- Agent2 starts rice cooking at time 11, utilizing the cooking time (16 units) to obtain nori and combine ingredients\n- Agent2 reaches the table at time 19, after agent1 has placed fish, and adds nori to the plate\n- Agent2 picks up the plate with fish and nori, then waits at the stove for rice to complete cooking at time 27\n- Final assembly happens seamlessly: rice is transferred to plate with fish and nori, then immediately served\n- Total completion time: 28 time units\n\n**Optimization Considerations:**\n- Parallel processing of fish chopping and rice cooking eliminates idle time\n- Agent2 efficiently uses rice cooking wait time to obtain nori and perform ingredient combination\n- Minimal redundant movements through careful routing\n- Both agents work simultaneously with complementary tasks, maximizing throughput\n- Strategic plate pickup timing ensures all ingredients are ready for final assembly when rice finishes cooking",
    "graph": {
        "START": ["get_fish", "get_rice"],
        "get_fish": ["move_to_chop_fish"],
        "move_to_chop_fish": ["chop_fish"],
        "chop_fish": ["pick_fish"],
        "pick_fish": ["move_to_plate_fish"],
        "move_to_plate_fish": ["place_fish_on_plate"],
        "get_rice": ["move_to_stove"],
        "move_to_stove": ["cook_rice"],
        "cook_rice": ["wait_for_rice"],
        "place_fish_on_plate": ["get_nori"],
        "get_nori": ["move_to_plate_nori"],
        "move_to_plate_nori": ["place_nori_on_plate"],
        "place_nori_on_plate": ["pick_plate"],
        "pick_plate": ["move_back_to_stove"],
        "move_back_to_stove": ["wait_for_rice"],
        "wait_for_rice": ["transfer_rice_to_plate"],
        "transfer_rice_to_plate": ["move_to_serving"],
        "move_to_serving": ["serve_sushi"],
        "serve_sushi": ["END"],
        "END": []
    },
    "time_dict": {
        "START": 0,
        "get_fish": 3,
        "move_to_chop_fish": 4,
        "chop_fish": 4,
        "pick_fish": 0,
        "move_to_plate_fish": 5,
        "place_fish_on_plate": 0,
        "get_rice": 6,
        "move_to_stove": 5,
        "cook_rice": 16,
        "get_nori": 0,
        "move_to_plate_nori": 4,
        "place_nori_on_plate": 0,
        "pick_plate": 0,
        "move_back_to_stove": 2,
        "wait_for_rice": 6,
        "transfer_rice_to_plate": 0,
        "move_to_serving": 1,
        "serve_sushi": 0,
        "END": 0
    },   
    "plan": {
        "agent1": [
            {"action": "MoveTo", "target": [1, 1]},
            {"action": "Interact", "target": "dispenser1"},
            {"action": "MoveTo", "target": [5, 1]},
            {"action": "Interact", "target": "chopping_board1"},
            {"action": "Process", "target": "chopping_board1"},
            {"action": "Interact", "target": "chopping_board1"},
            {"action": "MoveTo", "target": [3, 4]},
            {"action": "Interact", "target": "table1"},
            {"action": "Finish"}
        ],
        "agent2": [
            {"action": "MoveTo", "target": [3, 1]},
            {"action": "Interact", "target": "dispenser3"},
            {"action": "MoveTo", "target": [5, 4]},
            {"action": "Interact", "target": "stove"},
            {"action": "MoveTo", "target": [4, 1]},
            {"action": "Interact", "target": "dispenser4"},
            {"action": "MoveTo", "target": [3, 4]},
            {"action": "Interact", "target": "table1"},
            {"action": "Interact", "target": "table1"},
            {"action": "MoveTo", "target": [5, 4]},
            {"action": "Wait", "duration": 6},
            {"action": "Interact", "target": "stove"},
            {"action": "MoveTo", "target": [4, 4]},
            {"action": "Interact", "target": "serving_window"},
            {"action": "Finish"}
        ]
    }
}
```
"""