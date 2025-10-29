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
```
"""