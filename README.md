# AI Projects Repository

This repository is dedicated to a collection of Artificial Intelligence projects focusing on different aspects of AI, including puzzle solving, game playing, and decision-making through the use of algorithms and data structures. Each project is designed to tackle unique problems, offering a practical approach to understanding and implementing AI concepts.

## Projects Overview

### Expense 8 Puzzle

**Objective**: Develop an agent to solve a modified version of the 8 puzzle problem, termed as the Expense 8 puzzle. Unlike the traditional puzzle, each tile's number represents the cost of moving that tile. The goal is to achieve a desired configuration with the least total cost.

**Implementation**: `expense_8_puzzle.py <start-file> <goal-file> <method> <dump-flag>`

- `<start-file>` and `<goal-file>`: Define the initial and goal states.
- `<method>`: Choose from `bfs`, `ucs`, `dfs`, `dls`, `ids`, `greedy`, or `a*` (default).
- `<dump-flag>`: If true, dumps search trace for analysis.

### Red-Blue Nim Game

**Objective**: Create an AI to play two versions of a game called Red-Blue Nim against a human player. The game involves two piles of marbles, red and blue, and players remove marbles from these piles under specific rules to win or lose points.

**Implementation**: `red_blue_nim.py <num-red> <num-blue> <version> <first-player> <depth>`

- `<num-red>` and `<num-blue>`: Number of red and blue marbles respectively.
- `<version>`: `standard` or `misere` (default is `standard`).
- `<first-player>`: `computer` or `human` (default is `computer`).

### Decision Tree and Forest

**Objective**: Implement decision trees and forests for binary classification. The program will learn from training data and apply the learned model to classify test data.

**Implementation**: `dtree training_file test_file option`

- `training_file` and `test_file`: Specify the training and testing datasets.
- `option`: Select from `optimized`, `randomized`, `forest3`, or `forest15` for the training method.

