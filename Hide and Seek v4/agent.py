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
        if not self.found:
            neighborhood = self.model.grid.get_neighborhood(self.pos, True, True)
            new_pos = (self.random.choice(neighborhood))
            self.model.grid.move_agent(self, new_pos)


"""
Seeker agent kijkt of Hider in gezichtsveld is. Zo ja, beweegt ernaartoe, zo nee, beweegt willekeurig.
"""


class Seeker(Agent):
    def __init__(self, unique_id, model, pos, start_pos, end_nodes):
        super().__init__(unique_id, model)
        self.cell_history = []
        self.pos = pos
        self.id = unique_id
        self.end_nodes_pos = end_nodes  # lijst met end_nodes
        self.start = start_pos  # startpositie
        self.end_node_count = 0  # telt bij welk item in de lijst end_nodes_pos zijn
        self.path_count = 0  # telt bij welke item in de lijst path we zijn
        self.path = self.find_path()  # eerste path dat de Seeker gaat volgen

        self.scanned_patches = []
        self.found = False

    def step(self):
        # Als de end node bereikt is moet alles gereset worden en naar
        # de volgende node in de lijst gekeken worden.
        if len(self.model.grid.get_cell_list_contents(self.pos)) == 3:
            exit()

        if not self.found:
            if self.pos == self.end_nodes_pos[self.end_node_count]:
                self.start = self.pos
                self.end_node_count += 1
                self.path = self.find_path()
                self.path_count = 0
        else:
            self.path = self.find_path()
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
                if type(agent) is Hider:
                    self.found = True
                    self.end_nodes_pos = [agent.pos]
                    self.end_node_count = 0
                    self.start = self.pos
                    agent.found = True

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

    def shortest_path(self):
        pass


class Patch(Agent):
    parent: object

    def __init__(self, pos, model, cost, parent=None):
        super().__init__(pos, model)
        self.pos = pos
        self.seen = False
        self.cost = cost
        self.parent = parent

        self.g = 0
        self.h = 0
        self.f = 0

    def step(self):
        pass
