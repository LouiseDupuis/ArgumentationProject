from itertools import count
import random


class Argument():

    _ids = count(0)

    def __init__(self, upvotes = 0, downvotes = 0):
        self.key = next(self._ids)
        self.upvotes = upvotes
        self.downvotes = downvotes 
        #self.weight = 0.5 # to modify ?? Probably the weight is computed somewhere else ? 

    def get_weight(self):
        if self.upvotes == self.downvotes == 0:
            return 1
        return max(self.upvotes - self.downvotes, 0)

    def __str__(self):
        return str(self.key) + " : " + str(self.upvotes) + " + " + str(self.downvotes) + " -"

    def random_votes(self, N):
        """ Used for tests. Initializes random votes between 0 and N.
        """
        self.upvotes = random.randint(0, N)
        self.downvotes = random.randint(0, N)
    
    def add_upvote(self):
        self.upvotes += 1
    
    def add_downvote(self):
        self.downvotes += 1
    
    
        
        