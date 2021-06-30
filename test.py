from ArgumentationProject.graphs import DebateDAG, DebateGraph, OpinionGraph
import networkx as nx
from ArgumentationProject.semantic import GradualSemantic, scoring_function_hbs
from ArgumentationProject.model import OnlineDebate

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

    
    for a in g.nodes:
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

    for a in g.nodes:
        print(a)
        V = S.get_argument_value(a, g)
        print(V)

def test_semantic_weights():
    g = DebateGraph()
    g.random_initialize(4, p=0.2, seed = 43, weights=True, N = 5)
    g.view_edges()
    print()
    
    S = GradualSemantic(scoring_function_hbs, 100)

    for a in g.nodes:
            print(a)
            V = S.get_argument_value(a, g)
            print(V)


#test_semantic_no_weights()

def test_vote_propagation(arg):
    g = DebateGraph(arg)

    g.view_edges()

    arg.add_upvote()

    g.view_edges()


def test_newg():
    g = DebateGraph()
    g.random_initialize(3)

    g.view_edges()
    print(g.nodes)
    print(g.nodes[g.get_issue()])

def test_graph_copy():
    g = DebateGraph()
    g.random_initialize(3)

    g.view_graph()
    n = g.special_copy()
    n.view_graph()


def test_previous_graph():
    g = DebateGraph()
    print(g)
    g.random_initialize(3)
    Hbs = GradualSemantic(scoring_function_hbs, 10)

    m = OnlineDebate(2, g, Hbs, 0.5)
    m.run_model(3)
    print(m.get_previous_graph())
    print(m.state)
    print(m.state[0])
    print(m.state[-1])


def test_DAG():
    n = 7
    p = 0.5
    seed = 40
    argument_graph = DebateDAG()
    argument_graph.random_initialize(n,p=p, seed = seed, connected=False)
    #argument_graph.view_graph()
    argument_graph.draw()
    argument_graph.random_initialize(n,p=p, seed = seed, connected=True)
    argument_graph.draw()

test_DAG()