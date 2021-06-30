

from copy import Error
from re import S
from ArgumentationProject.agents import DebateAgent
from ArgumentationProject.graphs import DebateGraph
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from ArgumentationProject.schedule import SimultaneousDebateActivation
import time 
from datetime import datetime
import pandas as pd

class OnlineDebate(Model):
    """
    Model implementing the protocol for the Online Debate Games
    """


    description = (
        "A model for simulating online debates"
    )

    def __init__(
        self, num_agents, argument_graph, semantic, comfort_limit, learning_strategy, p_learn, voting_strategy, subgraph_creation, save, show_images
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
        self.comfort_limit = comfort_limit
        self.subgraph_creation = subgraph_creation
        self.save_images = save
        self.show_images = show_images

        self.public_graph = DebateGraph(argument_graph.get_issue())
        
        self.schedule = SimultaneousDebateActivation(self)

        self.time = datetime.now() # a time marker to help save all relevant informations

        self.current_value = self.semantic.get_argument_value(self.public_graph.get_issue(), self.public_graph) # the current vlue of the issue in the public board

        self.state = [] # a list keeping track of the last state of the game
        self.strategies = [] # a list keeping track of all of the agent's strategies during the game
        self.opinions = [] # a list keeping track of all of the agent's opinions during the game
        self.agent_argument_set = set() # the set containing all of the arguments known by the agents

        print("=============== MODEL INITIALIZATION =========================================")
        print()
        print("Global Argument Graph for the game : ")
        self.argument_graph.view_graph()  #printing graph on command line
        if show_images :
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
            self.agent_argument_set = self.agent_argument_set.union(set(list(opinion_graph.nodes)))
            
            agent = DebateAgent(i, model=self, opinion_graph = opinion_graph, learning_strategy=learning_strategy, p_learn = p_learn, voting_strategy=voting_strategy, comfort_limit=self.comfort_limit)
            if show_images:
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
    
    def check_strategies(self):
        """
        This function is implemented to save computing time in the case of big graphs. 
        All of the effects of the arguments in the agent's graphs are computed only once, then used by the agents to choose their strategy 
        """

        self.strategy_evaluation = dict()
        unpublished_arguments = self.agent_argument_set - self.public_graph.nodes
        for arg in unpublished_arguments:
            print("Testing argument ", arg)
            edges = self.argument_graph.get_edges_between(arg, self.public_graph)
            new_value = self.semantic.get_argument_effect(arg, edges, self.public_graph)
            print('New value : ', new_value)
            self.strategy_evaluation[arg] = new_value
        
        print("End of testing")
        print(self.current_value)
        return self.strategy_evaluation

    

    def get_merged_value(self):
        # create the merged model and compute its value 
        merged_debate = self.argument_graph.deep_copy()
        for arg in self.merged_debate.nodes:
            if arg not in self.agent_argument_set:
                merged_debate.remove_node(arg)
        # adding the votes in the merged version
        for agent in self.schedule.agents:
            for arg in self.merged_debate.nodes:
                if arg in agent.opinion_graph.nodes:
                    merged_debate.add_upvote(arg,agent)
                else:
                    merged_debate.add_downvote(arg,agent)
        merged_value = self.semantic.get_argument_value(merged_debate.get_issue(), merged_debate)
        del(merged_debate)
        return merged_value
        


        
    def step(self, i):
        print()
        print()
        print("------------------ Step ", i, "---------------------------------------")
        print()
        print("Current Public Graph : ")
        self.public_graph.view_graph()
        self.state = [self.public_graph.deep_copy()]
        self.strategies += [dict()]
        #self.positions += [dict()]
        self.opinions += [dict()]
        self.check_strategies()
        self.schedule.step()
        self.current_value = self.semantic.get_argument_value(self.public_graph.get_issue(), self.public_graph)
        print()
    
   

    def run_model(self, step_count, game_stats):

        stats = {'Original Value' : self.semantic.get_argument_value(self.argument_graph.get_issue(), self.argument_graph), 'Final Value' : None, 'Number of Agents' : self.num_agents, 'Nb Change of Mind' : None, 'Steps' : None, 'Nb of Arguments' : len(self.argument_graph), 'Nb of Arguments of Agents' : len(self.agent_argument_set), 'Final Nb of Arguments' : None}
        steps= 0
        for i in range(step_count):
            self.step(i)
            if self.check_equilibrium():
                steps = i
                break
        
        print("====================================== Debate Over ============================================")

        #updating the stats of the debate :
        stats['Final Value'] = self.semantic.get_argument_value(self.public_graph.get_issue(), self.public_graph)
        stats['Final Nb of Arguments'] = len(self.public_graph)
        stats['Steps'] = steps + 1

        # computing the nb of agents in their comfort zone 

        # at the beginning of the debate
        agents_in_comfort_zone = []
        for agent, opinion in self.opinions[0].items():
            op, comfort_limit, model_value = opinion
            if model_value >= op - comfort_limit and model_value <= op + comfort_limit:
                agents_in_comfort_zone += [agent]
        stats['Beginning - Nb of Agents in C. Z.'] = len(agents_in_comfort_zone)

        # after the end of the debate
        agents_in_comfort_zone = []
        for agent in self.schedule.agents:
            op = agent.get_opinion(self.semantic)
            if self.current_value >=  op - agent.comfort_limit and self.current_value <= op + agent.comfort_limit:
                agents_in_comfort_zone += [agent]

        stats['End -Nb of Agents in C. Z.'] = len(agents_in_comfort_zone)
        # computing how many times in total agents changed their minds on the issue
        number_of_change_of_minds = 0
        for i in range(self.num_agents):
            opinion = self.opinions[0][i][0]
            for s in range(steps):
                new_opinion = self.opinions[s][i][0]
                if opinion != new_opinion:
                    number_of_change_of_minds += 1
                opinion = new_opinion
        stats['Nb Change of Mind'] = number_of_change_of_minds

        stats_df = pd.DataFrame.from_records([stats])
        game_stats = pd.concat([game_stats, stats_df], sort=False).fillna(0)


        print("Final Value of the Issue : ", stats['Final Value'])
        print("Original Value of the Issue : ", stats['Original Value'])
        if self.show_images:
            self.public_graph.draw( self.get_time(), "Final_graph", save = self.save_images)
        return game_stats


   