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
        if agent.seen:
            portrayal["Color"] = "#D6F5D6"
        elif agent.density > 0.25:
            portrayal["Color"] = "#023020"
        elif agent.density < 0.15:
            portrayal["Color"] = "#AFE1AF"
        else:
            portrayal["Color"] = "#097969"

        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "True"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1
        return portrayal


width = 100
height = 100
start_node = (5,29)
end_nodes = [(25,6)]

grid = mesa.visualization.CanvasGrid(agent_portrayal, width, height, 750, 750)
server = mesa.visualization.ModularServer(
    HaS, [grid], "Hide and Seek", {"width": width, "height": height})

server.port = 8521  # The default
server.launch()
