from collections import defaultdict

from mesa.time import SimultaneousActivation

class SimultaneousDebateActivation(SimultaneousActivation):
    """A scheduler to simulate the simultaneous activation of all the agents.

    This scheduler requires that each agent have two methods: step and advance.
    step() activates the agent and stages any necessary changes, but does not
    apply them yet. advance() then applies the changes.

    """

    def step(self) -> None:
        """ Step all agents, then advance them. """
        agent_keys = list(self._agents.keys())
        for agent_key in agent_keys:
            self._agents[agent_key].step()
        for agent_key in agent_keys:
            self._agents[agent_key].advance()
        for agent_key in agent_keys:
            self._agents[agent_key].learn_and_vote()
        self.steps += 1
        self.time += 1
