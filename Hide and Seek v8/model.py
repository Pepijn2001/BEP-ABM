from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
import numpy

from agent import Hider, Seeker, Patch


class HaS(Model):
    """
    Model heeft height en width als attributen. Plaatst 2 agenten op willekeurige cells.
    """

    def __init__(self, height, width, density=0.2, seed=3):
        super().__init__(seed=seed)

        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, torus=False)
        self.width = width
        self.height = height
        self.running = True
        self.found = False
        self.lost = False
        self.density = density

        for i, x, y in self.grid.coord_iter():  # patches maken
            pos = (x, y)
            agent_patch = Patch(pos, self, density)
            agent_patch.density = numpy.random.normal(density)
            self.grid.place_agent(agent_patch, pos)

        pos_hider = (20, 10)
        pos = (4, 29)
        end_nodes = [(4, 3), (26, 26), (26, 3), (3, 26)]

        hider_agent = Hider(1, self, pos_hider, age=10, speed = 50)
        seeker_agent = Seeker(2, self, pos, end_nodes, speed = 50)

        self.schedule.add(hider_agent)
        self.schedule.add(seeker_agent)

        self.grid.place_agent(hider_agent, pos_hider)
        self.grid.place_agent(seeker_agent, pos)

    def step(self):
        """
        Run one step of the model.
        """
        self.schedule.step()
        if self.found:
            self.running = False
