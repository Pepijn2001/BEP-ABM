from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import Hider, Seeker, Patch


class HaS(Model):
    """
    Model heeft height en width als attributen. Plaatst 2 agenten op willekeurige cells.
    """

    def __init__(self, height, width, seed=None):
        super().__init__(seed=seed)

        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, torus=False)
        self.running = True
        self.found = False

        pos_hider = self.grid.find_empty()

        self.cell_list = []
        for i, x, y in self.grid.coord_iter():
            pos = (x,y)
            self.cell_list.append(pos)

        for i, x, y in self.grid.coord_iter():
            pos = (x,y)
            cost = 1
            agent = Patch(pos, self,cost)
            self.grid.place_agent(agent, pos)



        start_pos = (4,29)
        end_nodes = [(4,3), (26,26), (26,3), (3,26)]

        Hider_agent = Hider(1, self, pos_hider)
        Seeker_agent = Seeker(2, self, pos, start_pos, end_nodes)

        self.schedule.add(Hider_agent)
        self.schedule.add(Seeker_agent)

        self.grid.place_agent(Hider_agent, pos_hider)
        self.grid.place_agent(Seeker_agent, start_pos)


    def step(self):
        """
        Run one step of the model.
        """
        self.schedule.step()
        if self.found == True:
            self.running = False
