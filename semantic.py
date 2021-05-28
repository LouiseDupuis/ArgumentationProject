
import copy

class GradualSemantic():
    """ A gradual Semantic which can compute the overall strength of the arguments of a weighted graph
    """

    def __init__(self, scoring_function, nb_of_iterations):
        self.scoring_function = scoring_function
        self.nb_of_iterations = nb_of_iterations
    
    def get_argument_value(self, arg, debate_graph):
        for i in range(self.nb_of_iterations):
            f = self.scoring_function(arg, i, debate_graph)
        return f

    def get_argument_effect(self, arg, edges, debate_graph):
        """ Used in the agent's strategies : this function determines the effect of adding an argument and the corresponding edges 
        to a graph on the value of the issue
        """

        #original_value = self.get_argument_value(debate_graph.get_issue(), debate_graph)
        new_graph = debate_graph.copy()
        new_graph.add_node(arg)
        new_graph.add_edges_from(edges)
        new_value = self.get_argument_value(new_graph.get_issue(), new_graph)

        return new_value


def scoring_function_hbs(a, i, debate_graph):
    """
    Scoring function of the Weighted h-Categorizer Semantic (Hbs).
    This function is recursive. Its limit when i --> infinity is the overall strength of argument a
    params :
        a = an argument
        i = the index of the step
        debate_graph = an instance of the DebateGraph class
        weights = wether to take into account the graph's weights or consider it as a flat graph
    """
    if i == 0:
        return a.get_weight()
    B = debate_graph.get_attacking_nodes(a)
    if len(B) == 0:
        return a.get_weight()
    f = a.get_weight() / (1 + sum([scoring_function_hbs(b, i-1, debate_graph) for b in B]))
    return f


