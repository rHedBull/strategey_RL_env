class Ownable:
    """
    Mixin class to add ownership capabilities to buildings.
    """

    def __init__(self, agent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = agent  # ID of the owning agent

    def set_owner(self, agent):
        """
        Assign ownership to an agent.
        """
        self.owner = agent

    def get_owner(self):
        """
        Get the ID of the owning agent.
        """
        return self.owner
