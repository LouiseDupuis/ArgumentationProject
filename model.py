

from copy import Error
from agents import DebateAgent
from graphs import DebateGraph
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from schedule import SimultaneousDebateActivation
import time 
from datetime import datetime

class OnlineDebate(Model):
    """
    Model implementing the protocol for the Online Debate Games
    """


    description = (
        "A model for simulating online debates"
    )

    def __init__(
        self, num_agents, argument_graph, semantic, threshold, learning_strategy, voting_strategy, subgraph_creation, save
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
        self.subgraph_creation = subgraph_creation

        self.public_graph = DebateGraph(argument_graph.get_issue())
        
        self.schedule = SimultaneousDebateActivation(self)

        self.time = datetime.now() # a time marker to help save all relevant informations

        self.state = [] # a list keeping track of all of the previous states of the game
        self.strategies = [] # a list keeping track of all of the agent's strategies during the game

        print("=============== MODEL INITIALIZATION =========================================")
        print()
        print("Global Argument Graph for the game : ")
        self.argument_graph.view_graph()  #printing graph on command line
        self.argument_graph.draw(self.get_time(), "Argument Graph", save = save)
        print("Value of the Issue : ", self.semantic.get_argument_value(self.argument_graph.get_issue(), self.argument_graph))
        
        # Create each agent and their opinion graph
        for i in range(num_agents):
            print()
            print("Agent ", i)
            if self.subgraph_creation == 'random':
                opinion_graph = argument_graph.create_subgraph_new()
            elif self.subgraph_creation == 'custom':
                opinion_graph = argument_graph.create_subgraph()
            opinion_graph.view_graph()
            
            agent = DebateAgent(i, model=self, opinion_graph = opinion_graph, learning_strategy=learning_strategy, threshold=threshold, voting_strategy=voting_strategy)
            opinion_graph.draw(self.get_time(), "Agent " + str(i) + ' ' + agent.get_position(self.semantic, self.threshold), save = save)
            self.schedule.add(agent)


    def get_semantic(self):
        return self.semantic
    
    def get_time(self):
        return self.time
    
    def implement_strategy(self, strategy, agent):
        self.strategies[-1][agent] =  strategy
        if strategy != 'NOTHING':
            self.public_graph.add_node(strategy[0])
            self.public_graph.add_edges_from(strategy[1])
            self.public_graph.add_upvote(strategy[0], agent)
    
    def get_previous_graph(self):
        """ Returns the public graph from the last step
        """
        if len(self.state) < 1:
            raise Error("There is no previous graph to return")
        return self.state[-1]

    def check_equilibrium(self):
        for s in self.strategies[-1].values():
            if s != 'NOTHING':
                return False
        return True

        
    def step(self, i):
        print()
        print()
        print("------------------ Step ", i, "---------------------------------------")
        print()
        print("Current Public Graph : ")
        self.public_graph.view_graph()
        self.state += [self.public_graph.special_copy()]
        self.strategies += [dict()]
        self.schedule.step()
        print()
        # Collect data
        #self.datacollector.collect(self)

    def run_model(self, step_count=10):
        for i in range(step_count):
            self.step(i)
            if self.check_equilibrium():
                break
        
        print("====================================== Debate Over ============================================")
        print("Final Value of the Issue : ", self.semantic.get_argument_value(self.public_graph.get_issue(), self.public_graph))

