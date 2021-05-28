
import networkx as nx
import random
from argument import Argument



class CustomDiGraph(nx.DiGraph):

    def special_copy(self):
        # A copy which changes the graph object but keeps the same node objects
        n = CustomDiGraph()
        n.add_nodes_from(self.nodes)
        n.add_edges_from(self.edges)
        return n





class DebateGraph():

    """ A Weighted, attack argumentation graph
         
        Parameters : 
            issue = the main issue of the debate
    """
    def __init__(self, issue = None, graph = None):

        if graph is not None:
            self.graph = graph
        else:
            self.graph = CustomDiGraph()
        self.issue = issue
        if self.issue is not None:
            self.add_node(issue)

    def get_graph(self):
        return self.graph
    
    def get_issue(self):
        return self.issue

    def get_size(self):
        # getting the size of the graph (including the issue)
        return len(list(self.graph.nodes))

    def add_node(self, node):
        self.graph.add_node(node)
    
    def add_edge(self, n1, n2):
        self.graph.add_edge(n1, n2)
    
    def add_nodes_from(self, nodes):
        self.graph.add_nodes_from(nodes)
    
    def add_edges_from(self, edges):
        self.graph.add_edges_from(edges)

    def get_attacking_nodes(self, a):
        return [edge[0] for edge in self.graph.in_edges(a)]
    
    def get_edges_between(self, a, graph):
        """ Getting all edges from argument a toward nodes that belong to another graph
        """
        in_edges = [e for e in self.get_graph().in_edges(a) if e[0] in graph.get_graph().nodes ]
        out_edges = [e for e in self.get_graph().out_edges(a) if e[1] in graph.get_graph().nodes ]
        return in_edges + out_edges


    
    def random_initialize(self, nb_args, p = 0.05, seed = None, weights = False, N = 0):
        """ A function to create a random argumentation graph with an issue and votes initialized to zero
            nb_args = number of arguments in the graph (excluding the issue)
            p = probability that an edge is added to the graph (in the Erdos-Renyi algorithm)
            seed = random seed for the generator
            weights = wether to initialize with random weights. Used for test
            N = used only if weights is True. Max number of positive or negative votes
        """

        self.issue = Argument()
        arguments = [Argument() for i in range(nb_args)]

        if weights:
            self.issue.random_votes(N)
            for arg in arguments:
                arg.random_votes(N)

        if seed is not None :
            random.seed(seed)

        def generate():
            self.graph = CustomDiGraph()
            # adding the issue and random attacks from arguments
            self.add_node(self.issue)
            self.add_nodes_from(arguments)

            for node1 in list(self.graph.nodes):
                for node2 in list(self.graph.nodes):
                    if node1 != node2:
                        if node1 != self.issue and random.random() < p:
                            self.add_edge(node1, node2)
                        if node2 != self.issue and random.random() < p:
                            self.add_edge(node2, node1)
        
        generate()
        # checking if the issue is attacked, if not generate a new graph until it is the case :
        issue_attacked = False
        while not issue_attacked:
            for edge in list(self.graph.edges):
                if edge[1] == self.issue:
                    return self.graph
                else:
                    if seed is not None:
                        seed += 1
                        random.seed(seed)
                    generate()





    def create_subgraph(self):

        """ This function creates a random DebateGraph object which is a subgraph of the parent graph 
        It is a connected graph which contains the issue 
        """

        # generating a random size for the subgraph
        S = random.randint(2, self.get_size())
        print("Size of subgraph : ", S)

        # Initialization
        current_node = self.issue
        s_graph = OpinionGraph(self, current_node)

        # building loop
        while s_graph.get_size() < S:

            #selecting a random edge 
            edges_toward_cn = [e for e in list(self.graph.in_edges(current_node)) if e[0] not in s_graph.graph.nodes]

            # if no edges exist, we add a random node from the rest of the graph
            if len(edges_toward_cn) == 0:
                complementaire = self.graph.nodes - s_graph.get_graph().nodes
                new_node = random.sample(list(complementaire), 1)[0]
            
            else : 
                edge = random.sample(edges_toward_cn, 1)[0]
                new_node = edge[0]
                #s_graph.add_edge(edge)

            s_graph.add_node(new_node)
            # getting all edges between the new node and the subgraph
            in_edges = [e for e in self.graph.in_edges(new_node) if e[0] in s_graph.get_graph().nodes]
            out_edges = [e for e in self.graph.out_edges(new_node) if e[1] in s_graph.get_graph().nodes]

            
            s_graph.add_edges_from(in_edges)
            s_graph.add_edges_from(out_edges)

            current_node = new_node
        
        return s_graph
 
    def view_edges(self):
        for edge in self.graph.edges:
            print(edge[0], " ===> ",edge[1])
        
        print("Nodes :")
        for node in self.graph.nodes:
            print(node)
    
    def copy(self):
        return DebateGraph(self.issue, self.graph.special_copy())


class OpinionGraph(DebateGraph):

    """ An opinion graph, subgraph of a DebateGraph, with no weights
    Parameters : 
            issue = the main issue of the debate
            parent : the parent DebateGraph
            ? Agent ? 
    """

    def __init__(self, parent, issue = None):
        super().__init__(issue)
        self.parent = parent

    def view_edges(self):
        return super().view_edges()







        