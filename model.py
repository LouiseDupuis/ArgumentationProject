

from agents import DebateAgent
from graphs import DebateGraph
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from schedule import SimultaneousDebateActivation
from learning import learn_all, learn_nothing

class OnlineDebate(Model):
    """
    Model implementing the protocol for the Online Debate Games
    """


    description = (
        "A model for simulating online debates"
    )

    def __init__(
        self, num_agents, argument_graph, semantic, threshold
    ):
        """
        Create a new model with the given parameters.

        Args: num_agents = total number of agents
              argument_graph = the graph containing all of the possible arguments od the debate and their relationships
              semantic = a GradualSemantic object used to assess the argument's strength
            
        """
        super().__init__()
        # Set parameters

        self.num_agents = num_agents
        self.argument_graph = argument_graph
        self.semantic = semantic
        self.threshold = threshold

        self.public_graph = DebateGraph(argument_graph.get_issue())
        
        self.schedule = SimultaneousDebateActivation(self)

        self.strategies = dict() # a dictionnary keeping track of all of the agent's strategies

        print("=============== MODEL INITIALIZATION =========================================")
        print()
        print("Global Argument Graph for the game : ")
        self.argument_graph.view_edges()
        
        # Create each agent and their opinion graph
        for i in range(num_agents):
            print()
            opinion_graph = argument_graph.create_subgraph()
            opinion_graph.view_edges()
            agent = DebateAgent(i, model=self, opinion_graph = opinion_graph, learning_strategy=learn_nothing, threshold=threshold)
            self.schedule.add(agent)


    def get_semantic(self):
        return self.semantic
    
    def implement_strategy(self, strategy):
        #self.strategies
        if strategy != 'NOTHING':
            self.public_graph.add_node(strategy[0])
            self.public_graph.add_edges_from(strategy[1])

        
    def step(self, i):
        print()
        print()
        print("------------------ Step ", i, "---------------------------------------")
        print()
        print("Current Public Graph : ")
        self.public_graph.view_edges()
        self.strategies[i] = dict()
        self.schedule.step()
        print()
        # Collect data
        #self.datacollector.collect(self)

    def run_model(self, step_count=10):
        for i in range(step_count):
            self.step(i)

