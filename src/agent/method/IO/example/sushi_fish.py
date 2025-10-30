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
['sushi_fish: First chop the fish and cook the rice. Then put the chopped fish and cooked rice and a piece of nori on a plate to make a fish sushi.']

Orders:
['sushi_fish']
"""

output = """
```json
{
    "agent1": [
        {"action": "MoveTo", "target": [1, 1]},
        {"action": "Interact", "target": "dispenser1"},
        {"action": "MoveTo", "target": [5, 1]},
        {"action": "Interact", "target": "chopping_board1"},
        {"action": "Process", "target": "chopping_board1"},
        {"action": "Interact", "target": "chopping_board1"},
        {"action": "MoveTo", "target": [3, 4]},
        {"action": "Interact", "target": "table1"}
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
        {"action": "Wait", "duration": 8},
        {"action": "Interact", "target": "stove"},
        {"action": "MoveTo", "target": [4, 4]},
        {"action": "Interact", "target": "serving_window"}
    ]
}
```
"""