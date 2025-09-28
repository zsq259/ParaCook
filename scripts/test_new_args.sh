#!/bin/bash

# 测试新的 argparse 版本

echo "测试 1: 基本命令行参数"
echo "===================="
python -m src.main --model gpt-4o --agent CoT --examples burger_basic --orders salad/salad_advanced
python -m src.main --model gpt-4o --agent Fixed --examples burger_basic --orders salad/salad_advanced

python -m src.main --model gpt-4o --agent Fixed --orders sushi/sushi_fish --map config/map/map3
python -m src.main --model gpt-4o --agent Fixed --orders salad/salad_advanced

echo ""
echo "测试 2: 配置文件 + 命令行参数"
echo "===================="
echo "python -m src.main --config config/experiment/test.yaml --model gpt-4o --help"

echo ""
echo "提示：现在可以直接使用："
echo "1. 纯命令行方式："
echo "   python -m src.main --model gpt-4o --agent ReAct --examples salad_advanced"
echo ""
echo "2. 配置文件 + 命令行覆盖："
echo "   python -m src.main --config config/experiment/test.yaml --model gpt-4o"
echo ""
echo "3. 使用简化的启动脚本："
echo "   ./run_experiment.sh --model gpt-4o --agent ReAct --examples salad_advanced"
echo ""
echo "4. 批量运行："
echo "   ./run_batch_experiments.sh --models \"gpt-4o gemini-2.5-pro\" --agents \"ReAct CoT\""