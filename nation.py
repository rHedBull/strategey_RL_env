class Nation:
    def __init__(self, name, color, initial_money):
        self.name = name
        self.color = color
        self.money = initial_money

    # return nation state as a dictionary
    def get_nation_state_as_dic(self):
        return {"name": self.name, "color": self.color, "money": self.money}
    def save_nation_state(self):
        raise NotImplementedError

    def update_nation_state(self):
        self.money += 1

