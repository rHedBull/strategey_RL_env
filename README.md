# setup

if both repos are only local
```bash
pip install -e /path/to/other/repo
```

# Civ Sim

## Game Rules

## Winning and Loosing
- there is NO win condition
- an Agent looses/ dies if its money is less than 0 or if it holds 0 claimed tiles

### Claiming tiles
- a tile can only be claimed if it is visible
- a tile can only be claimed if it is not already claimed
- a tile can only be claimed if it is adjacent to a claimed tile or a building not including roads and bridges

### Buildings
#### Roads
- can be placed next to an self owned city
- can be placed next to another road or bridge, which does not have to be self owned/ build
- only placeable on: normal Land, Dessert, Mountain and Marsh
- placement on Mountain costs twice as much

#### Bridge
- can be placed next to an self owned city
- can be placed next to another road or bridge, which does not have to be self owned/ build
- only placeable on: normal Ocean and River

#### City
- can only be placed on a visible or already self claimed tiles
- placement must keep clear of the city_clearance_distance from the next city
- placing a city claims the tile
- only placeable on: normal Land, Dessert and Marsh

#### Farm
- can only be placed on an already self claimed tile
- only placeable on: normal Land and Marsh
- placement on a tile with the resource Grain doubles the output of the mine

#### Mine
- can only be placed on an already self claimed tile
- only placeable on Mountain tile with or without a resource
- placement on a Mountain tile with the resource Metall doubles the output of the mine


## Units
base_unit_strength = 50
max_unit_strength = 500

only one unity type, one unit per tile

Placing
- can be placed on all visible tiles unclaimed or claimed by own agents
- cannot be placed an opponent claimed tile, unless there are 3 other own units adjacent to the tile
- can be placed on a tile with a building, except for roads and bridges
- cannot be place on opponent units
- if placed on existing own unit, the unit strenghts is added to the existing unit

Attacking
- opponent targets are, opponent units or buildings
- each unit automatically attacks randomly an adjacent opponent target
- an attack weakens the attacked and attacker
- damage is relative to the unit strengths

### Land Types
- normal Land
- Mountain
- Dessert
- Marsh
- Ocean

### Resources
#### Grain
- only on Land and Marsh tiles
- doubles Farm output

#### Metall
- only on Mountain tiles
- doubles Mine output


# API
## Environment

### Attributes
- env_settings (Dict[str, Any]): A dictionary containing environment-specific settings.
- num_agents (int): The number of agents present in the environment.
- render_mode (str): The mode for rendering the environment. Options:
  - 'human': Renders the environment to the screen.
  - 'rgb_array': Returns an RGB array of the current frame.
- seed (Optional[int]): Seed for the environment's random number generator, ensuring reproducibility.
- screen_width (int): Width of the rendering screen (default: 1000).
- screen_height (int): Height of the rendering screen (default: 1000).
- screen: The pygame screen object used for rendering.
- map: Represents the grid-based map of the environment.
- agents (List[Agent]): A list of agent instances present in the environment.
- action_manager (ActionManager): Manages and applies actions from agents.
- action_mapping: Placeholder for action mappings (implementation-specific).
- observation_space: Defines the space of possible observations.
- action_space: Defines the space of possible actions.

### Initialization
`__init__(env_settings, num_agents, render_mode='rgb_array', seed=None)`
Initializes the MapEnvironment.

Parameters:
- env_settings (Any): Configuration settings for the environment.
- num_agents (int): Number of agents in the environment.
- render_mode (str, optional): Rendering mode ('human' or 'rgb_array'). Default is 'rgb_array'.
- seed (Optional[int], optional): Seed for random number generation. Default is None.

Raises:
- ValueError: If env_settings is not a dictionary.
- ValueError: If num_agents is not an integer.
- ValueError: If render_mode is not 'human' or 'rgb_array'.
- ValueError: If seed is provided but is not an integer.

### `reset(seed=None, map_file=None)`
Resets the environment to its initial state and returns the initial observations.

Parameters:
- seed (Optional[int], optional): Seed for random number generation. If provided, it ensures reproducibility.
- map_file (Optional[str], optional): Path to a file defining the map topology. If provided, the map is created based on the file's topology.

