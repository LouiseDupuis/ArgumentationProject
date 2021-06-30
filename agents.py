from mesa import Agent
import random


class DebateAgent(Agent):
    """
    An agent participating in an online debate.
    """

    def __init__(self, unique_id, model, opinion_graph, learning_strategy, p_learn, voting_strategy, comfort_limit = 0.05 ):
        """
        Creates a new agent

        Args:
            opinion_graph : the agent's own set of arguments
            learning_strategy : the name (?) of the agent's learning strategy 
            
        """
        super().__init__(unique_id, model)
        self.opinion_graph = opinion_graph
        self.learning_strategy = learning_strategy
        self.p_learn = p_learn
        self.voting_strategy = voting_strategy
        self.opinion = None # opinion = value of the issue in the graph 
        self.comfort_limit = comfort_limit
        self.current_strategy = None
        self.name = unique_id

    
    def get_opinion(self, semantic):
        self.opinion = semantic.get_argument_value(self.opinion_graph.get_issue(), self.opinion_graph)
        return self.opinion

    

    def get_better_strategies(self, comfort_zone):
        """
        Iterating through all the possible moves to try to obtain moves that influence the debate
        """

        better_strategies = []

        original_value = self.model.current_value
        print('Public value : ', original_value )

        for arg in self.opinion_graph.nodes:
            if arg in self.model.strategy_evaluation.keys():
                #print("Testing argument ", arg)
                new_value = self.model.strategy_evaluation[arg]
                if abs(self.opinion - new_value) < abs(self.opinion - original_value):
                    print('New value : ', new_value)
                    edges = self.model.argument_graph.get_edges_between(arg, self.model.public_graph )
                    better_strategies += [(arg, edges)]
        return better_strategies
    
    def get_comfort_strategies(self):
        """ Identifying strategies that have a good chance to keep the debate inside the agent's comfort zone. 
        """
        comfort_strategies = []

        original_value = self.model.current_value
        print('Public value : ', original_value )

        for arg in self.opinion_graph.nodes:
            if arg in self.model.strategy_evaluation.keys():
                new_value = self.model.strategy_evaluation[arg]
                if new_value > self.opinion - self.comfort_limit and new_value < self.opinion + self.comfort_limit:
                    edges = self.model.argument_graph.get_edges_between(arg, self.model.public_graph )
                    comfort_strategies += [(arg, edges)]
        return comfort_strategies


    
  

    def __str__(self) -> str:
        return str(self.name)
    
    def __repr__(self):
        return self.__str__()
        


    def step(self):
        print()

        # get opinion 

        self.get_opinion(self.model.get_semantic())
        print("Agent's opinion : ", self.opinion )
        self.model.opinions[-1][self.name] = (self.opinion, self.comfort_limit, self.model.current_value)

        comfort_zone = [self.opinion - self.comfort_limit, self.opinion + self.comfort_limit]
        if self.model.current_value > comfort_zone[1] or self.model.current_value < comfort_zone[0]:
            # choosing amongst the better strategies 
            better_strategies = self.get_better_strategies(comfort_zone)
            if len(better_strategies) > 0:
                strategy = random.sample(better_strategies, 1)[0]
            else:
                strategy = 'NOTHING'
        else:
            #playing any move that allows the player to stay in her comfort zone
            comfort_strategies = self.get_comfort_strategies()
            if len(comfort_strategies) > 0:
                strategy = random.choice(comfort_strategies)
            else:
                strategy = 'NOTHING'
        print("Strategy : ", strategy[0])
        self.current_strategy = strategy
        
        return strategy
    
        
    
    def learn(self):
        
        """ 
        Learning Step, where the agent applies the learning policy to change its opinion
        """

        previous_graph = self.model.state[-1]
        new_arguments = self.model.public_graph.nodes - previous_graph.nodes
        unknown_arguments = new_arguments - self.opinion_graph.nodes

    
        for arg in unknown_arguments:
                if self.learning_strategy(self.opinion, self.model.current_value, arg, self.model.public_graph, p = self.p_learn):
                    print("AGENT ", self.name, "LEARNS ARGUMENT ", arg)
                    edges = self.model.public_graph.get_edges_between(arg, self.opinion_graph)
                    self.opinion_graph.add_node(arg)
                    self.opinion_graph.add_edges_from(edges)
    
    def vote(self): 

        previous_graph = self.model.state[-1]
        new_arguments = self.model.public_graph.nodes - previous_graph.nodes

        # upvoting the arguments which are in favor of the agent's goal
    
        for arg in new_arguments:
            if not self.model.public_graph.check_if_agent_already_voted(arg, self):
                if self.voting_strategy(self.opinion, self.model.current_value, arg, self.model.public_graph):
                    self.model.public_graph.add_upvote(arg, self)
                else:
                    self.model.public_graph.add_downvote(arg, self)

        
    def advance(self):
        # model implement strategy
        self.model.implement_strategy( self.current_strategy, self)

        
        
        
        

