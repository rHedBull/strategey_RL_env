from strategyRLEnv.map.map_settings import healing_base


class Destroyable:
    """
    Mixin class to add ownership capabilities to buildings.
    """

    def __init__(self, health: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_health = health
        self.health = health

    def reduce_health(self, env, damage):
        self.health -= damage
        print(f"Building {self.building_type} reduced health to {self.health}")
        if self.health <= 0:
            self.destroy(env)

    def heal(self):
        health = self.health + healing_base
        self.health = min(health, self.max_health)

    def destroy(self, env):
        env.map.remove_building(self.position)
        print(f"Building {self.building_type} destroyed at {self.position}")