Returns:
- Tuple[observations, info]:
- observations: Initial observations for all agents.
- info (Dict): Additional information (currently contains a placeholder).

Raises:
- ValueError: If seed is provided but is not an integer.

### `step(actions)`
Executes a step in the environment by applying actions from all agents and updating the environment state.
Dimension 1: List of agents.
Dimension 2: List of actions per agent.
Dimension 3: Action parameters ([action_id, x, y]).

action_id:
wait = 0
claim = 1
build_city = 2
build_road = 3
build_bridge = 4
build_farm = 5
build_mine = 6
destroy = 7
place_unit = 8
withdraw_unit = 9

Parameters:
- actions (List[List[List[int]]]): A 3D list of integers representing actions.

Returns:
- Tuple[observations, rewards, dones, truncated, info]:
- observations: Updated observations for all agents.
- rewards: Rewards received by each agent.
- dones: Flags indicating whether each agent died
- truncated: Flags indicating whether each agent's episode was truncated.(currently always False)
- info (Dict): Additional information (currently empty).

Raises:
- ValueError: If actions is not a 3D list of integers.
- ValueError: If each individual action does not consist of exactly three integers.

### `render()`
Renders the current state of the environment.

Behavior:
`env.render_mode == "human"` mode:
Updates the pygame display.
Prints the money and last money PL of the first agent.
`env.render_mode == "rgb_array"` mode:
Updates the pygame display.
Returns an RGB array representing the current frame.

Returns:
Optional[np.ndarray]: The RGB array if render_mode is 'rgb_array', otherwise None.

Raises:
- NotImplementedError: If an unknown render_mode is specified.


### `close()`
Closes the environment and performs necessary cleanup.

Behavior:
- Quits the pygame instance to free up resources.
- return the initial observation of the newly setup environment. and a info



# TODO

## RL Setup
- [ ] Integration with PufferLib?
- [ ] Optimized for RL, Cython?, JAX?


## Utils
- [ ] write profiler script for memory and time for different map sizes and agent counts-> write to a file/ table, maybe markdown?
- [ ] map previewer for a map topology file, with matplotlib

## Map
- [ ] extend map generator script to create maps of different settings
- [ ] create some maps with different sizes and different land type and resource distributions

- graph representation of roads

- make importance editable water over mountain over dessert
-  enable distribution method
-  make the distribution density and type editable
- add river water adjacent type, based on perlin noise with meandering
- enable actual biomes
- make height relevant for water and mountain
- loading maps into env
- more realistic height map with biomes and more influence on the map


## RL
- [ ] make some kind of run setup to run on the different maps of different settings and logg
- [ ] distance damage units
- [ ] wall structure?

### Observation
- [ ] different types of observability for different agents
- [ ] add option for continuos map
- [ ] optimize observation metrics calculation, updates, savings, costly since done every step


### Rewards
- [ ] calculate rewards better, decide what rewards to give !!
- [ ] setup reward structure around 0 with standard deviation of 1, is supposed to be better for learning
- [ ] increase city reward if connected to other cities, own farm or mine
- [ ] look for reward loopholes !!


### Actions
- [ ] account for continuous maps in action checks
- [ ] concept of upgradable buildings


## UI
- [ ] zooming, moving?


## Dev Ops
- [ ] move stuff to cython
- [ ] optimize for GPU, cuda
- [ ] add more scenario tests
- [ ] scaling tests, on predefined test map, small and large scale, by map size and agent count
- [ ] setup guide, game example
- [ ] simplify to single action per step
- [ ] think about package API access, which attributes of env and which methods, functions, objects should be accessible

### tests




## Far fetched
- [ ] tech tree, some actions only possible if reached a level
- [ ] Population
- [ ] Tech tree
- [ ] Units with own agent ai
- [ ] Diplomacy

