

def simple_voting_heuristic(agent_pos, arg, graph):
    if graph.get_oddity(arg) == 1:
        if agent_pos == 'PRO':
            return True
        else:
            return False
    else:
        if agent_pos == 'CON':
            return True
        else:
            return False


def simple_voting_heuristic_opinion(agent_opinion,  public_graph_value, arg, graph):
    if graph.get_oddity(arg) == 1:
        if agent_opinion > public_graph_value:
            return True
        else:
            return False
    else:
        if agent_opinion < public_graph_value:
            return True
        else:
            return False



def upvote_all(agent_pos, arg, graph):
    return True