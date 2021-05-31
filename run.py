from graphs import DebateGraph
from semantic import GradualSemantic, scoring_function_hbs
from model import OnlineDebate
from graphs import DebateGraph
import random

from agents import DebateAgent

# Hyperparameters 
#seed = 11111

seed = 444

nb_of_iterations = 10
nb_of_arguments = 6
nb_agents = 3
p = 0.1
threshold = 0.5

# Initialization 
random.seed(seed)

Hbs = GradualSemantic(scoring_function_hbs, nb_of_iterations)

argument_graph = DebateGraph()
# for now for the tests 
argument_graph.random_initialize(nb_of_arguments, p=p)

debate_model = OnlineDebate(nb_agents, argument_graph, Hbs, threshold)
debate_model.run_model(100)

