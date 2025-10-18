#!/bin/bash


# Run single model test examples
python -m src.main --model gpt-5 --agent CoT --examples burger_basic --orders burger/burger_basic --map config/map_examples/map2
python -m src.main --model gpt-5 --agent MultiStepReAct --examples burger_basic --orders burger/burger_basic --map config/map_examples/map2
python -m src.main --model gpt-5 --agent MultiStepReAct --examples burger_basic --orders salad/salad_advanced --map config/map_examples/map1
python -m src.main --model gpt-5 --agent MultiStepReAct --examples burger_basic --orders pasta/pasta_mushroom pasta/pasta_tomato --map data/cook/maps/pasta/seed_42/agent_num_2

# Run single human test example
python -m src.main --model name --agent Human --orders pasta/pasta_mushroom pasta/pasta_tomato --map data/cook/maps/pasta/seed_42/agent_num_2
