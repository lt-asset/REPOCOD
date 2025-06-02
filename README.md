# Can Language Models Replace Programmers? REPOCOD Says ‘Not Yet’

We create REPOCOD, a code generation benchmark with 980 problems collected from 12 popular real-world projects, with more than 58% of them requiring file-level or repository-level context information. In addition, REPOCOD has the longest average canonical solution length (331.6 tokens) and the highest average cyclomatic complexity (9.00) compared to existing benchmarks. Each task in REPOCOD includes 313.5 developer-written test cases on average for better correctness evaluation. In our evaluations on ten LLMs, none of the models achieves more than 30 pass@1 on REPOCOD, disclosing the necessity of building stronger LLMs that can help developers in real-world software development.

## Updates:
10/30/2024: Our preprint available at: [ArXiv](https://arxiv.org/abs/2410.21647v1)

10/30/2024: Our dataset is available on Huggingface: [link](https://huggingface.co/datasets/lt-asset/REPOCOD)

11/01/2024: The leaderboard is available here: [leaderboard](https://lt-asset.github.io/REPOCOD/)
## Usage

### Install Dependencies
Optional choice to use a conda environment:
```
conda create -n repocod python=3.10 -y
conda activate repocod
```

Please use the following commands to install the necessary packages for inference and evaluation using REPOCOD.
```
pip install --upgrade pip
pip install -r requirements.txt
```

### Inference
Please refer to [./inference/Inference.md](./inference/Inference.md) for using REPOCOD.

### Evaluation
To evaluate on REPOCOD, please refer to [./evaluate/Evaluate.md](./evaluate/Evaluate.md).

## Data Collection
![Overview of REPOCOD's data collection process](./resources/overview_repocod.png)

We employ a three-stage data collection pipeline to efficiently gather target functions from popular repositories: Repository Selection, Target Function Selection, and Relevant Test Case Collection. For more details, feel free to read our paper!

## LLMs' Performance
![LLM's performance on REPOCOD](./resources/main_result.png)

This table shows 10 LLMs’ performance on REPOCOD, under three retrieval settings. On all retrieval methods, commercial LLMs have better performance. Specifically, GPT-4o has the best result, reaching up to 27.35 pass@1. 

However,  Compared
to their pass@1 on HumanEval (about 90 pass@1) and MBPP, SOTA LLMs are still far
away from writing real-world programs requiring repository-level information.

## Citation

```
@misc{liang2024languagemodelsreplaceprogrammers,
      title={Can Language Models Replace Programmers? REPOCOD Says 'Not Yet'}, 
      author={Shanchao Liang and Yiran Hu and Nan Jiang and Lin Tan},
      year={2024},
      eprint={2410.21647},
      archivePrefix={arXiv},
      primaryClass={cs.SE},
      url={https://arxiv.org/abs/2410.21647}, 
}
```
