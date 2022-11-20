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
        self.end_nodes = [(3,29), (6,29), (6,0), (9,0), (9,29), (12,29), (12,0), (15,0),
                     (15,29), (18,29), (18,0), (21,0), (21,29), (24,29), (24,0), (27,0), (27,29), (29,29), (29,0)]
        self.start = (3,0)

    def step(self):
        self.move()

    def move(self):
        end_nodes_full = self.model.grid.get_cell_list_contents(self.end_nodes)
        end_nodes = [agent for agent in end_nodes_full if type(agent) != "Hider"]
        start_node = self.model.grid.get_cell_list_contents([(3,0)])[0]

        open_list = []
        closed_list = []

        open_list.append(start_node)

        for i, node in enumerate(end_nodes):

            end_node = end_nodes[i]
            start_node.g = start_node.h = start_node.f = 0
            end_node.g = end_node.h = end_node.f = 0

            while len(open_list) > 0:

                current_node = open_list[0]
                current_index = 0
                for i, item in enumerate(open_list):
                    if item.f < current_node.f:
                        current_node = item
                        current_index = i

                open_list.pop(current_index)
                closed_list.append(current_node)

                if current_node == end_node:
                    path = []
                    current = current_node
                    while curret is not None:
                        path.append(current.pos)
                        current = current.parent
                    return path[::-1]

                children = []
                for new_position in self.model.grid.iter_neighborhood(current_node.pos, True, False):
                    new_nodes = self.model.grid.get_cell_list_contents(new_position)
                    new_node = [agent for agent in new_nodes if type(agent) != "Hider"]
                    children.append(new_node)

                for child in children:
                    child_pos = child[0].pos
                    for closed_child in closed_list:
                        if child == closed_child:
                            continue

                    child[0].g = current_node.g + 1
                    child[0].h = ((child_pos[0] - end_node.pos[0] ** 2) +
                                child_pos[1] - end_node.pos[1] ** 2)
                    child[0].f = child[0].g + child[0].h

                    for open_node in open_list:
                        if child == open_node and child.g > open_node.g:
                            continue

                    open_list.append(child)

            start_node = end_node
        print(open_list)

    def update_patch(self):
        for cell in self.model.grid.iter_neighborhood(self.pos, True, True, 3):
            self.cell_history.append(cell)
            for i in self.model.grid.get_cell_list_contents(cell):
                if type(i) is Patch:
                    i.seen = True

    def shortest_path(self):
        pass

class Patch(Agent):
    def __init__(self, pos, model, cost):
        super().__init__(pos, model)
        self.pos = pos
        self.seen = False
        self.cost = cost

        self.g = 0
        self.h = 0
        self.f = 0

    def step(self):
        pass