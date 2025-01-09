class Ownable:
    """
    Mixin class to add ownership capabilities to buildings.
    """

    def __init__(self, agent_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner_id = agent_id  # ID of the owning agent

    def set_owner(self, agent_id: int):
        """
        Assign ownership to an agent.
        """
        self.owner = agent_id

    def get_owner(self) -> int:
        """
        Get the ID of the owning agent.
        """
        return self.owner
