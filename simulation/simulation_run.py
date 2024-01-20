import pickle
import random

from simulation.nation import Nation
import pandas as pd


class Simulation_run:

    def __init__(self, numb_nations, save_file_name, max_steps):
        self.save_file = save_file_name

        self.nations = []
        self.numb_nations = numb_nations
        self.max_steps = max_steps
        self.all_states = []
        self.save_df = pd.DataFrame()

    def setup_run(self):
        for i in range(self.numb_nations):
            self.nations.append(Nation("Nation " + str(i), "red", 100))

    def update(self):

        #random update

        update_nations_list = self.nations.copy()
        random.shuffle(update_nations_list)

        for nation in update_nations_list:
            nation.update()
        self.save_step()

    def run_calculation(self):

        for step in range(self.max_steps):
            for nation in self.nations:
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
        pickle_file = "./saveFiles/" + save_file_name + "_nations.pkl"
        with open(pickle_file, 'rb') as file:
            self.save_df = pickle.load(file)

    def visualize_on_graph(self):
        print(self.df.head())
