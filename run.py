from graphs import DebateDAG, DebateGraph, DebateTree, FlatArgumentTree
from semantic import GradualSemantic, scoring_function_hbs
from model import OnlineDebate
from graphs import DebateGraph
import random

from agents import DebateAgent
from learning import learn_all, learn_confirmation_bias, learn_nothing
from voting import simple_voting_heuristic_opinion, upvote_all, simple_voting_heuristic
import pandas as pd 

# Hyperparameters 
#seed = 11111

seed = 449
#seed = None

nb_of_debates = 10

#for i in range(1,10):


nb_of_arguments = 5
#game_stats_position = pd.DataFrame(columns = ['Original Value', 'Final Value', 'Number of Agents', 'Orig. Number of PRO Agents', 'Final Number of PRO Agents', 'Nb Change of Mind', 'Steps', 'Nb of Arguments', 'Nb of Arguments of Agents', 'Final Nb of Arguments' ])
game_stats = pd.DataFrame(columns = ['Original Value', 'Final Value', 'Number of Agents', 'Nb Change of Mind', 'Steps', 'Nb of Arguments', 'Nb of Arguments of Agents', 'Final Nb of Arguments' ])

for d in range(nb_of_debates):

    # Hyperparameters 
    nb_of_iterations = nb_of_arguments*10
    #nb_of_arguments = 50
    nb_agents = 6
    learning_strategy = learn_confirmation_bias
    p = 0.5
    p_learn = 0.5
    voting_strategy = simple_voting_heuristic_opinion
    subgraph_creation = 'random'   #'custom' = all agents have a least one link to zero; 'random' = completely random
    show_images = False
    save_images = False
    comfort_limit = 0.05

    # Initialization 
    seed += 1
    random.seed(seed)

    Hbs = GradualSemantic(scoring_function_hbs, nb_of_iterations)

    argument_graph = DebateDAG()
    argument_graph.random_initialize(nb_of_arguments)

    debate_model = OnlineDebate(nb_agents, argument_graph, Hbs, comfort_limit, learning_strategy=learning_strategy, p_learn = p_learn, voting_strategy = voting_strategy, subgraph_creation= subgraph_creation, save = save_images, show_images = show_images)
    game_stats = debate_model.run_model(100, game_stats)
    
    #game_stats.to_excel('game_stats_'+ str(comfort_limit) +'_limit.xlsx')




