from graphs import DebateGraph, OpinionGraph
from argument import Argument
import networkx as nx
from semantic import GradualSemantic, scoring_function_hbs

def test_1():
    for i in range(2, 25):
        g = DebateGraph()
        g.random_initialize(i)
        print()
        g.view_edges()
        print()

def test_2():
    g = DebateGraph()
    g.random_initialize(4, p=0.2)
    g.view_edges()
    print(g.get_size())


    print()
    s = g.create_subgraph()
    s.view_edges()


def test_3():
    g = DebateGraph()
    g.random_initialize(4, p=0.2, seed = 42)
    g.view_edges()
    print(g.get_size())

    s = OpinionGraph(g, Argument())
    print(s.get_size())


def test_scoring_no_weights():
    g = DebateGraph()
    g.random_initialize(4, p=0.2, seed = 42)
    g.view_edges()
    print()

    for i in range(5):
        S = scoring_function_hbs(g.get_issue(), i, g)
        print(S)

def test_scoring_weights():
    g = DebateGraph()
    g.random_initialize(4, p=0.2, seed = 43, weights=True, N = 5)
    g.view_edges()
    print()

    
    for a in g.get_graph().nodes:
        print(a)
        for i in range(5):
            S = scoring_function_hbs(a, i, g)
            print(S)
        print()


### Testing the Semantic Class

def test_semantic_no_weights():
    g = DebateGraph()
    g.random_initialize(1, p=0.2, seed = 43)
    g.view_edges()
    print()

    S = GradualSemantic(scoring_function_hbs, 100)

    for a in g.get_graph().nodes:
        print(a)
        V = S.get_argument_value(a, g)
        print(V)

def test_semantic_weights():
    g = DebateGraph()
    g.random_initialize(4, p=0.2, seed = 43, weights=True, N = 5)
    g.view_edges()
    print()
    
    S = GradualSemantic(scoring_function_hbs, 100)

    for a in g.get_graph().nodes:
            print(a)
            V = S.get_argument_value(a, g)
            print(V)


#test_semantic_no_weights()

arg = Argument()
def test_vote_propagation(arg):
    g = DebateGraph(arg)

    g.view_edges()

    arg.add_upvote()

    g.view_edges()

test_vote_propagation(arg)
print(arg)
