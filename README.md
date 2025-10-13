# ParaCook: On Time-Efficient Planning for Multi-Agent Systems

> A benchmark for evaluating parallel and asynchronous planning ability of large language model based agents.

📌 **Paper:** Coming soon on arXiv (link placeholder)

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

2. To run the tests:

```bash
./scripts/test.sh
```

## 🎮 GUI for Human Tests

We provide a web-based GUI for human tests. 
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
If you find this work useful, please consider citing (BibTeX coming soon)




