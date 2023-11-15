import json

import pygame
from nation import Nation
import pandas as pd


class simulation_run:

    def __init__(self,  numb_nations, path_to_saveFile, max_steps):
        self.save_file = path_to_saveFile
        #self.world_map = map # TODO create map class
        self.nations = []
        self.numb_nations = numb_nations
        self.max_steps = max_steps
        self.all_states = []
        self.save_df = pd.DataFrame()

    def setup_run(self):
        for i in range(self.numb_nations):
            self.nations.append(Nation("Nation " + str(i), "red", 100))

    def run_calculation(self):

        for step in range(self.max_steps):
            for nation in self.nations: # TODO make random order
                nation.update()
            self.save_step(step)
        self.save_to_file()

    def save_step(self, step):
        data = []
        for nation in self.nations:
            data.append(nation.get_nation_data_as_dict(step))
        df = pd.DataFrame(data)
        self.save_df = pd.concat([self.save_df, df], ignore_index=True)

    def save_to_file(self):
        # TODO save to other file types
        self.save_df.to_csv(self.save_file, index=False)

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

    def load_from_file(self, path_to_file):
        raise NotImplementedError

    def save_all_nations_state(self):
        current_total_state = []
        for nation in self.nations:
            current_nation_state = nation.get_nation_state_as_dic()
            current_total_state.append(current_nation_state)

        return current_total_state
