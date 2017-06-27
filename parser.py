# Written by Mackenzie Ostler (mackenzie.ostler@gmail.com) 2017
# Does NOT currently work.  If needed contact me for more info.

import json
from ProductionSystem import *
import lake
import sys


class Parser:
    def __init__(self):
        self.mind = "test_mind"
        self.pools = []
        self.gactions = []
        self.gaction_list = []
        self.knowledge = Knowledge({Node("No initial system knowledge")})
        self.mentonCapacity = None
        self.replenishRate = None
        self.steps = 0
        self.parameters = {}

    def get_file(self, json_file):
        with open(json_file) as data_file:
            data = json.load(data_file)
        return data

    def extract_values(self, data_file):
        mind = data_file["mind"]
        gactions = mind["gactions"]
        pools = mind["pools"]
        self.mind = mind["name"]
        self.steps = mind["number of steps"]

        for i in pools:
            self.pools.append(i)

        for i in gactions:
            self.gactions.append(i)

            name = i["name"]
            precondition = []
            for node in i["precondition"]:
                print(node)
                if precondition != "":
                    con = str(node["node"])
                    precondition.append(con)
                else:
                    con = str(node["node"])
                    precondition.append(con)
            start = []
            for node in i["action"][0]["start"]:
                if start != "":
                    con = str(node["node"])
                    start.append(con)
                else:
                    con = str(node["node"])
                    start.append(con)
            stop = []
            if len(i["action"][1]["stop"]) == 0:
                # print(Node(x) for x in precondition)
                print('%s = Production(Precondition({Node("%s")}),Action({Node("%s")}))' %(name, precondition[0], start[0]))
                exec('%s = Production(Precondition({Node("%s")}),Action({Node("%s")}))' %(name, precondition[0], start[0]))
                self.gaction_list.append(Production(Precondition({Node(precondition[0])}), Action({Node(start[0])})))
            else:
                for node in i["action"][1]["stop"]:
                    if stop != "":
                        con = str(node["node"])
                        stop.append(con)
                    else:
                        con = str(node["node"])
                        stop.append(con)
                print("%s = Production(Precondition({Node('%s')}),Action({Node('%s')},{Node('%s')}))" %(name, precondition[0], stop[0], start[0]))
                exec("%s = Production(Precondition({Node('%s')}),Action({Node('%s')},{Node('%s')}))" %(name, precondition[0], stop[0], start[0]))
                self.gaction_list.append(Production(Precondition({Node(precondition[0])}), Action({Node(stop[0])}, {Node(start[0])})))

    def create_mind(self):
        lake.Mind(self.mind)

    def create_pools(self):
        self.parameters["pools"] = {}
        self.parameters["capacity"] = {}
        self.parameters["rates"] = {}

        for i in self.pools:
            name = str(i["name"])
            cap = i["capacity"]
            rate = i["rates"]
            initial = i["initial"]

            self.parameters["pools"][name] = initial
            self.parameters["capacity"][name] = cap
            self.parameters["rates"][name] = rate

    def create_params(self):
        self.parameters["costs"] = {}
        self.parameters["priorities"] = {}

        for i in self.gactions:
            name = str(i["name"])
            priorities = i["priority"]
            costs = {}
            for j in i["costs"]:
                k = (str(j.keys()[0]))
                v = j[k]
                costs.update({k: v})

            self.parameters["costs"][name] = costs
            self.parameters["priorities"][name] = priorities


def main():
    p = Parser()
    file = str(sys.argv[1])
    f = p.get_file(file)
    p.extract_values(f)
    p.create_mind()
    p.create_pools()
    p.create_params()

    # for key in p.parameters:
    #     print(str(key) + ": " + str(p.parameters[key]))

    engine = lake.Mind(str(p.mind))
    par = p.parameters
    system = ProductionSystem(p.knowledge, p.gaction_list, engine.bind, (par["pools"], par["capacity"], par["rates"], par["costs"], par["priorities"]))
    # for i in range(len(engine.mentonPools)):
    #     print(str(engine.mentonPools[i].name) + ": " + str(engine.mentonPools[i].mentons))

    system.knowledge.add({Arrow((Node("Is"), Node("Paper"), Node("Blank")))})
    for i in range(5):
        system.step()
        print "\nState of the Mentons in step " + str(i + 2) + ": "
        for j in range(len(engine.mentonPools)):
            print(str(engine.mentonPools[j].name) + ": " + str(engine.mentonPools[j].mentons))

    print '\n' + system.log

if __name__ == "__main__":
    main()
