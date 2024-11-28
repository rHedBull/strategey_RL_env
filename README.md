# Civ Sim

## Game Rules

### Claiming tiles
- a tile can only be claimed if it is visible
- a tile can only be claimed if it is not already claimed
- a tile can only be claimed if it is adjacent to a claimed tile or a building not including roads and bridges

### Buildings
#### Roads
- must be placed on an already self claimed tile
- or next to another building including roads and bridges
- only placable on: normal Land, Dessert and Marsh

#### Bridge
- must be placed on an already self claimed tile
- or next to another building including roads and bridges
- - only placable on: normal Ocean and River

#### City
- can only be placed on a visible or already self claimed tiles
- placing a city claims the tile
- only placable on: normal Land, Dessert and Marsh

#### Farm
- can only be placed on an already self claimed tile
- only placable on: normal Land and Marsh

# RL considerations

## Action space


# Code quality

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


# TODO

- [ ] adapt more stringly to openAI gym interface
- [ ] pygame should only be needed to handle here

## RL Setup
- [ ] Integrartion with PufferLib
- [ ] Optimized for RL, Cython?, JAX?
- [ ] restructure project setup


## Utils
- [ ] write profiler script for memory and time for different map sizes and agent counts-> write to a file/ table, maybe markdown?
- [ ] map previewer

## Map
- [ ] extend map generator script to create maps of different settings
- [ ] create some maps with different sizes and different land type and resource distributions
  - [ ] add some resources

- graph representation of roads

- make importance editable water over mountain over dessert
-  enable distribution method
- add resources
-  make the distribution density and type editable
- add river water adjacent type, based on perlin noise with meandering
- enable actual biomes
- make height relevant for water and mountain
- map seperated from env, first create env, then function to create map, enable generating maps, loading maps into env

## RL

- [ ] calculate just execution time for different map sizes and agent counts on hardware
- [ ] make some kind of run setup to run on the different maps of different settings and logg

### Observation
- [ ] different types of observability for different agents
- [ ] adjust height, biomes and other min and max values in obs space
  - [ ] add option for continuos map
  - differentiate between tiles seen and claimed and how it influences where actions can happen

### Rewards
- [ ] calculate rewards better, decide what rewards to give


### Actions
- [ ] !! adjust action space
- [ ] account for continuous maps in action checks
- [ ] add Mine with resource extraction

## UI
- [ ] zooming, moving?
- [ ] Better Game termination log, why did it terminate?, which round?
- [ ] round counter in ui
- [ ] better logging for other agents, what actions they choose
- [ ] City ID connected to city owner?

## Dev Ops
- [ ] move stuff to cython
- [ ] connect to pufferlib
- [ ] optimize for GPU, cuda
- [ ] add more tests, increase coverage
- [ ] add more scenario tests
- [ ] scaling tests, on predefined test map, small and large scale, by map size and agent count


## Far fetched
- [ ] tech tree, some actions only possible if reached a level
- [ ] Population
- [ ] Tech tree
- [ ] Units
- [ ] Diplomacy
- [ ] Combat

# Mind Map

```mermaid
graph LR

    m[main] --> R[Run]
    R --> A[Agent]
    A --> E[Environment]

```

```mermaid
graph LR

    subgraph Agent
        P[Policy]
    end

    subgraph Environment

        E1[ActionManager]
        E2[SimulationAgents]
        E2[Map]

    end

    P-- Action --> Environment
    Environment -- Reward --> Agent
    Environment -- Observation --> Agent
```

# Resources

## interesting tools and repos

* https://terrain.party/
* https://godotengine.org/asset-library/asset/1913
* https://github.com/Mindwerks/plate-tectonics
* https://github.com/Mindwerks/worldengine
* https://github.com/jessvb/3D_world_procedural_generation_GAN/blob/master/README.md
* http://www-cs-students.stanford.edu/~amitp/game-programming/polygon-map-generation/
* https://www.redblobgames.com/maps/mapgen4/
* https://www.redblobgames.com/x/1929-voronoi-percolation/

### intersting research
* https://www.instructables.com/Converting-Map-Height-Data-Into-3D-Tiles/
* https://www.mit.edu/~jessicav/6.S198/Blog_Post/ProceduralGeneration.html

## coding tools

* https://neptune.ai/blog/tensorboard-tutorial
