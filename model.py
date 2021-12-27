

from copy import Error
from re import S
from agents import DebateAgent
from graphs import DebateGraph
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from schedule import SimultaneousDebateActivation
import time 
from datetime import datetime
import pandas as pd
import copy
import shutil
import networkx as nx
import sys 

from pathlib import Path



class OnlineDebate(Model):
    """
    Model implementing the protocol for the Online Debate Games
    """


    description = (
        "A model for simulating online debates"
    )

    def __init__(
        self, num_agents, argument_graph, semantic, comfort_limit, learning_strategy, p_learn, voting_strategy, subgraph_creation, lightmode = True, protocol = 'complete', number_of_clones = 0
    ):
        """
        Create a new model with the given parameters.

        Args: num_agents = total number of agents
              argument_graph = the graph containing all of the possible arguments od the debate and their relationships
              semantic = a GradualSemantic object used to assess the argument's strength

              lightmode = When False, saves all of the information about the debate
            
        """
        super().__init__()
        # Set parameters

        self.num_agents = num_agents
        self.argument_graph = argument_graph
        self.semantic = semantic
        self.comfort_limit = comfort_limit
        self.subgraph_creation = subgraph_creation
        self.lightmode = lightmode
        self.p_learn = p_learn
        self.protocol = protocol 
        self.number_of_clones = number_of_clones

        self.public_graph = DebateGraph(argument_graph.get_issue())
        
        self.schedule = SimultaneousDebateActivation(self)

        self.time = str(datetime.now()).replace('.', '_').replace(':', '_') # a time marker to help save all relevant informations

        if not lightmode:
            Path("tmp/" + self.time).mkdir(parents=True, exist_ok=True)   # folder to stock the state files of the model during game iteration


        self.current_value = self.semantic.get_argument_value(self.public_graph.get_issue(), self.public_graph) # the current vlue of the issue in the public board

        self.state = [] # a list keeping track of or all states of the game - in lightmode, only the last state of the game 
        self.strategies = [] # a list keeping track of all of the agent's strategies during the game
        self.opinions = [] # a list keeping track of all of the agent's opinions during the game
        self.agent_argument_set = set() # the set containing all of the arguments known by the agents

        print("=============== MODEL INITIALIZATION =========================================")
        print()
        print("Global Argument Graph for the game : ")
        self.argument_graph.view_graph()  #printing graph on command line
        print("Value of the Issue : ", self.semantic.get_argument_value(self.argument_graph.get_issue(), self.argument_graph))
        
        # Create each agent and their opinion graph
        for i in range(self.num_agents - self.number_of_clones):
           
            if self.subgraph_creation == 'custom' or self.number_of_clones > 0:
                opinion_graph = argument_graph.create_subgraph_connected()
            elif self.subgraph_creation == 'random':
                opinion_graph = argument_graph.create_subgraph_new()
                
            if i == 0 :
                # on ajoute l'agent 0 
                self.agent_argument_set = self.agent_argument_set.union(set(list(opinion_graph.nodes)))
                agent = DebateAgent(i, model=self, opinion_graph = opinion_graph, learning_strategy=learning_strategy, p_learn = p_learn, voting_strategy=voting_strategy, comfort_limit=self.comfort_limit)
                self.schedule.add(agent)


                # on clone l'agent 0 
                for j in range(self.number_of_clones):
                    agent = DebateAgent(j + 1, model=self, opinion_graph = opinion_graph.deep_copy(), learning_strategy=learning_strategy, p_learn = p_learn, voting_strategy=voting_strategy, comfort_limit=self.comfort_limit)
                    self.schedule.add(agent)
            else:
                 agent = DebateAgent(i + self.number_of_clones, model=self, opinion_graph = opinion_graph, learning_strategy=learning_strategy, p_learn = p_learn, voting_strategy=voting_strategy, comfort_limit=self.comfort_limit)
                 self.agent_argument_set = self.agent_argument_set.union(set(list(opinion_graph.nodes)))
                 self.schedule.add(agent)



    


    def get_semantic(self):
        return self.semantic
    
    def get_time(self):
        return self.time
    
    def implement_strategy(self, strategy, agent):
        self.strategies[-1][agent.name] =  strategy
        if strategy != 'NOTHING':
            self.public_graph.add_node(strategy[0])
            self.public_graph.add_edges_from(strategy[1])

            if not self.protocol == 'simplified' :
                self.public_graph.add_upvote(strategy[0], agent)


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

    

    def get_merged_value(self, step = 0, beginning = False):

        # create the merged model and compute its value 
        merged_debate = self.argument_graph.deep_copy()
        all_nodes = copy.deepcopy(merged_debate.nodes)
        
        for arg in all_nodes:
            if arg not in self.agent_argument_set:
                merged_debate.remove_node(arg)
        # adding the votes in the merged version

        #if not self.protocol == 'simplified':
        for agent in self.schedule.agents:
            for arg in merged_debate.nodes:
                if beginning:
                    agent_debate = agent.opinion_graph
                elif not self.lightmode:
                    agent_debate = agent.state[step]
                else:
                    raise("The parameter beginning should be true when using lightmode")
                    
                if arg in agent_debate :
                    if arg != agent_debate.issue :
                        merged_debate.add_upvote(arg,agent)
                else:
                    merged_debate.add_downvote(arg,agent)
        merged_value = self.semantic.get_argument_value(merged_debate.get_issue(), merged_debate)

        del(all_nodes)
        
        return merged_value, merged_debate
        


        
    def step(self, i):
        print()
        print()
        print("------------------ Step ", i, "---------------------------------------")
        print()
        print("Current Public Graph : ")
        self.current_step = i
        self.public_graph.view_graph()
        
        if not self.lightmode:
             nx.write_gpickle(self.public_graph, "tmp/" + str(self.time) + "/" + str(i) + ".gpickle")
        
        self.state = [self.public_graph.deep_copy()]
        self.strategies += [dict()]
        self.opinions += [dict()]
        self.check_strategies()
        self.schedule.step()
        self.current_value = self.semantic.get_argument_value(self.public_graph.get_issue(), self.public_graph)

        print()
   

    def run_model(self, step_count):

        
        merged_value, merged_debate = self.get_merged_value(beginning = True)
        del(merged_debate)
        stats = {'O. V.' : round(self.semantic.get_argument_value(self.argument_graph.get_issue(), self.argument_graph),5), 'M.V.' : round(merged_value,5),'Nb Agents' : self.num_agents, 'Nb of Arguments' : len(self.argument_graph), 'Args of Agents' : len(self.agent_argument_set)}
        
        
        # agent's stats 
        if self.lightmode:
            intersect = self.argument_graph.nodes

            for agent in self.schedule.agents:
                stats['Agent ' + str(agent.name) + ' O.V.'] = round(self.semantic.get_argument_value(agent.opinion_graph.get_issue(), agent.opinion_graph), 5)
                stats['Agent ' + str(agent.name) + ' O. N. Args'] = len(agent.opinion_graph.nodes)
                intersect = set(intersect).intersection(agent.opinion_graph.nodes)

                stats['Agent ' + str(agent.name) + ' Opinion Influence Index'] = agent.influence_index(opinion = True)
                stats['Agent ' + str(agent.name) + ' Merged Influence Index'] = agent.influence_index(opinion = False)

                """for other_agent in self.schedule.agents:
                    if not other_agent.name == agent.name:
                        stats['Agent ' + str(agent.name) + ' Agent '+ str(other_agent.name) + " Common Arguments" ] = len(set(agent.opinion_graph.nodes).intersection(other_agent.opinion_graph.nodes))"""


                
            stats['Common Arguments'] = len(intersect)
        
        steps= 0
        for i in range(step_count):
            self.step(i)
            if self.check_equilibrium():
                steps = i
                break
        
        print("====================================== Debate Over ============================================")

        #updating the stats of the debate :
        stats['F. V.'] = round(self.semantic.get_argument_value(self.public_graph.get_issue(), self.public_graph),5)
        stats['Args Played'] = len(self.public_graph)
        stats['Steps'] = steps + 1

        stats['Comfort Limit'] = self.comfort_limit
        stats['P Favor Bias'] = self.p_learn[0]
        stats['P Against Bias'] = self.p_learn[1]

        # computing the nb of agents in their comfort zone 

        # at the beginning of the debate
        agents_in_comfort_zone = []
        for agent, opinion in self.opinions[0].items():
            op, comfort_limit, model_value = opinion
            if model_value >= op - comfort_limit and model_value <= op + comfort_limit:
                agents_in_comfort_zone += [agent]
        stats['C.Z. Step 0'] = len(agents_in_comfort_zone)

        # after the end of the debate
        agents_in_comfort_zone = []
        for agent in self.schedule.agents:
            op = agent.get_opinion(self.semantic)
            if self.current_value >=  op - agent.comfort_limit and self.current_value <= op + agent.comfort_limit:
                agents_in_comfort_zone += [agent]

        stats['C.Z. Final Step'] = len(agents_in_comfort_zone)

        # computing how many times in total agents changed their minds on the issue
        number_of_change_of_minds = 0
        for i in range(self.num_agents):
            opinion = self.opinions[0][i][0]
            for s in range(steps):
                new_opinion = self.opinions[s][i][0]
                if opinion != new_opinion:
                    number_of_change_of_minds += 1
                opinion = new_opinion
        stats['Arguments Learned'] = number_of_change_of_minds


        
        print("Final Value of the Issue : ", stats['F. V.'])
        print("Original Value of the Issue : ", stats['O. V.'])


        # getting the states back 
        if not self.lightmode: 
            self.state = []
            for i in range(steps + 1):
                self.state += [nx.read_gpickle("tmp/" + str(self.time) + "/" + str(i) + ".gpickle")]
            
            for agent in self.schedule.agents:
                agent.state = []
                for i in range(steps + 1):
                    agent.state += [nx.read_gpickle("tmp/" + self.time + "/ agent_" + str(agent.name) + "_" + str(i) + ".gpickle")]
            shutil.rmtree("tmp/")
        
        # computing the final merged value 
        stats['F.M.V.'] = round(self.get_merged_value(beginning = True)[0],5)
        stats['Nb Clones'] = self.number_of_clones


        # final stats for the agents 
        if self.lightmode:
            for agent in self.schedule.agents:
                stats['Agent ' + str(agent.name) + ' F.V.'] = round(self.semantic.get_argument_value(agent.opinion_graph.get_issue(), agent.opinion_graph), 5)
                stats['Agent ' + str(agent.name) + ' F. N. Args'] = len(agent.opinion_graph.nodes)

                stats['Agent ' + str(agent.name) + ' Dissatisfaction'] = abs(stats['Agent ' + str(agent.name) + ' F.V.'] - stats['F. V.']) 
            


        return stats


   