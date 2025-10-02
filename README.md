# ParaCook

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

3. To human tests:

Please see `scripts/test_human.sh` for details.

```bash
./scripts/test_human.sh
```