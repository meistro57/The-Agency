class AgentMarketplace:
    """Registry for sharing and instantiating agents."""

    def __init__(self):
        self._agents = {}

    def register_agent(self, name: str, agent_cls):
        self._agents[name] = agent_cls

    def list_agents(self):
        return list(self._agents.keys())

    def create_agent(self, name: str, config, memory):
        cls = self._agents.get(name)
        if not cls:
            raise ValueError(f"Unknown agent: {name}")
        return cls(config, memory)
