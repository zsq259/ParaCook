# ParaCook: On Time-Efficient Planning for Multi-Agent Systems

> A benchmark for evaluating parallel and asynchronous planning ability of large language model based agents.

📌 **[Paper Link](https://arxiv.org/abs/2510.11608)**

---

### Abstract
Large Language Models (LLMs) exhibit strong reasoning abilities for planning long-horizon, real-world tasks, yet existing agent benchmarks focus on task completion while neglecting time efficiency in parallel and asynchronous operations. To address this, we present **ParaCook**, a benchmark for time-efficient collaborative planning. Inspired by the Overcooked game, ParaCook provides an environment for various challenging interaction planning of multi-agent systems that are instantiated as cooking tasks, with a simplified action space to isolate the core challenge of strategic parallel planning. Through a comprehensive evaluation of state-of-the-art LLMs, we find that current approaches achieve suboptimal plans, which struggle with parallel actions or coordination. Our analysis also reveals LLMs' potential on abstract tasks where they can focus on high-level parallel optimization. ParaCook provides a scalable evaluation framework with adjustable complexity, establishing a foundation for developing and assessing time efficiency-aware multi-agent planning.


## 🚀 Quick Start

1. Create a conda environment and install dependencies:

```bash
conda create -n paracook python=3.12 -y
conda activate paracook
pip install -r requirements.txt
```

2. To run a sample test with a built-in agent:

```bash
python -m src.main --model gpt-5 --agent CoT --examples burger_basic --orders burger/burger_basic --map config/map_examples/map2.json
```

3. To run batch tests with different agents and tasks:

```bash
./scripts/test.sh
```

## 🧩 Define your agent and test

To define your own agent, please refer to `src/agent/agent.py` for the base class `Agent`, and some other example agents in `src/agent/method/`, such as `IOAgent`. You can create a new agent by inheriting from the base class and implementing the required methods, such as `run_test`.
You should register your agent in the `name_to_agent` dictionary in `src/main.py`.
To test your agent, you can modify the test script, use your agent's name in the `--agent` argument.

In `src/game/simulator.py`, we provide an interface for the simulator to interact with agents:

- `submit_plan(actions: Dict[str, List])`: Submit the planned actions for each agent. The `actions` parameter is a dictionary mapping agent names to their respective action lists.
- `step()`: Advance the simulation to the next event timepoint, processing all events scheduled for that time.
- `next_decision_step()`: Advance the simulation until the next decision point where one or more agents need to make decisions. Returns a list of agent names that need to act.
- `run_simulation(raise_on_error: bool = False)`: Run the simulation until completion or until an error occurs. If `raise_on_error` is True, exceptions will be raised; otherwise, they will be logged.
- `get_observation()`: Get the current observation dict of the environment, including the state of agents and workstations.
- `get_decision_agents()`: Get a list of agents that need to make decisions at the current time step.
- `is_done()`: Check if all tasks are completed.


## 🎮 GUI for Human Tests

We provide a web-based GUI for human tests. Please follow the steps below to set up the environment.

```bash
cd gui/web
npm install
```

Run the following command to start an example human test:

```bash
python -m src.main --model name --agent Human --orders pasta/pasta_mushroom pasta/pasta_tomato --map data/cook/maps/pasta/seed_42/agent_num_2
```

Or see and run the script for batch tests:

```bash
./scripts/test_human.sh
```

---

## 📚 Citation
If you find this work useful, please consider citing our paper:

```bibtex
@misc{zhang2025paracooktimeefficientplanningmultiagent,
      title={ParaCook: On Time-Efficient Planning for Multi-Agent Systems}, 
      author={Shiqi Zhang and Xinbei Ma and Yunqing Xu and Zouying Cao and Pengrui Lu and Haobo Yuan and Tiancheng Shen and Zhuosheng Zhang and Hai Zhao and Ming-Hsuan Yang},
      year={2025},
      eprint={2510.11608},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2510.11608}, 
}
```




