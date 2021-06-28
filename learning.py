
import random 

def learn_nothing(agent_pos, arg, graph, p=None):
    return False

def learn_all(agent_pos, arg, graph, p=None):
    return True

def learn_confirmation_bias(agent_opinion, current_issue_value, arg, graph, p = 0.9):
    """ This learning heuristic is based on the confirmation bias when evaluating new information. 
    Agents have more chance of learning arguments when they seem to favor their own opinion
    p : probablity that an agent will accept an argument if it is in his favor. 

    """
    arg_position = graph.get_oddity(arg)
    arg_value = random.random()

    if arg_position == 1: # if the argument defends the issue, its value needs to be less than 1- p for the agent not to acccept it
        if agent_opinion < current_issue_value and arg_value < p:
            return True
        elif agent_opinion > current_issue_value and arg_value > p:
                return True
        else:
            return False
            
    else:
        if agent_opinion > current_issue_value and arg_value < p:
            return True
        elif agent_opinion < current_issue_value and arg_value > p:
                return True
        else:
            return False