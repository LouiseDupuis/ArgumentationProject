
import networkx as nx
import random
from argument import Argument
from networkx.classes.function import set_node_attributes
import copy
import matplotlib.pyplot as plt
import re
from pathlib import Path
import math


def sigmoid(x):
  return 1 / (1 + math.exp(-x))



class DebateGraph(nx.DiGraph):

    """ A Weighted, attack argumentation graph
         
        Parameters : 
            issue = the main issue of the debate
    """
    def __init__(self, issue = None, nodes = None):

        super().__init__(nodes)
        self.issue = issue
        if self.issue is not None:
            self.add_nodes_from([(issue, {"upvotes": 0, "up_list" : [], "downvotes" : 0, "down_list" : []})])

    
    def get_issue(self):
        return self.issue

    def get_size(self):
        # getting the size of the graph (including the issue)
        return len(list(self.nodes))

    
    def get_edges_between(self, a, graph):
        """ Getting all edges from argument a toward nodes that belong to another graph
        """
        in_edges = [e for e in self.in_edges(a) if e[0] in graph.nodes ]
        out_edges = [e for e in self.out_edges(a) if e[1] in graph.nodes ]
        return in_edges + out_edges
    

    def get_argument_weight(self, arg):
        if arg == self.issue:
            return 0.75
        upvotes = self.nodes[arg]["upvotes"]
        downvotes = self.nodes[arg]["downvotes"]
        if upvotes == downvotes == 0:
            return 0.5 # to avoid division by zero
        return sigmoid( 2.5 * (upvotes - downvotes)/(upvotes + downvotes))
    
    
    def add_upvote(self, arg, agent):
        upvotes = self.nodes[arg]["upvotes"]
        downvotes = self.nodes[arg]["downvotes"]
        up_list = self.nodes[arg]["up_list"]
        down_list = self.nodes[arg]["down_list"]
        set_node_attributes(self, {arg: { "upvotes" : upvotes + 1, "up_list" : up_list +  [agent], "downvotes" : downvotes, "down_list" : down_list}})
    
    def add_downvote(self, arg, agent):
        upvotes = self.nodes[arg]["upvotes"]
        downvotes = self.nodes[arg]["downvotes"]
        up_list = self.nodes[arg]["up_list"]
        down_list = self.nodes[arg]["down_list"]
        set_node_attributes(self, {arg: { "upvotes" : upvotes,"up_list" : up_list, "downvotes" : downvotes + 1, "down_list" : down_list + [agent]}})
    
    def check_if_agent_already_voted(self, arg, agent):
        if agent not in self.nodes[arg]["up_list"] and agent not in self.nodes[arg]["down_list"]:
            return False
        return True


    
    def random_initialize(self, nb_args, p = 0.05, seed = None):
        """ A function to create a random argumentation graph with an issue and votes initialized to zero
            nb_args = number of arguments in the graph (excluding the issue)
            p = probability that an edge is added to the graph (in the Erdos-Renyi algorithm)
            seed = random seed for the generator
        """

        #self.issue = Argument()
        #arguments = [Argument() for i in range(nb_args)]

        self.issue = 0
        arguments = [(i, {"upvotes": 0, "up_list" : [], "downvotes" : 0, "down_list" : []}) for i in range( nb_args)]

        if seed is not None :
            random.seed(seed)

        def generate():
            # adding the issue and random attacks from arguments
            self.add_nodes_from(arguments)

            for node1 in list(self.nodes):
                for node2 in list(self.nodes):
                    if node1 != node2:
                        if node1 != self.issue and random.random() < p:
                            self.add_edge(node1, node2)
                        if node2 != self.issue and random.random() < p:
                            self.add_edge(node2, node1)
        
        generate()
        # checking if the issue is attacked, if not generate a new graph until it is the case :
        issue_attacked = False
        while not issue_attacked:
            if len(list(self.predecessors(self.issue))) > 0:
                return self
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
        
        s_graph = OpinionGraph(self, self.issue)
        current_node = self.issue

        # building loop
        while s_graph.get_size() < S-1:

            #selecting a random edge 
            edges_toward_cn = [e for e in list(self.in_edges(current_node)) if e[0] not in s_graph.nodes]

            # if no edges exist, we add a random node from the rest of the graph
            if len(edges_toward_cn) == 0:
                complementaire = self.nodes - s_graph.nodes
                new_node = random.sample(list(complementaire), 1)[0]
            
            else : 
                edge = random.sample(edges_toward_cn, 1)[0]
                new_node = edge[0]
                #s_graph.add_edge(edge)

            s_graph.add_node(new_node)
            # getting all edges between the new node and the subgraph
            in_edges = [e for e in self.in_edges(new_node) if e[0] in s_graph.nodes]
            out_edges = [e for e in self.out_edges(new_node) if e[1] in s_graph.nodes]

            
            s_graph.add_edges_from(in_edges)
            s_graph.add_edges_from(out_edges)

            current_node = new_node
        
        return s_graph
    
    def create_subgraph_new(self):
        # generating a random size for the subgraph
        S = random.randint(2, self.get_size())
        print("Size of subgraph : ", S)
        random_nodes = random.sample(list(self.nodes - set([self.issue ])), S -1)
        sub_graph = copy.deepcopy(self.subgraph(random_nodes + [self.issue]))
        return OpinionGraph(self, self.issue, sub_graph)

    
    def print_arg(self, arg):
        print(arg, " ", self.nodes[arg]["upvotes"], "+ ",self.nodes[arg]["up_list"], " | ", self.nodes[arg]["downvotes"], " -", self.nodes[arg]["down_list"])
 
    def view_graph(self):
        print("Arguments :")
        for arg in self.nodes:
            self.print_arg(arg)
        print("Edges")
        for edge in self.edges:
            print(edge[0], " ===> ",edge[1])
    
    def draw(self, time, title, save = False):
        """
        This function draws a graph and saves the image
        """
        path = 'Figs/' + re.sub(  "\:", "_", str(time)) + '/'   # sub to avoid filename errors
        if save:
            Path(path).mkdir(parents=True, exist_ok=True)
        plt.figure(figsize=(10,5))
        ax = plt.gca()
        ax.set_title(title)
        nx.draw(self, pos=nx.spring_layout(self), labels = {n:str(n) for n in self.nodes})
        if save:
            plt.savefig( path +title + '.png', format ="PNG" )
        plt.show()
         

        
    
    def __str__(self) -> str:
        return str(self.issue) + str(self.nodes)
        
        
    
    def special_copy(self):
        # A copy which changes the graph object but keeps the same node objects
        """n = DebateGraph(issue = self.issue)
        n.add_nodes_from(self.nodes)
        n.add_edges_from(self.edges)"""
        return copy.deepcopy(self)
    
    def add_node(self, node):
        if node not in self:
            self.add_nodes_from([(node, {"upvotes": 0, "up_list" : [], "downvotes" : 0, "down_list" : []})])
    
    def get_oddity(self, arg):
        """ Returns 1 if the sequence from the arg to the issue is odd, 0 if it is even
        odd -> defense node
        even -> attack node
        """

        paths = [ p for p in nx.all_simple_paths(self, source=arg, target=self.issue)]
        # select a random path (bounded rationality)

        path = random.sample(paths, 1)[0]
        print("PATH from ", arg, " to ", self.issue, " : ", path)
        return len(path) % 2

    



