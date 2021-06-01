from graphs import DebateGraph
from semantic import GradualSemantic, scoring_function_hbs
from model import OnlineDebate
from graphs import DebateGraph
import random

from agents import DebateAgent
from learning import learn_all, learn_nothing


# Hyperparameters 
#seed = 11111

seed = 444

nb_of_iterations = 10
nb_of_arguments = 10
nb_agents = 5
p = 0.1
threshold = 0.5
learning_strategy = learn_all

# Initialization 
random.seed(seed)

Hbs = GradualSemantic(scoring_function_hbs, nb_of_iterations)

argument_graph = DebateGraph()
# for now for the tests 
argument_graph.random_initialize(nb_of_arguments, p=p)

debate_model = OnlineDebate(nb_agents, argument_graph, Hbs, threshold, learning_strategy=learning_strategy)
debate_model.run_model(100)

debate_model.public_graph.draw( debate_model.get_time(), "Final_graph")

