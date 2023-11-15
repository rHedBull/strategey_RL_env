import json

import pickle
import pygame
from nation import Nation
import pandas as pd


class simulation_run:

    def __init__(self,  numb_nations, save_file_name, max_steps):
        self.save_file = save_file_name
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

        # save to pickle file
        save_directory = "./saveFiles/"
        with open(save_directory + self.save_file + ".pkl", 'wb') as file:
            pickle.dump(self.save_df, file)

        # save to csv file
        self.save_df.to_csv(save_directory + self.save_file + ".csv", index=False)

    def load_from_file(self, save_file_name):
        # load from pickle file
        pickle_file = "./saveFiles/" + save_file_name + ".pkl"
        with open(pickle_file, 'rb') as file:
            self.save_df = pickle.load(file)

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

    def visualize_on_graph(self):
        raise NotImplementedError