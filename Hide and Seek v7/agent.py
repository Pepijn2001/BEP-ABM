from mesa import Agent
import random
import math

direction_list = [(-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0)]


def find_path(self):
    # Patch agent vinden voor start en einde, functie van Mesa geeft lijst met
    # alle agents, dus ook evt. Hider en Seeker
    end_node = [agent for agent in self.model.grid.get_cell_list_contents([self.end_nodes_pos[self.end_node_count]])
                if isinstance(agent, Patch)][0]
    start_node = [agent for agent in self.model.grid.get_cell_list_contents([self.start])
                  if isinstance(agent, Patch)][0]

    # Open en closed lijsten maken, start- en eindnode waardes aanmaken, start_node parent op None
    # omdat deze nog opgeslagen is na een eerste zoekronde
    open_list = []
    closed_list = []
    start_node.parent = None

    start_node.g = start_node.h = start_node.f = 0
    end_node.g = end_node.h = end_node.f = 0

    open_list.append(start_node)

    # Als de open lijst op 0 staat is er geen weg naar de eindnode
    while len(open_list) > 0:
        current_node = open_list[0]
        current_index = 0

        # Kijken wat de beste node is o.b.v. f-waarde
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Current node uit open lijst halen en in closed lijst
        open_list.pop(current_index)

        closed_list.append(current_node)

        # Checken of eindbestemming bereikt is en met terugwerkende kracht
        # route vinden
        if current_node == end_node:
            path = []
            current = current_node

            while current.parent is not None:
                path.append(current.pos)
                current = current.parent

            return path[::-1]

        # Children aanmaken voor current node om zo potentiële nieuwe nodes
        # te vinden
        children = []
        for new_position in self.model.grid.get_neighborhood(current_node.pos, True, False):

            new_nodes = self.model.grid.get_cell_list_contents(new_position)
            new_node = [agent for agent in new_nodes if isinstance(agent, Patch)][0]

            if new_node.tree:
                continue
            children.append(new_node)

        # Voor elk kind worden relevante waardes berekend en gecheckt of ze al
        # in open/closed lijst zitten. 'Continue_function' gebruikt omdat continue
        # niet goed werkte.
        for child in children:
            continue_function = False

            for closed_child in closed_list:
                if child == closed_child:
                    continue_function = True
            if continue_function:
                continue

            child.g = current_node.g + 1
            child.h = (((child.pos[0] - end_node.pos[0]) ** 2) +
                       ((child.pos[1] - end_node.pos[1]) ** 2))
            child.f = child.g + child.h

            # Child wordt alleen niet toegevoegd aan de lijst als het een
            # oude 'generatie' is
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    continue_function = True
            if continue_function:
                continue

            # Child wordt toegevoegd aan de open list en de parent node
            # wordt toegevoegd
            open_list.append(child)
            child.parent = current_node


"""
Hider agent kiest willekeurige cell in neighborhood en verplaatst.
"""


class Hider(Agent):
    def __init__(self, unique_id, model, pos, age, speed):
        super().__init__(unique_id, model)
        self.pos, self.pos_float = pos  # positie in grid en echte positie van agent
        self.found = False  # of de agent gevonden is
        self.cell_history = []  # wat het pad is dat de agent heeft gelopen, voor backtracking
        self.direction = ()  # richting van de agent
        self.speed = speed / 100  # snelheid van de agent

        # attributen die over strategie gaan
        self.lost = False  # of de agent verdwaald is en dus een bepaalde strategie gaat gebruiken
        self.age = age  # beïnvloedt strategie
        self.destination_reached = True

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
            if self.random.random() < 0.001:
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
    def __init__(self, unique_id, model, pos, start_pos, end_nodes):
        super().__init__(unique_id, model)
        self.cell_history = []
        self.grid_pos, self.pos = pos
        self.end_nodes_pos = end_nodes  # lijst met end_nodes
        self.start = start_pos  # startpositie
        self.end_node_count = 0  # telt bij welk item in de lijst end_nodes_pos zijn
        self.path_count = 0  # telt bij welke item in de lijst path we zijn
        self.path = find_path(self)  # eerste path dat de Seeker gaat volgen
        self.radius = 3

        self.scanned_patches = []
        self.found = False

    def step(self):
        # Als de end node bereikt is moet alles gereset worden en naar
        # de volgende node in de lijst gekeken worden.

        if self.model.lost:
            if len(self.model.grid.get_cell_list_contents(self.pos)) == 3:
                exit()

            if not self.found:
                if self.pos == self.end_nodes_pos[self.end_node_count]:
                    self.start = self.pos
                    self.end_node_count += 1
                    self.path = find_path(self)
                    self.path_count = 0
            else:
                self.path = find_path(self)
                self.path_count = 0
            new_pos = self.path[self.path_count]
            self.model.grid.move_agent(self, new_pos)
            self.path_count += 1

            self.scanning()

    def scanning(self):
        for cell in self.model.grid.iter_neighborhood(self.pos, True, True, 3):
            if cell not in self.scanned_patches:
                self.scanned_patches.append(cell)

            for agent in self.model.grid.get_cell_list_contents(cell):
                if type(agent) is Patch:
                    agent.seen = True
        # functie gaat elke richting af tot de radius van het zicht
        for direction in direction_list:
            tree_found = False
            pos = self.pos
            for _ in range(self.radius):
                # stapsgewijs wordt in elke richting gekeken of er een boom staat of niet, zo ja dan wordt
                # de loop gebroken en gaat hij door naar de volgende richting
                pos = ((pos[0] + direction[0]), (pos[1] + direction[1]))
                if not self.model.grid.out_of_bounds(pos):
                    patch = [agent for agent in self.model.grid.get_cell_list_contents(pos)
                             if isinstance(agent, Patch)][0]
                    hider = [agent for agent in self.model.grid.get_cell_list_contents(pos)
                             if isinstance(agent, Hider)]
                    # checkt of de persoon gevonden is
                    if len(hider) != 0:
                        self.found = True
                        self.end_nodes_pos = [hider[0].pos]
                        self.end_node_count = 0
                        self.start = self.pos
                        hider[0].found = True
                    if tree_found:
                        if patch not in self.scanned_patches:
                            patch.seen = False
                        if patch in self.scanned_patches:
                            self.scanned_patches.remove(patch)
                    if patch.tree:
                        tree_found = True


class Patch(Agent):
    parent: object

    def __init__(self, pos, model, cost, parent=None):
        super().__init__(pos, model)
        self.pos = pos
        self.seen = False
        self.cost = cost
        self.parent = parent
        self.tree = False

        self.g = 0
        self.h = 0
        self.f = 0

    def step(self):
        pass
