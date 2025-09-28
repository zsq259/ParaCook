INSTRUCTION = """
Based on the input map JSON, recipes and orders, combined with the following Overcooked multi-agent parallel planning rules, to output a detailed action plan (Action List) for guiding each agent to complete dish preparation. The action plan must strictly follow the format and constraints.

## 1. Input Content
- **Map JSON**: Describes kitchen layout, station coordinates, initial items, and agent positions.
- **Recipes**: Describes the preparation workflow and required ingredients for the dishes.
- **Orders**: Describe the dishes that need to be completed in order.

## 2. Output Requirements

  
  
  
  
- Tasks must be reasonably allocated to achieve multi-agent parallel collaboration and minimize total time consumption.


- Action sequence must completely cover the entire process from raw material acquisition, processing, assembly to serving.




- Always notice the timepoint when each action starts and ends to ensure no conflicts in agent actions and get the most efficient plan.


Please combine the map layout and recipe workflow to reasonably arrange each operation step and collaboration details, outputting a standard action list.
"""