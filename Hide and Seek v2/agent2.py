import math

from mesa import Agent

"""
Hider agent kiest willekeurige cell in neighborhood en verplaatst.
"""

class Hider(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
        self.found = False
        self.id = unique_id

    def step(self):
        if self.model.found == False:
            neighborhood = self.model.grid.get_neighborhood(self.pos, True, True)
            new_pos = (self.random.choice(neighborhood))
            self.model.grid.move_agent(self, new_pos)


"""
Seeker agent kijkt of Hider in gezichtsveld is. Zo ja, beweegt ernaartoe, zo nee, beweegt willekeurig.
"""
class Seeker(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
        self.id = unique_id
        self.cell_history = []
        self.in_range = False
        self.target = 0

    def step(self):
        neighbors = self.model.grid.get_neighbors(self.pos, True, False, 3)
        """
        Als Seeker iemand in het zicht heeft, vergelijkt hij alle cells met de afstand naar Hider en
        kiest deze een cell om naar te bewegen die de afstand kleiner maakt.
        """
        for neighbor in neighbors:
            if type(neighbor) is Hider:
                self.in_range = True
                self.target = neighbor.pos
                self.shortest_path()
                self.update_patch()

                for i in self.model.grid.get_cell_list_contents(self.pos):
                    if type(i) is Hider:
                        self.model.found = True
                        break
                break


        if self.in_range == False:
            self.update_patch()

            self.move()


    def move(self):

        neighborhood = self.model.grid.get_neighborhood(self.pos, True, True)
        potential_cells = {}
        potential_cell_history = self.cell_history
        for cell in neighborhood:
            for x in self.model.grid.iter_neighborhood(cell, True, True, 3):
                potential_cell_history.append(x)
            new_potential_cell_history = list(dict.fromkeys(potential_cell_history))
            potential_cells[cell] = len(new_potential_cell_history)
            potential_cell_history = self.cell_history

        new_cell = max(potential_cells, key=potential_cells.get)

        if new_cell == self.pos:  ###Werkt niet goed, kan geen nieuwe cell vinden als hij 'vast' zit
            potential_cells = self.cell_history
            for cell in self.model.cell_list:
                if cell in potential_cells:
                    potential_cells.remove(cell)
            self.target = self.random.choice(potential_cells)
            self.shortest_path()

        else:
            self.model.grid.move_agent(self, new_cell)

    def update_patch(self):
        for cell in self.model.grid.iter_neighborhood(self.pos, True, True, 3):
            self.cell_history.append(cell)
            for i in self.model.grid.get_cell_list_contents(cell):
                if type(i) is Patch:
                    i.seen = True

    def shortest_path(self):
        best_cell = None
        previous_distance = 10000
        for x, y in self.model.grid.iter_neighborhood(self.pos, True, False):

            cell_pos = x, y
            distance = math.sqrt(((cell_pos[0] - self.target[0]) ** 2) +
                                 ((cell_pos[1] - self.target[1]) ** 2))
            if distance <= previous_distance:
                best_cell = cell_pos
                previous_distance = distance
        self.model.grid.move_agent(self, best_cell)

class Patch(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos
        self.seen = False

    def step(self):
        pass