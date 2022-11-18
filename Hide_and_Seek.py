#!/usr/bin/env python
# coding: utf-8

# In[14]:


from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import math


class HaS(Model):
    def __init__(self, height, width, seed=None):
        super().__init__(seed=seed)
        
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, torus=True)
        
        pos_hider = self.grid.find_empty()
        pos_seeker = self.grid.find_empty()
        
        Hider_agent = Hider(1, self, pos_hider)
        Seeker_agent = Seeker(2, self, pos_seeker)
        
        self.schedule.add(Hider_agent)
        self.schedule.add(Seeker_agent)
        
        self.grid.place_agent(Hider_agent, pos_hider)
        self.grid.place_agent(Seeker_agent, pos_seeker)
        
    def step(self):
        """
        Run one step of the model.
        """
        self.schedule.step()
        
class Hider(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
        self.found = False
    
    
    
    def step(self):
        neighborhood = self.model.grid.get_neighborhood(self.pos, True, True)
        self.model.grid.move_agent(self, self.random.choice(neighborhood)) 
                        
class Seeker(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
        self.found = False
        
    def step(self):
        neighbors = self.model.grid.get_neighbors(self.pos, True, False, 3)
        if neighbors:
            neighbor = neighbors[0]
            neighbor_position = neighbor.pos
            best_cell = None
            previous_distance = 10000
            for x,y in self.model.grid.iter_neighborhood(self.pos, True, False):
                
                cell_pos = x,y
                distance = math.sqrt( ((cell_pos[0]-neighbor_position[0])**2)+((cell_pos[1]-neighbor_position[1])**2) )
                if distance <= previous_distance:
                    best_cell = cell_pos
                    previous_distance = distance
            self.model.grid.move_agent(self, best_cell)
            
        else:
            neighborhood = self.model.grid.get_neighborhood(self.pos, True, True)
            self.model.grid.move_agent(self, self.random.choice(neighborhood))
            
    


# In[13]:





# In[ ]:




