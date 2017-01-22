import json
from ProductionSystem import *
import lake

"""
intended to parse a json to easily add and create models in lake...
Not updated... nor accurate anymore.
Keeping in case it is needed in future (quickly modifiable)
"""

class Parser:
    def __init__(self):
        mind = None
        pool = None
        mentonCapacity  = None
        replenishRate   = None

    def getFile(self, jsonFile):
        with open(jsonFile) as data_file:
            data = json.load(data_file)
        return data

    def extractValues(self, data_file, gaction):
        self.mind = data_file["mind"]["name"]
        self.pool = data_file["mind"]["pool"]["pool_name"]
        self.mentonCapacity = data_file["mind"]["pool"]["mentonCapacity"]
        self.replenishRate = data_file["mind"]["pool"]["replenishRate"]
        # gactions
        counter = 0
        while counter < len(data_file["mind"]["gaction"]):
            goal = data_file["mind"]["gaction"][counter]["goal"]["name"]
            goal_importance = data_file["mind"]["gaction"][counter]["goal"]["importance"]

            action = data_file["mind"]["gaction"][counter]["action"]["name"]
            action_cost = data_file["mind"]["gaction"][counter]["action"]["cost"]
            action_importance = data_file["mind"]["gaction"][counter]["action"]["importance"]

            relation = data_file["mind"]["gaction"][counter]["relationship"]
            diction = {"goal": goal, "goal_importance": goal_importance, "action": action, "action_cost": action_cost,
                       "action_importance": action_importance, "relation": relation}
            gaction.append(diction)

            counter += 1

    def creatGactions(self, gactionlist):
        lake = lake

        # create mind
        mind = lake.Mind(self.mind)
        pool = lake.createMentonPool(self.pool, mind, self.mentonCapacity, self.replenishRate)
        chunkList = []
        for gaction in range(len(gactionlist)):
            # create goal
            lake_goal = lake.createGoal(mind, gactionlist[gaction]['goal'], gactionlist[gaction]['goal_importance'])
            # create action
            lake_action = lake.createAction(mind, gactionlist[gaction]['action'], gactionlist[gaction]['goal'],
                                            gactionlist[gaction]['action_cost'],
                                            gactionlist[gaction]['action_importance'])
            # create chunk
            lake_chunk = lake.createChunk(mind, lake_action, gactionlist[gaction]['relation'], lake_goal)
            chunkList.append(lake_chunk)

            return chunkList

    def useProductionSystem(self, chunkList):
        productions = {}
        for i in range(len(chunkList)):
            prod = Production(Precondition(set(),
                                           Arrow((
                                               Node(chunkList[i].relation), Node(chunkList[i].thingx.name),
                                               Node(chunkList[i].thingy.name)
                                           )),
                                           Action(({Node(chunkList[i].thingx.name)}))))

            print("dictionary index")
            print(chunkList[i].thingy.name)
            productions[chunkList[i].thingy.name] = prod


if __name__ == "__main__":
    parser = Parser()
    f = parser.getFile("testFile.json")  # this name should be passed in from cmd

    gaction = []

    parser.extractValues(f, gaction)
    chunkList = parser.creatGactions(gaction)
    productions = parser.useProductionSystem(chunkList)
    engine = lake.Mind()

    priorities = {}

    system = ProductionSystem(knowledge, productions, engine.bind, )
