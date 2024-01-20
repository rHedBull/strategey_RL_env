action_dictionary = {
    'Move Up': 0,
    'Move Down': 1,
    'Move Left': 2,
    'Move Right': 3,
    'Claim': 4
}


class ActionManager:
    def __init__(self):
        self.action_to_int = action_dictionary
        self.int_to_action = {v: k for k, v in self.action_to_int.items()}

    def get_action_name(self, action_int):
        return self.int_to_action.get(action_int, "Unknown")

    def get_action_int(self, action_name):
        return self.action_to_int.get(action_name, -1)


