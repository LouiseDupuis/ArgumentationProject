
import random 

def learn_nothing(agent_pos, arg, graph, p=None):
    return False

def learn_all(agent_pos, arg, graph, p=None):
    return True

def learn_confirmation_bias(agent_opinion, current_issue_value, arg, graph, p_favor_bias = 0.9, p_against_bias = 0.1):
    """ This learning heuristic is based on the confirmation bias when evaluating new information. 
    Agents have more chance of learning arguments when they seem to favor their own opinion
    p : probablity that an agent will accept an argument if it is in his favor. 

    """
    arg_position = graph.get_oddity(arg)
    arg_value = random.random()
    avg_learning_proba = (p_against_bias+ p_favor_bias)/2 

    if agent_opinion == current_issue_value and arg_value < avg_learning_proba:
        return True

    if arg_position == 1: # if the argument defends the issue
        if agent_opinion < current_issue_value and arg_value < p_favor_bias:
            return True
        elif agent_opinion > current_issue_value and arg_value < p_against_bias:
                return True
        else:
            return False
            
    else: # if the argument attacks the issue 
        if agent_opinion > current_issue_value and arg_value < p_favor_bias:
            return True
        elif agent_opinion < current_issue_value and arg_value < p_against_bias:
                return True

        else:
            return False