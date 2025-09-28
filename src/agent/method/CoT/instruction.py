INSTRUCTION = """
Based on the input map JSON, recipes and orders, combined with the following Overcooked multi-agent parallel planning rules, to output a detailed action plan (Action List) for guiding each agent to complete dish preparation. The action plan must strictly follow the format and constraints.

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
- For each agent, output an ordered action list (e.g., agent1, agent2).
- Each action is a dictionary containing action type and parameters. Detailed action definitions are provided in Section 5.
Please think step by step and first explain your reasoning process in detail using natural language, including task allocation, key operation sequences, collaboration details, and time arrangement. After the reasoning, output the standard JSON format action list without any additional explanations or content.

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
    - If empty-handed and the top is free, take a raw ingredient from the box.
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

## 6. Suggestions
- Tasks must be reasonably allocated to achieve multi-agent parallel collaboration and minimize total time consumption.
- Action sequence must completely cover the entire process from raw material acquisition, processing, assembly to serving.
- Always notice the timepoint when each action starts and ends to ensure no conflicts in agent actions and get the most efficient plan.

Please combine the map layout and recipe workflow to reasonably arrange each operation step and collaboration details, outputting a standard action list.
"""

REFINE_INSTRUCTION = """
Your previous action plan occurred an error during simulation: {error}. 
Here is the world state when the error occurred:
{world_json}
Please think step by step and first analyze the error, then refine your previous action plan to avoid this error while still following all the rules and constraints.
Remember to strictly check all actions in your previous plan to ensure they are all valid and prevent similar errors from happening again.
Output format:

```json
{{
    "reasoning": "...",
    "plan": ...
}}
```
"""