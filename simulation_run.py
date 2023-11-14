import json

import pygame
from nation import Nation


class simulation_run:

    def __init__(self,  numb_nations, path_to_saveFile, max_steps):
        self.saved_file = path_to_saveFile
        #self.world_map = map # TODO create map class
        self.nations = []
        self.numb_nations = numb_nations
        self.max_steps = max_steps
        self.all_states = []

    def setup_run(self):
        for i in range(self.numb_nations):
            self.nations.append(Nation("Nation " + str(i), "red", 100))

    def run_calculation(self):

        for i in range(self.max_steps):
            for nation in self.nations: # TODO make random order
                nation.update_nation_state()

            self.all_states.append({ "step": i, "nation_states": self.save_all_nations_state()})

        with open("test.json", "w") as file:
            json.dump(self.all_states, file, indent=4)

    # save nations state of the current step
    def save_all_nations_state(self):
        current_total_state = []
        for nation in self.nations:
            current_nation_state = nation.get_nation_state_as_dic()
            current_total_state.append(current_nation_state)

        return current_total_state

    def visualize_on_map(self):
        pygame.init()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Update and display the world map
            self.world_map.display()

        # Quit pygame
        pygame.quit()

        raise NotImplementedError

    def visualize_on_graph(self):
        raise NotImplementedError

    def save_to_file(self):
        raise NotImplementedError

    def load_from_file(self, path_to_file):
        raise NotImplementedError
