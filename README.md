# Civ Sim


## TODO

### Game
- [ ] Population
- [ ] Tech tree
- [ ] Buildings
- [ ] Units
- [ ] Diplomacy
- [ ] Combat
- [ ] continuous map?

### RL Setup
- [ ] Integrartion with PufferLib
- [ ] Optimized for RL, Cython?
- [ ] restructure project setup


## Code quality

### pre-commit

This project uses [pre-commit](https://pre-commit.com/) to enforce code quality.
It must be executed manually!

```bash
pre-commit run -a
```

### TF logs
clear TF logs
run TF board

```bash
tensorboard --logdir logs
```
### time profiling

```bash
python -m cProfile -o output.prof main.py
snakeviz output.prof
``` 

| tiles | sim_map.create_map | map_square.draw | 
|-------|--------------------|-----------------|
| 10    | 0.000              | 0.000           |
| 10^2  | 0.000              | 0.000           |
| 10^3  | 0.000              | 0.000           |
| 10^4  | 0.000              | 0.000           |
| 10^5  | 0.000              | 0.000           |
| 10^6  | 23.6               | 9.08            |
| 10^9  | 0.000              | 0.000           |
### memory profiling

add the following to the functions you want to profile

```python
from memory_profiler import profile
@profile
def your_function():
    pass
```

run the script with the following command
```bash
python -m memory_profiler your_script.py
```

| memory | spike 1 | spike_2 | 
|--------|---------|---------|
| 10     | 0.000   | 0.000   |
| 10^2   | 0.000   | 0.000   |
| 10^3   | 0.000   | 0.000   |
| 10^4   | 0.000   | 0.000   |
| 10^5   | 0.000   | 0.000   |
| 10^6   | 23.6    | 9.08    |
| 10^9   | 0.000   | 0.000   |


# TODOs

- [ ] write profiler script for memory and time for different map sizes and agent counts-> write to a file/ table, maybe markdown?
## Map
- [ ] write script that just creates multiple maps of various sizes and save them to be used later
- [ ] create some maps with different sizes and different land type and resource distributions
  - [ ] add some resources
- make importance editable water over mountain over dessert
-   make distribution percentage wise locked to tile count
-  enable selection of land types
-  enable distribution method
- add random mountain distribution
-  make the distribution density and type editable
- add river water adjacent type

## RL
- [ ] add more actions
- [ ] calculate rewards better, decide what rewards to give
- [ ] train simple claiming AI
- [ ] calculate just execution time for different map sizes and agent counts on hardware
- [ ] different types of observability for different agents

## UI
- [ ] zooming, moving?
- 
## Far fetched
- [ ] tech tree, some actions only possible if reached a level
- [ ] 