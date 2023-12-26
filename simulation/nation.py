class Nation:
    def __init__(self, name, color, initial_money):
        self.name = name
        self.color = color
        self.money = initial_money
        self.territory = []

    # return nation state as a dictionary
    def get_nation_data_as_dict(self,   step):
        return {"step": step, "name": self.name, "color": self.color, "money": self.money}

    def update(self):
        self.money += 1

    def add_territory(self, territory):
        self.territory.append(territory)
