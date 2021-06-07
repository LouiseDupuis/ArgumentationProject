from graphs import DebateGraph, DebateTree
from semantic import GradualSemantic, scoring_function_hbs
from model import OnlineDebate
from graphs import DebateGraph
import random

from agents import DebateAgent
from learning import learn_all, learn_nothing
from voting import upvote_all, simple_voting_heuristic


# Hyperparameters 
#seed = 11111

seed = 450
#seed = None
nb_of_iterations = 10
nb_of_arguments = 15
nb_agents = 10
p = 0.1
threshold = 0.5
learning_strategy = learn_nothing
voting_strategy = simple_voting_heuristic
subgraph_creation = 'random'   #'custom' = all agents have a least one link to zero; 'random' = completely random
save_images = False

# Initialization 

random.seed(seed)

Hbs = GradualSemantic(scoring_function_hbs, nb_of_iterations)

argument_graph = DebateTree()
# for now for the tests 
argument_graph.random_initialize(nb_of_arguments)

debate_model = OnlineDebate(nb_agents, argument_graph, Hbs, threshold, learning_strategy=learning_strategy, voting_strategy = voting_strategy, subgraph_creation= subgraph_creation, save = save_images)
debate_model.run_model(100)

debate_model.public_graph.draw( debate_model.get_time(), "Final_graph", save = save_images)

