class Agent:
    def __init__(self, id):
        self.id = id
        self.reset()

    def reset(self):
        # Reset the agent to its initial state
        self.state = None