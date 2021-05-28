from mesa import Agent
import random


class DebateAgent(Agent):
    """
    An agent participating in an online debate.
    """

    def __init__(self, unique_id, model, opinion_graph, learning_strategy, threshold ):
        """
        Creates a new agent

        Args:
            opinion_graph : the agent's own set of arguments
            learning_strategy : the name (?) of the agent's learning strategy 
            threshold : the threshold to determine an agent's position on the issue
        """
        super().__init__(unique_id, model)
        self.opinion_graph = opinion_graph
        self.learning_strategy = learning_strategy
        self.position = None
        self.threshold = threshold
        self.current_strategy = None
        self.name = unique_id
    


    def get_position(self, semantic, threshold):   
        """
        Computing the agent's position on the issue
        """  
        value = semantic.get_argument_value(self.opinion_graph.get_issue(), self.opinion_graph)
        if value > threshold:
            self.position = 'PRO'
        else:
            self.position = 'CON'
        return self.position
    

    def get_better_strategies(self, public_graph):
        """
        Iterating through all the possible moves to try to obtain moves that influence the debate
        """
        print()
        print( "Testing Strategies :")

        better_strategies = []
        original_value = self.model.semantic.get_argument_value(public_graph.get_issue(), public_graph )
        print('Original value : ', original_value )
        unpublished_arguments = self.opinion_graph.get_graph().nodes - public_graph.get_graph().nodes
        for arg in unpublished_arguments:
            print("Testing argument ", arg)
            edges = self.opinion_graph.get_edges_between(arg, public_graph )
            new_value = self.model.semantic.get_argument_effect(arg, edges, public_graph)
            print('New value : ', new_value)
            if self.position == 'PRO':
                if new_value > original_value:
                    better_strategies += [(arg, edges)]
            else:
                if new_value < original_value:
                    better_strategies += [(arg, edges)]
        
        return better_strategies
        


        

    def step(self):

        public_graph = self.model.public_graph
        print()

        # 1 : position
        self.get_position(self.model.get_semantic(), self.threshold)
        print("Agent's position : ", self.position )

        # choosing amongst the better strategies 
        better_strategies = self.get_better_strategies(public_graph)
        if len(better_strategies) > 0:
            strategy = random.sample(better_strategies, 1)[0]
        else:
             strategy = 'NOTHING'
        print("Strategy : ", strategy[0])
        self.current_strategy = strategy
        # model rememebers strategy

        # learning

        # voting
        
        return strategy
    
    def upvote(self, arg ):
        """ Upvoting an argument
        """ 
        arg.add_upvote()

    def downvote(self, arg ):
        """ Upvoting an argument
        """ 
        arg.add_downvote()
    
    def learn(self, arg, edges):
        self.opinion_graph.add_node(arg)
        self.opinion_graph.add_edges_from(edges)
    
    def learn_and_vote(self):
        print("Agent ", self.name, " is voting")
        unknown_arguments = self.model.public_graph.get_graph().nodes - self.opinion_graph.get_graph().nodes
        for arg in unknown_arguments:
            print(arg)
            if self.learning_strategy(arg):
                edges = public_graph.get_edges_between(arg, self.opinion_graph)
                self.learn(arg, edges)
                self.upvote(arg)
            else:
                self.downvote(arg)


    
    def advance(self):
        # model implement strategy
        self.model.implement_strategy( self.current_strategy)

        
        
        
        