class OpinionGraph(DebateGraph):

    """ An opinion graph, subgraph of a DebateGraph, with no weights
    Parameters : 
            issue = the main issue of the debate
            parent : the parent DebateGraph
            ? Agent ? 
    """

    def __init__(self, parent, issue = None, nodes = None):
        super().__init__(issue, nodes)
        self.parent = parent

    def view_graph(self):
        return super().view_graph()
    
    def get_argument_weight(self, arg):
        return 1





class DebateTree(DebateGraph):

    def __init__(self, issue = None, nodes = None):
        super().__init__(issue=issue, nodes=nodes)
    

    def random_initialize(self, nb_args, seed = None):
        #return super().random_initialize(nb_args, p=p, seed=seed)

        """
        Function to randomly generated a rooted tree, where the root is the issue, and all edges point towards it. 
        Method : we generate a random free tree and then root it. 
        """

        self.issue = 0
        random_tree = nx.generators.trees.random_tree(nb_args, seed)
        arguments = [(n, {"upvotes": 0, "up_list" : [], "downvotes" : 0, "down_list" : []}) for n in range(nb_args)]
        self.add_nodes_from(arguments)

        # rooting by performing a depth first search and then reversing the direction of the edges
        for edge in nx.algorithms.traversal.depth_first_search.dfs_edges(random_tree, source= self.issue):
            self.add_edge(edge[1], edge[0])
        







