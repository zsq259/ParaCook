#!/bin/bash


python -m src.main --model gpt-4o --agent CoT --examples burger_basic --orders salad/salad_advanced

python -m src.main --model gemini-2.5-pro --agent MultiStepReAct --examples salad_advanced --orders sushi/sushi_fish --map config/map/map3

python -m src.main --model gpt-4o --agent Fixed --examples burger_basic --orders salad/salad_advanced
python -m src.main --model gpt-4o --agent Fixed --orders sushi/sushi_fish --map config/map/map3
python -m src.main --model gpt-4o --agent Fixed --orders salad/salad_advanced
