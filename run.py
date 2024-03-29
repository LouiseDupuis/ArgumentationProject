#from ArgumentationProject.graphs import DebateDAG, DebateGraph, DebateTree, FlatArgumentTree
#from ArgumentationProject.semantic import GradualSemantic, scoring_function_hbs
#from ArgumentationProject.model import OnlineDebate
#from ArgumentationProject.graphs import DebateGraph
from networkx.algorithms.shortest_paths.weighted import multi_source_dijkstra_path_length
from graphs import DebateDAG, DebateGraph, DebateTree
from semantic import GradualSemantic, scoring_function_hbs
from model import OnlineDebate
from graphs import DebateGraph
import random

from learning import learn_all, learn_confirmation_bias, learn_nothing
from voting import simple_voting_heuristic_opinion, upvote_all, simple_voting_heuristic
import pandas as pd 

import numpy as np


def run_debate(nb_agents, nb_of_arguments, lightmode = True, comfort_limit = 0.05, p_favor_bias = 0.5,
    p_against_bias = 0.5, seed = 450, protocol = 'complete', number_of_clones = 0):

    """ One debate simulation. 
    gamestats : a dataframe where the stats of this debate will be added
    lightmode = if Tue, keeps the program light by not keeping in memory all of the debate information - useful when analysing hundreds of debates 
    """

    if seed is not None:
        random.seed(seed)
    

    id = str(nb_of_arguments) + '_' + str(nb_agents) + '_' + str(comfort_limit) + '_' + str(p_favor_bias) + '_' + str(p_against_bias) + '_' + str(seed) + '_' + str(number_of_clones)


    # Hyperparameters
    nb_of_iterations = int(nb_of_arguments*1.3)

    learning_strategy = learn_confirmation_bias
    #p = 0.5
    voting_strategy = simple_voting_heuristic_opinion
    subgraph_creation = 'random'   #'custom' = all agents have a least one link to zero; 'random' = completely random
    Hbs = GradualSemantic(scoring_function_hbs, nb_of_iterations)

    argument_graph = DebateTree()
    argument_graph.random_initialize(nb_of_arguments)

    debate_model = OnlineDebate(nb_agents, argument_graph, Hbs, comfort_limit, learning_strategy=learning_strategy, 
                        p_learn = (p_favor_bias, p_against_bias), voting_strategy = voting_strategy, subgraph_creation= subgraph_creation, 
                        lightmode=lightmode, protocol=protocol, number_of_clones = number_of_clones)
    stats = debate_model.run_model(100)

    stats['ID'] = id
    
    #game_stats.to_excel('game_stats_'+ str(comfort_limit) +'_limit.xlsx')
    return debate_model, stats


def run_debate_id(id, lightmode = False, protocol = 'complete'):

    """ Run a debate identified by its unique id 
    id format : " nb_agents_nb_of_arguments_comfort_limit_p_favor_bias_p_against_bias_seed"
    """

    params = id.split("_")
    print(params)
    nb_of_arguments = int(params[0])
    nb_agents = int(params[1])
    comfort_limit = float(params[2])
    p_favor_bias = float(params[3])
    p_against_bias = float(params[4])
    seed = int(params[5])
    number_of_clones = int(params[6])
    

    debate_model, stats = run_debate(nb_agents = nb_agents, nb_of_arguments = nb_of_arguments, lightmode = lightmode, comfort_limit = comfort_limit, p_favor_bias = p_favor_bias, p_against_bias = p_against_bias, seed =seed, protocol = protocol,
    number_of_clones = number_of_clones)
    
    #game_stats.to_excel('game_stats_'+ str(comfort_limit) +'_limit.xlsx')

    stats['ID'] = id
    return debate_model, stats
 



if __name__ == '__main__':

    protocol = 'complete'
    number_of_debates = 1000
    number_of_arguments = 20
    number_of_agents = 7
    number_of_clones = 0

    max_comfort_limit = 1
    min_comfort_limit = 0.0001
    

    seed = 1000

    comfort_limit = 0.05
    p_favor_bias, p_against_bias = 0.5,0.5


    game_stats = pd.DataFrame()

    for i in range(number_of_debates):

        #comfort_limit = random.uniform(min_comfort_limit, max_comfort_limit)
        

        #p_favor_bias =  random.SystemRandom().uniform(0,1)
        #p_against_bias = max(p_favor_bias - 0.1, 0)
        #p_against_bias = random.SystemRandom().uniform(0,p_favor_bias) 
        

        #number_of_clones = random.randint(0,6) 


        debate_model, stats = run_debate(number_of_agents,number_of_arguments, lightmode=True, p_favor_bias = p_favor_bias, p_against_bias = p_against_bias, comfort_limit = comfort_limit, seed = seed, protocol = protocol, number_of_clones=number_of_clones)
        del(debate_model)

        stats_df = pd.DataFrame.from_records([stats])
        game_stats = pd.concat([game_stats, stats_df], sort=False).fillna(0)


        
        
        if i % 50 == 0:
            game_stats.to_excel('Game_Stats_complete.xlsx')
        
            #seed += 1

        seed += 1
    
        
        




