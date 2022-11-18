from mesa import Agent, Model
from mesa.space import ContinuousSpace
from mesa.time import RandomActivation

class FlockingAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
    def flock(self):
        neighbors = self.model.space.get_neighbors(self.pos, 4, False)
        if not neighbors:
            print("I have no neighbors")
        else:
            print("I have neighbors")
            
    def step(self):
        self.flock()
        
class FlockingModel(Model):
    def __init__(self, N, width, height):
        self.num_agents = N
        self.space = ContinuousSpace(width, height, True, 0, 0)
        self.schedule = RandomActivation(self)
        
        ##Create & place agents
        for i in range(self.num_agents):
            bird = FlockingAgent(i, self)
            self.schedule.add(bird)
            x = self.random.randrange(self.space.width)
            y = self.random.randrange(self.space.height)
            pos = x, y
            self.space.place_agent(bird, pos) 
            
    def step(self):
        self.schedule.step()

        
model = FlockingModel(10, 10, 10)
for i in range(10):
    model.step()