from model import HaS
from agent import Seeker, Patch, Hider
import mesa




def agent_portrayal(agent):
    if type(agent) is Hider:
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 2,
                     "Color": "red",
                     "r": 0.5}
        return portrayal

    if type(agent) is Seeker:
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 2,
                     "Color": "blue",
                     "r": 0.5}
        return portrayal

    if type(agent) is Patch:
        portrayal = {}
        if agent.tree:
            portrayal["Color"] = "#00FF00"
        elif agent.seen:
            portrayal["Color"] = "#D6F5D6"
        else:
            portrayal["Color"] = "#964B00"

        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "True"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1
        return portrayal


width = 30
height = 30
start_node = (5,29)
end_nodes = [(25,6)]

grid = mesa.visualization.CanvasGrid(agent_portrayal, width, height, 500, 500)
server = mesa.visualization.ModularServer(
    HaS, [grid], "Hide and Seek", {"width": width, "height": height})

server.port = 8521  # The default
server.launch()
