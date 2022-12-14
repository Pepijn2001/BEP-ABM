from mesa import Agent
import random

direction_list = [(-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0)]


"""
Hider agent kiest willekeurige cell in neighborhood en verplaatst.
"""


class Hider(Agent):
    def __init__(self, unique_id, model, pos, age, speed):
        super().__init__(unique_id, model)
        self.pos = pos
        self.pos_float = pos  # positie in grid en echte positie van agent
        self.found = False  # of de agent gevonden is
        self.cell_history = []  # wat het pad is dat de agent heeft gelopen, voor backtracking
        self.direction = ()  # richting van de agent
        self.speed = speed / 100  # snelheid van de agent

        # attributen die over strategie gaan
        self.lost = False  # of de agent verdwaald is en dus een bepaalde strategie gaat gebruiken
        self.age = age  # beïnvloedt strategie

        # nodig voor direction_traveling
        self.direction_chosen = False

        self.strategy = self.choose_strategy()

    def step(self):
        if not self.lost:
            self.direction = self.get_direction()
            self.pos_float = (self.pos_float[0] + self.direction[0], self.pos_float[1] + self.direction[1])
            rounded_pos = (round(self.pos_float[0]), round(self.pos_float[1]))
            self.model.grid.move_agent(self, rounded_pos)
            self.cell_history.append(self.pos_float)
            if self.random.random() < 0.1:
                self.lost = True
                self.model.lost = True
                self.direction_chosen = False
        else:
            self.random_walking()
            self.direction_traveling()
            self.staying_put()
            self.backtracking()

    def get_direction(self):
        self.direction = random.choice(direction_list)
        new_direction = tuple(self.speed * i for i in self.direction)
        return new_direction

    def choose_strategy(self):
        strategy_list = ["direction_traveling", "random_walking", "staying_put", "backtracking"]
        strategy = self.random.choice(strategy_list)
        return strategy

    def random_walking(self):
        if self.strategy == "random_walking":
            new_direction = self.get_direction()
            self.pos_float = (self.pos_float[0] + new_direction[0], self.pos_float[1] + new_direction[1])
            rounded_pos = (round(self.pos_float[0]), round(self.pos_float[1]))
            if not self.model.grid.out_of_bounds(rounded_pos):
                self.model.grid.move_agent(self, rounded_pos)

    def direction_traveling(self):
        if self.strategy == "direction_traveling":
            if not self.direction_chosen:
                self.direction = self.get_direction()
                self.direction_chosen = True
            if self.direction_chosen:
                self.pos_float = (self.pos_float[0] + self.direction[0], self.pos_float[1] + self.direction[1])
                rounded_pos = (round(self.pos_float[0]), round(self.pos_float[1]))
                if self.model.grid.out_of_bounds(rounded_pos):
                    self.strategy = "staying_put"
                else:
                    self.model.grid.move_agent(self, rounded_pos)

    def staying_put(self):
        if self.strategy == "staying_put":
            pass

    def route_traveling(self):
        pass

    def view_enhancing(self):
        pass

    def backtracking(self):
        if self.strategy == "backtracking" and len(self.cell_history) != 0:
            path = self.cell_history[::-1]
            self.pos_float = path[0]
            self.cell_history.pop()
            rounded_pos = (round(self.pos_float[0]), round(self.pos_float[1]))
            self.model.grid.move_agent(self, rounded_pos)


"""
Seeker agent kijkt of Hider in gezichtsveld is. Zo ja, beweegt ernaartoe, zo nee, beweegt willekeurig.
"""


class Seeker(Agent):
    def __init__(self, unique_id, model, pos, end_nodes, speed):
        super().__init__(unique_id, model)
        self.cell_history = []
        self.pos = pos
        self.pos_float = pos  # positie in grid en echte positie van agent
        self.direction = ()  # richting van de agent
        self.speed = speed / 100  # snelheid van de agent
        self.end_nodes = end_nodes  # lijst met end_nodes
        self.end_node_count = 0  # telt bij welk item in de lijst end_nodes_pos zijn
        self.radius = 3

        self.scanned_patches = []
        self.found = False

    def step(self):
        # Als de end node bereikt is moet alles gereset worden en naar
        # de volgende node in de lijst gekeken worden.

        if self.model.lost:
            if not self.found:
                if (round(self.pos_float[0]), round(self.pos_float[1])) == self.end_nodes[self.end_node_count]:
                    self.end_node_count += 1
                    if self.end_node_count == len(self.end_nodes):
                        self.model.running = False
                        return
                self.get_direction(self.end_nodes[self.end_node_count])
                new_direction = tuple(self.speed * i for i in self.direction)
                self.pos_float = (self.pos_float[0] + new_direction[0], self.pos_float[1] + new_direction[1])
                rounded_pos = (round(self.pos_float[0]), round(self.pos_float[1]))
                self.model.grid.move_agent(self, rounded_pos)
            else:
                self.model.running = False

            self.scanning()

    def get_direction(self, end_node):
        # transformeert de afstand naar nieuwe node naar een heading met x,y max 1
        direction = (end_node[0] - self.pos_float[0], end_node[1] - self.pos_float[1])
        print("End nodes", end_node[0], end_node[1])
        print("Float pos", self.pos_float[0], self.pos_float[1])
        self.direction = (direction[0]/max(abs(direction[0]), abs(direction[1]))), direction[1]/max(abs(direction[0]), abs(direction[1]))
        print(self.direction)

    def scanning(self):
        for cell in self.model.grid.iter_neighborhood(self.pos, True, True, 3):
            if cell not in self.scanned_patches:
                self.scanned_patches.append(cell)

            for agent in self.model.grid.get_cell_list_contents(cell):
                if type(agent) is Patch:
                    agent.seen = True
        # functie gaat elke richting af tot de radius van het zicht
        for direction in direction_list:
            pos = self.pos
            for _ in range(self.radius):
                # stapsgewijs wordt in elke richting gekeken of er een boom staat of niet, zo ja dan wordt
                # de loop gebroken en gaat hij door naar de volgende richting
                pos = ((pos[0] + direction[0]), (pos[1] + direction[1]))
                if not self.model.grid.out_of_bounds(pos):
                    hider = [agent for agent in self.model.grid.get_cell_list_contents(pos)
                             if isinstance(agent, Hider)]
                    # checkt of de persoon gevonden is
                    if len(hider) != 0:
                        self.found = True
                        self.end_nodes_pos = [hider[0].pos]
                        self.end_node_count = 0
                        self.start = self.pos
                        hider[0].found = True



class Patch(Agent):
    parent: object

    def __init__(self, pos, model, density, parent=None):
        super().__init__(pos, model)
        self.pos = pos
        self.seen = False
        self.density = density


    def step(self):
        pass
