import json
import time

from strategyRLEnv.environment import MapEnvironment


test_settings = {
    "map_width": 10,
    "map_height": 10,
    "water_budget_per_agent": 0.2,
    "mountain_budget_per_agent": 0.1,
    "dessert_budget_per_agent": 0.1,
    "resource_density": 0.5,
    "city_clearance_radius": 3,
    "agent_initial_budget": 1000,
    "agent_initial_budget_distribution": "equal",
    "actions": {
        "wait": {
            "cost": 1,
            "reward": 0
        },
        "claim": {
            "cost":100,
            "reward": 10
        },
        "build_city": {
            "cost": 500,
            "reward": 20,
            "money_gain_per_turn": 110,
            "maintenance_cost_per_turn": 10
        },
        "build_road": {
            "cost": 10,
            "reward": 3
        },
        "build_bridge": {
            "cost": 20,
            "reward": 3
        },
        "build_farm": {
            "cost": 100,
            "reward": 5,
            "money_gain_per_turn": 20,
            "maintenance_cost_per_turn": 5
        },
        "build_mine": {
            "cost": 8,
            "reward": 5,
            "money_gain_per_turn": 20,
            "maintenance_cost_per_turn": 5
        },
        "destroy": {
            "action_id": 7,
            "cost": 0,
            "reward": 0.5
        },
        "place_unit": {
            "cost": 50,
            "reward": 0.5
        },
        "withdraw_unit": {
            "cost": 0.7
        },
        "invalid_action_penalty": -1000
    },
    "map_features": [
        {
            "name": "land_type",
            "select": True,
            "values": {
                "min": 0,
                "max": 5
            }
        },
        {
            "name": "tile_ownership",
            "select": True,
            "values": {
                "min": 0,
                "max": 63
            }
        },
        {
            "name": "land_money_value",
            "select": False,
            "values": {
                "min": 0,
                "max": 10000
            }
        },
        {
            "name": "buildings",
            "select": True,
            "values": {
                "min": 0,
                "max": 10000000000
            }
        },
        {
            "name": "resources",
            "select": False
        }
    ],
    "agent_features": [
        {
            "name": "agent_money",
            "select": True,
            "values":{
                "min": 0,
                "max": 1000000
            }
        },
        {
            "name": "agent_map_ownership",
            "select": True,
            "values":{
                "min": 0,
                "max": 1
            }
        },
        {
            "name": "last_money_pl",
            "select": False
        },
        {
            "name": "resource_access",
            "select": False
        },
        {
            "name": "resource_collection_rate",
            "select": False
        },
        {
            "name": "production_rate",
            "select": False
        },
        {
            "name": "resource_collection_rate",
            "select": False
        }
    ]
}


def timing_test():
    map_sizes = [10, 100, 1000]
    agents = [2, 10, 60]

    for size in map_sizes:
        for numb in agents:
            if (size * size)/ numb < 10:
                continue
            test_settings["map_width"] = size
            test_settings["map_height"] = size
            env = MapEnvironment(test_settings, numb, "rgb_array")
            t_0 = time.time()
            env.reset()
            t_1 = time.time()
            action_space = env.action_space

            max_total_steps = 100
            total_steps_taken = 0

            while total_steps_taken < max_total_steps:
                actions = [[action_space.sample()] for _ in range(numb)]

                new_observations, rewards, dones, all_done, infos = env.step(actions)
                total_steps_taken += 1
                if total_steps_taken in [25, 50, 75]:
                    print(f"Step: {total_steps_taken}")
            t_2 = time.time()
            env.close()

            print(f"Map size: {size}x{size}, Agents: {numb}, Reset time: {t_1 - t_0}, Step/s {100/ (t_2 - t_1)}")


if __name__ == "__main__":
    timing_test()