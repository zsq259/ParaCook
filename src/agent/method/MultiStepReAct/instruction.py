INSTRUCTION = """
Based on the input map JSON, recipes and orders, combined with the following Overcooked multi-agent parallel planning rules, to output a detailed action plan for guiding each agent to complete dish preparation. The action plan must strictly follow the format and constraints.

## 1. Core Principles
Your planning must always be guided by these three principles:
- **Maximize Efficiency**: Minimize the total time required to complete all orders. This is the most critical goal.
- **Maximize Parallelism**: Ensure multiple agents are working simultaneously whenever possible to reduce idle time.
- **Ensure Accuracy**: Adhere 100% to all action definitions, rules, and constraints outlined below.

## 2. Input Content
- **Map JSON**: Describes kitchen layout, station coordinates, initial items, and agent positions.
- **Recipes**: Describes the preparation workflow and required ingredients for the dishes.
- **Orders**: Describe the dishes that need to be completed in order.

## 3. Output Requirements
- For each agent, thought about the environment and output a sequence of one or more actions (the number of actions is decided by yourself), then wait for the next observation, and repeat this process until all orders are completed.
- **DO NOT** try to plan the entire workflow from start to finish in one turn
- Each action is a dictionary containing action type and parameters. Detailed action definitions are provided in Section 5.
Please think step by step and first explain your reasoning process in detail using natural language, including task allocation, key operation sequences, collaboration details, and time arrangement. After the reasoning, output the standard JSON format action without any additional explanations or content.

Here is the output format example:

```json
{{
    "reasoning": "...",
    "plan": {{
        "agent1": [
          {{"action": "MoveTo", "target": [x1, y1]}},
          {{"action": "Interact", "target": "station_name1"}},
          {{"action": "MoveTo", "target": [x2, y2]}},
          {{"action": "Process", "target": "station_name2"}},
          ...
        ],
        "agent2": [
          {{"action": "MoveTo", "target": [x3, y3]}},
          {{"action": "Interact", "target": "station_name3"}},
          {{"action": "Wait", "duration": t}},
          ...
        ],
        ...
    }}
}}
```
You must strictly follow the above format without any additional explanations or annotations.

## 4. Environment Rules and Constraints
This is the most important section. All rules must be strictly followed.
**Agent Rules**
- No Collision: Agents do **not** consider collision boxes between each other; their movement paths and positions can overlap at any time.
- Single Item Hold: An agent can only hold one item at a time (e.g., an ingredient, a plate, a pot). Item exchange must be done via surfaces like tables; direct passing is not allowed. Cannot hold multiple ingredients or containers at once.
- Positioning: Agents can only stand on empty floor tiles; actions must be performed on adjacent empty ground to target stations; movement can only occur through empty ground. In summary, at any time, an agent's coordinates can **never** overlap with a station's coordinates.
- Agents can only interact or process with workstations that are adjacent in the four cardinal directions (up, down, left, right).
**Environment & Item Rules**
- Station Exclusivity: Fixed stations like cutting boards or sinks can only be used by one agent at a time for a Process action.
- Ingredient Dispensing: Ingredients can only be obtained from designated dispensers. Each dispenser provides a specific type of ingredient. All types of ingredients can be directly held without the need for additional containers.
- Cooking Process:
  - Stoves can only hold cookware (pots/pans), not ingredients directly.
  - Cooking starts automatically once cookware is placed on a stove and contains ingredients. Picking it up pauses cooking; placing it back on any stove resumes it.
  - Cooked food cannot be picked up by hand; it must be transferred in a container.
- Serving Process:
  - All food items must be placed on a plate before being submitted at the serving window. The order in which the ingredients are placed on the plate is not important.
  - Dishes must be served in the exact order specified in the Orders list.
- Plate Cycle:
  - Dirty plates return to the dirty plate return station some time after a dish is served.
  - A dirty plate cannot hold any items and must be washed at a sink to become a clean plate.
- About time consumption:
    - Moving to an adjacent tile costs 1 time unit. Total time is proportional to the distance.
    - Interact: {INTERACT_TIME} time unit
    - Chopping: {PROCESS_CUT_TIME} time units
    - Pot Cooking: {PROCESS_POT_COOK_TIME} time units
    - Pan Cooking: {PROCESS_PAN_COOK_TIME} time units
    - Washing Plates: {PROCESS_WASH_PLATE_TIME} time units
    - Dirty Plate Return: {RETURN_DIRTY_PLATE_TIME} time units

## 5. Action Definitions
- **MoveTo(coordinate)**:
  - format: `{{"action": "MoveTo", "target": [x, y]}}`
  - Move to the target empty floor coordinate.
  - Agent can move directly to any reachable empty floor tile in one step, without needing to execute each move step to adjacent tiles. Just calculate the total distance and consume time proportionally.
  - The path must only go through empty floor tiles.
  - Important: Agent should directly moves to an empty tile adjacent to the target station, not the station's own tile. Always check if the target is empty.
- **Interact(target_name)**:
  - format: `{{"action": "Interact", "target": "station_name"}}`
  - Interact with an adjacent station. The outcome depends on the agent's and station's state:
  - With a regular counter(Table):
    - If one of hand or table is empty and the other has an item (ingredient/container): Pick up or place down the item.
    - If both hand and counter hold items:
      - If one is a container (pot/plate) and the other is an ingredient: Add the ingredient to the container. The container's location does not change.
      - If both are containers: The contents of the held container are transferred to the plate. Both containers remain in their original positions. For example, if holding a pot with rice and interacting with a table with a plate, the rice will be placed into the plate, the pot remains in hand, and the plate remains on the table.
    - Note: Ingredients already in a plate cannot be moved out; they can only be added to an another plate or discarded to trash.
  - With an Ingredient Dispenser: 
    - If empty-handed and the top is free, take a raw ingredient from the box. Ingredients can only be taken when empty-handed and there is no item on top of the dispenser.
    - If holding an item (ingredient or container), agent will put the item down on the top of the dispenser if it's free.
    - Otherwise, follow the same rules as with regular counters.
  - With a Stove:
    - Ingredients cannot be placed directly on the stove.
    - If a cookware is at the stove or in hand, follow the same rules as with regular counters.
    - Some examples:
      - If empty-handed and the stove has a pot: Pick up the pot.
      - If holding a pot and the stove is empty: Place the pot on the stove.
      - If holding a ingredient and the stove has a pot: Add the ingredient to the pot.
      - If holding a plate and the stove has a pot: Transfer the pot's contents to the plate. The pot remains on the stove, and the plate remains in hand.
  - With the Serving Window: Submit the completed dish on a plate.
  - With a Trash Bin: Dispose of the held item or empty the held container.
  - With the Dirty Plate Return: Items cannot be placed here; only one dirty plate can be picked up at a time with empty hands (if a dirty plate is available).
  - With a Sink:
    - If holding a dirty plate: Place it in the sink to be washed (if the sink is free).
    - If empty-handed: Pick up a clean plate (if one is ready).
- **Process(target_name)**:
  - format: `{{"action": "Process", "target": "station_name"}}`
  - Perform a continuous action at a station (e.g., chopping, washing).
  - Note: A stove cannot be the target of a Process action. Cooking operations start automatically when cooking equipment (pots/ pans) containing ingredients is placed on the stove.
- **Wait(duration)**:
  - format: `{{"action": "Wait", "duration": t}}`
  - Remain idle at the current position for t time units.
- **Finish()**:
  - format: `{{"action": "Finish"}}`
  - Indicates the agent has completed all its tasks and will take no further actions.

## 6. Suggestions
- Tasks must be reasonably allocated to achieve multi-agent parallel collaboration and minimize total time consumption.
- Action sequence must completely cover the entire process from raw material acquisition, processing, assembly to serving.
- Always notice the timepoint when each action starts and ends to ensure no conflicts in agent actions and get the most efficient plan.
- You can flexibly decide how many actions to output for each agent in each turn, according to the current situation and planning needs. 
- Do not output too many actions at once if you are not sure about the future situation. You can output less actions and wait for the next observation to adjust your plan.

Please combine the map layout and recipe workflow to reasonably arrange each operation step and collaboration details, outputting standard actions.

Here is an example of some steps:

Turn 1:
User Input:
Map JSON:
{{
    "name": "kitchen_salad_8x6",
    "width": 8,
    "height": 6,
    "agents": [
        {{"name": "agent1", "x": 1, "y": 4}},
        {{"name": "agent2", "x": 6, "y": 4}}
    ],
    "tiles": [
        {{"x": 0, "y": 0, "type": "obstacle", "name": "wall"}},
        {{"x": 1, "y": 0, "type": "station", "name": "dispenser1", "provides": "lettuce"}},
        {{"x": 2, "y": 0, "type": "station", "name": "dispenser2", "provides": "tomato"}},
        {{"x": 3, "y": 0, "type": "station", "name": "chopping_board1"}},
        {{"x": 4, "y": 0, "type": "station", "name": "chopping_board2"}},
        {{"x": 5, "y": 0, "type": "station", "name": "table1", "item": "plate"}},
        {{"x": 6, "y": 0, "type": "station", "name": "serving_window"}},
        {{"x": 7, "y": 0, "type": "obstacle", "name": "wall"}},
        {{"x": 0, "y": 1, "type": "obstacle", "name": "wall"}},
        {{"x": 7, "y": 1, "type": "obstacle", "name": "wall"}},
        {{"x": 0, "y": 2, "type": "obstacle", "name": "wall"}},
        {{"x": 7, "y": 2, "type": "obstacle", "name": "wall"}},
        {{"x": 0, "y": 3, "type": "obstacle", "name": "wall"}},
        {{"x": 7, "y": 3, "type": "obstacle", "name": "wall"}},
        {{"x": 0, "y": 4, "type": "obstacle", "name": "wall"}},
        {{"x": 7, "y": 4, "type": "obstacle", "name": "wall"}},
        {{"x": 0, "y": 5, "type": "obstacle", "name": "wall"}},
        {{"x": 1, "y": 5, "type": "station", "name": "sink"}},
        {{"x": 2, "y": 5, "type": "station", "name": "plate_return"}},
        {{"x": 3, "y": 5, "type": "station", "name": "table2"}},
        {{"x": 4, "y": 5, "type": "station", "name": "table3"}},
        {{"x": 5, "y": 5, "type": "station", "name": "table4"}},
        {{"x": 6, "y": 5, "type": "station", "name": "table5"}},
        {{"x": 7, "y": 5, "type": "obstacle", "name": "wall"}}
    ]
}}

Recipes:
- salad_advanced: Put chopped lettuce and chopped tomato together to a plate to make a salad.

Orders:
[salad_advanced]

Model Output:
```json
{{
    "reasoning": "The order requires a salad_advanced, which needs chopped lettuce and chopped tomato on a plate. To maximize efficiency and parallelism, I assign agent1 to collect lettuce and agent2 to collect tomato. Agents are not allowed to stand on station tiles, so each agent must move to an empty floor tile adjacent to its assigned dispenser in order to Interact. The lettuce dispenser is located at (1,0), so agent1 should move to the adjacent tile at (1,1) in order to interact with it. Similarly, the tomato dispenser is at (2,0), and agent2 should move to the adjacent tile at (2,1). This allocation ensures each agent is positioned optimally to pick up the correct ingredient, preparing for the chopping step next.",
    "plan": {{
        "agent1": [
          {{"action": "MoveTo", "target": [1, 1]}},
          {{"action": "Interact", "target": "dispenser1"}},
        ],
        "agent2": [
          {{"action": "MoveTo", "target": [2, 1]}},
          {{"action": "Interact", "target": "dispenser2"}},
        ],
    }}
}}
```

Turn 2:
User Input:
Observation:
Current time: 3
Agent agent1: vacant (remaining actions: 0)
Agent agent2: executing {{'action': 'MoveTo', 'target': [2, 1]}} (finish at: 7, remaining actions: 1)

Current World State:
{{'width': 8, 'height': 6, 'agents': [{{'name': 'agent1', 'x': 1, 'y': 1, 'holding': {{'name': 'lettuce', 'state': 'raw'}}}}, {{'name': 'agent2', 'x': 6, 'y': 4, 'holding': None}}], 'tiles': [{{'name': 'wall', 'type': 'obstacle', 'x': 7, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'dispenser1', 'type': 'station', 'x': 1, 'y': 0, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'dispenser2', 'type': 'station', 'x': 2, 'y': 0, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'chopping_board1', 'type': 'station', 'x': 3, 'y': 0, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'chopping_board2', 'type': 'station', 'x': 4, 'y': 0, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'table1', 'type': 'station', 'x': 5, 'y': 0, 'item': {{'name': 'plate', 'type': 'container', 'contents': []}}, 'in_use': False, 'current_user': None}}, {{'name': 'serving_window', 'type': 'station', 'x': 6, 'y': 0, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'sink', 'type': 'station', 'x': 1, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'plate_return', 'type': 'station', 'x': 2, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'table2', 'type': 'station', 'x': 3, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'table3', 'type': 'station', 'x': 4, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'table4', 'type': 'station', 'x': 5, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'table5', 'type': 'station', 'x': 6, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}]}}

Model Output:
```json
{{
    "reasoning": "Current time is 3. Observation shows agent1 is at (1,1) holding raw lettuce, while agent2 is still executing MoveTo to (2,1) and will finish that move at time 7. The chopping stations are at (3,0) and (4,0); agents cannot stand on station tiles, so valid interaction tiles are (3,1) and (4,1). Chopping board 1 is free at this moment. To maximize parallelism and avoid idle time, agent1 should proceed immediately to prepare the lettuce rather than wait for agent2. Concretely, agent1 should MoveTo (3,1) (Manhattan distance 2 → move duration 2, finishing at time 5), then Interact with chopping_board1 to place the raw lettuce on the board, and then start Process on chopping_board1 for 4 units. This sequence occupies chopping_board1 from time 5 to time 9 and will overlap with agent2's arrival at the tomato dispenser (finish move at time 7) and subsequent actions, achieving parallel chopping while respecting station exclusivity and the rule that agents must interact from adjacent tiles.",
    "plan": {{
        "agent1": [
          {{"action": "MoveTo", "target": [3, 1]}},
          {{"action": "Interact", "target": "chopping_board1"}},
          {{"action": "Process", "target": "chopping_board1"}},
        ],
    }}
}}
```

Turn 3:
User Input:
Observation:
Current time: 7
Agent agent1: executing {{'action': 'Process', 'target': 'chopping_board1'}} (finish at: 9, remaining actions: 0)
Agent agent2: vacant (remaining actions: 0)

Current World State:
{{'width': 8, 'height': 6, 'agents': [{{'name': 'agent1', 'x': 3, 'y': 1, 'holding': None}}, {{'name': 'agent2', 'x': 2, 'y': 1, 'holding': {{'name': 'tomato', 'state': 'raw'}}}}], 'tiles': [{{'name': 'wall', 'type': 'obstacle', 'x': 7, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'dispenser1', 'type': 'station', 'x': 1, 'y': 0, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'dispenser2', 'type': 'station', 'x': 2, 'y': 0, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'chopping_board1', 'type': 'station', 'x': 3, 'y': 0, 'item': {{'name': 'lettuce', 'state': 'raw'}}, 'in_use': True, 'current_user': 'agent1'}}, {{'name': 'chopping_board2', 'type': 'station', 'x': 4, 'y': 0, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'table1', 'type': 'station', 'x': 5, 'y': 0, 'item': {{'name': 'plate', 'type': 'container', 'contents': []}}, 'in_use': False, 'current_user': None}}, {{'name': 'serving_window', 'type': 'station', 'x': 6, 'y': 0, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'sink', 'type': 'station', 'x': 1, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'plate_return', 'type': 'station', 'x': 2, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'table2', 'type': 'station', 'x': 3, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'table3', 'type': 'station', 'x': 4, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'table4', 'type': 'station', 'x': 5, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'table5', 'type': 'station', 'x': 6, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}]}}

Model Output:
```json
{{
    "reasoning": "Current time is 7. At this point, agent1 is still processing the lettuce on chopping_board1 and will remain occupied until 9, so it cannot take on new actions yet. Agent2 has arrived at (2,1), adjacent to the tomato dispenser at (2,0), and is ready to collect tomato. The tomato then needs to be chopped, and chopping_board2 at (4,0) (accessible from (4,1)) is currently free. To maximize efficiency and parallelism, agent2 should first Interact with the tomato dispenser to pick up raw tomato, then MoveTo (4,1), which is the adjacent floor tile to chopping_board2, and finally Interact with the board to place the tomato and begin the chopping process. This ensures both chopping boards are utilized simultaneously, preventing idle time and aligning with the requirement for salad_advanced.",
    "plan": {{
        "agent2": [
          {{"action": "MoveTo", "target": [4, 1]}},
          {{"action": "Interact", "target": "chopping_board2"}},
          {{"action": "Process", "target": "chopping_board2"}},
        ],
    }}
}}
```

Turn 4:
User Input:
Observation:
Current time: 9
Agent agent1: vacant (remaining actions: 0)
Agent agent2: executing {{'action': 'Process', 'target': 'chopping_board2'}} (finish at: 13, remaining actions: 0)

Current World State:
{{'width': 8, 'height': 6, 'agents': [{{'name': 'agent1', 'x': 3, 'y': 1, 'holding': None}}, {{'name': 'agent2', 'x': 4, 'y': 1, 'holding': None}}], 'tiles': [{{'name': 'wall', 'type': 'obstacle', 'x': 7, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'dispenser1', 'type': 'station', 'x': 1, 'y': 0, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'dispenser2', 'type': 'station', 'x': 2, 'y': 0, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'chopping_board1', 'type': 'station', 'x': 3, 'y': 0, 'item': {{'name': 'lettuce', 'state': 'chopped'}}, 'in_use': False, 'current_user': None}}, {{'name': 'chopping_board2', 'type': 'station', 'x': 4, 'y': 0, 'item': {{'name': 'tomato', 'state': 'raw'}}, 'in_use': True, 'current_user': 'agent2'}}, {{'name': 'table1', 'type': 'station', 'x': 5, 'y': 0, 'item': {{'name': 'plate', 'type': 'container', 'contents': []}}, 'in_use': False, 'current_user': None}}, {{'name': 'serving_window', 'type': 'station', 'x': 6, 'y': 0, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'sink', 'type': 'station', 'x': 1, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'plate_return', 'type': 'station', 'x': 2, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'table2', 'type': 'station', 'x': 3, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'table3', 'type': 'station', 'x': 4, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'table4', 'type': 'station', 'x': 5, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'table5', 'type': 'station', 'x': 6, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}]}}

Model Output:
```json
{{
    "reasoning": "Current time is 9. Agent1 has finished processing the lettuce on chopping_board1 and is currently empty-handed at (3,1). Agent2 is still processing tomato on chopping_board2 and will finish at time 13. To prepare for plating once agent2 finishes, agent1 should first Interact with chopping_board1 to pick up the chopped lettuce. According to the Interact rules, when interacting with a table that already has a plate while holding an ingredient, the ingredient is added to the plate without moving the plate. Therefore, agent1 can then MoveTo (5,1), adjacent to table1 where a plate is available, and Interact with table1 twice: the first Interact places the chopped lettuce onto the plate, the second Interact picks up the plate. Since Interact takes negligible time and agents can stand on the same tile, agent1 can then Wait at (4,1) until agent2 finishes processing the tomato. This sequence ensures that agent1 is ready to combine both ingredients onto the plate immediately after agent2 completes, maximizing parallelism and minimizing total time.",
    "plan": {{
        "agent1": [
          {{"action": "Interact", "target": "chopping_board1"}},
          {{"action": "MoveTo", "target": [5, 1]}},
          {{"action": "Interact", "target": "table1"}},
          {{"action": "Interact", "target": "table1"}},
          {{"action": "MoveTo", "target": [4, 1]}},
          {{"action": "Wait", "duration": 1}},
        ],
    }}
}}
```

Turn 5:
User Input:
Observation:
Current time: 13
Agent agent1: vacant (remaining actions: 0)
Agent agent2: vacant (remaining actions: 0)

Current World State:
{{'width': 8, 'height': 6, 'agents': [{{'name': 'agent1', 'x': 4, 'y': 1, 'holding': {{'name': 'plate', 'type': 'container', 'contents': [{{'name': 'lettuce', 'state': 'chopped'}}]}}}}, {{'name': 'agent2', 'x': 4, 'y': 1, 'holding': None}}], 'tiles': [{{'name': 'wall', 'type': 'obstacle', 'x': 7, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'dispenser1', 'type': 'station', 'x': 1, 'y': 0, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'dispenser2', 'type': 'station', 'x': 2, 'y': 0, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'chopping_board1', 'type': 'station', 'x': 3, 'y': 0, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'chopping_board2', 'type': 'station', 'x': 4, 'y': 0, 'item': {{'name': 'tomato', 'state': 'chopped'}}, 'in_use': False, 'current_user': None}}, {{'name': 'table1', 'type': 'station', 'x': 5, 'y': 0, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'serving_window', 'type': 'station', 'x': 6, 'y': 0, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'sink', 'type': 'station', 'x': 1, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'plate_return', 'type': 'station', 'x': 2, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'table2', 'type': 'station', 'x': 3, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'table3', 'type': 'station', 'x': 4, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'table4', 'type': 'station', 'x': 5, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}, {{'name': 'table5', 'type': 'station', 'x': 6, 'y': 5, 'item': None, 'in_use': False, 'current_user': None}}]}}

Model Output:
```json
{{
    "reasoning": "Current time is 13. Agent1 is holding a plate containing chopped lettuce at (4,1). Agent2 has finished processing the tomato and is empty-handed at (4,1). To complete the salad_advanced order, agent1 needs to combine the chopped tomato with the plate containing lettuce and then deliver the completed dish to the serving_window. According to the Interact rules, when interacting with a table that holds an ingredient while holding a plate, the ingredient is added to the plate without moving the plate. Therefore, agent1 only need to Interact with chopping_board2 and can derectly add the chopped tomato to the plate. Then, agent1 should MoveTo (6,1), adjacent to the serving_window, and Interact with the serving_window to submit the completed salad. Finally, agent1 can finish. Agent2 has no further tasks and can directly Finish. This plan ensures that the order is completed efficiently and follows all environment and interaction rules.",
    "plan": {{
        "agent1": [
          {{"action": "Interact", "target": "chopping_board2"}},
          {{"action": "MoveTo", "target": [6, 1]}},
          {{"action": "Interact", "target": "serving_window"}},
          {{"action": "Finish"}}
        ],
        "agent2": [
          {{"action": "Finish"}}
        ],
    }}
}}
```
"""

REFINE_INSTRUCTION = """
Your previous action plan occurred an error during simulation: {error}. 
Here is the world state when the error occurred:
{world_json}
Please think step by step and first analyze the error, then refine your previous action plan to avoid this error while still following all the rules and constraints.
You can adjust the number of actions you output for each agent in this turn according to the current situation and planning needs. Do not output too many actions at once if you are meeting errors.
The current plan should be a correction to the plan you provided last time, based on the previous observation, rather than the world state at the time of the error.
Remember to strictly check all actions in your previous plan to ensure they are all valid and prevent similar errors from happening again.
Output format:

```json
{{
    "reasoning": "...",
    "plan": ...
}}
```
"""