# Mind Map
```mermaid
graph TB
    User((User/Agent))

    subgraph "Game Environment"
        MapEnv["Map Environment<br>Gymnasium"]

        subgraph "Core Systems"
            ActionMgr["Action Manager<br>Python"]
            MapGen["Map Generator<br>Python"]
            StateManager["State Manager<br>Python"]
        end

        subgraph "Map System"
            MapCore["Map Core<br>Python"]
            MapSquare["Map Square<br>Python"]
            MapPosition["Position Manager<br>Python"]
            VisibilitySystem["Visibility System<br>Python"]
        end

        subgraph "Action System"
            ActionBase["Action Base<br>Python"]

            subgraph "Building Actions"
                BuildCity["Build City Action<br>Python"]
                BuildFarm["Build Farm Action<br>Python"]
                BuildMine["Build Mine Action<br>Python"]
                BuildRoad["Build Road Action<br>Python"]
            end

            subgraph "Unit Actions"
                ClaimAction["Claim Action<br>Python"]
                DestroyAction["Destroy Action<br>Python"]
                MoveAction["Move Action<br>Python"]
                PlaceUnit["Place Unit Action<br>Python"]
                WithdrawUnit["Withdraw Unit Action<br>Python"]
            end
        end

        subgraph "Game Objects"
            OwnableBase["Ownable Base<br>Python"]

            subgraph "Buildings"
                City["City<br>Python"]
                Farm["Farm<br>Python"]
                Mine["Mine<br>Python"]
                Road["Road<br>Python"]
            end

            Unit["Unit<br>Python"]
        end

        subgraph "Rendering System"
            PyGame["Pygame Renderer<br>Pygame"]
        end
    end

    %% Core Relationships
    User -->|"Interacts with"| MapEnv
    MapEnv -->|"Uses"| ActionMgr
    MapEnv -->|"Manages"| MapCore
    MapEnv -->|"Renders via"| PyGame

    %% Action System Relationships
    ActionMgr -->|"Manages"| ActionBase
    ActionBase -->|"Defines"| BuildCity
    ActionBase -->|"Defines"| BuildFarm
    ActionBase -->|"Defines"| BuildMine
    ActionBase -->|"Defines"| BuildRoad
    ActionBase -->|"Defines"| ClaimAction
    ActionBase -->|"Defines"| DestroyAction
    ActionBase -->|"Defines"| MoveAction
    ActionBase -->|"Defines"| PlaceUnit
    ActionBase -->|"Defines"| WithdrawUnit

    %% Map System Relationships
    MapCore -->|"Contains"| MapSquare
    MapCore -->|"Uses"| MapPosition
    MapCore -->|"Uses"| VisibilitySystem
    MapCore -->|"Generated by"| MapGen

    %% Game Objects Relationships
    OwnableBase -->|"Inherited by"| City
    OwnableBase -->|"Inherited by"| Farm
    OwnableBase -->|"Inherited by"| Mine
    OwnableBase -->|"Inherited by"| Road
    OwnableBase -->|"Inherited by"| Unit

    %% State Management
    StateManager -->|"Updates"| MapCore
    StateManager -->|"Updates"| ActionMgr
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

# Bugs

- [ ] if bug with pyopengl for rendering you might need to do this: https://programmersought.com/article/82837518484/
- [ ] if error with rendering accessing the libGL error MESA-LOADER  failed to open iris driver try this command 'conda install -c conda-forge libstdcxx-ng', more info here: https://stackoverflow.com/questions/72110384/libgl-error-mesa-loader-failed-to-open-iris

Map size: 10x10, Agents: 2, Reset time: 0.0037834644317626953, Step/s 2344.8764752251623
Map size: 10x10, Agents: 10, Reset time: 0.005107402801513672, Step/s 1794.7999931533814
Map size: 100x100, Agents: 2, Reset time: 0.22341489791870117, Step/s 33.15119413501928
Map size: 100x100, Agents: 10, Reset time: 0.2037661075592041, Step/s 36.77033618661215
Map size: 100x100, Agents: 60, Reset time: 0.19458580017089844, Step/s 34.945535489851494
Map size: 1000x1000, Agents: 2, Reset time: 20.36270833015442, Step/s 0.38219249438168773
Map size: 1000x1000, Agents: 10, Reset time: 20.66606330871582, Step/s 0.3379367061436302
Map size: 1000x1000, Agents: 60, Reset time: 22.43561816215515, Step/s 0.37132157694853146
