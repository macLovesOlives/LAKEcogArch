# The Lake Cognitive Theory
# By Jim Davies (jim@jimdavies.org)
# Started 2006

# Extended by Mackenzie Ostler (mackenzie.ostler@gmail.com)

VERBOSE = 1

"""

Mind > Menton Pool
     > Chunk
     > Gaction > Goal
               > Action

"""

class Mind:
    "one individual animal mind"

    def __init__(self, theName):
        self.name = theName
        self.chunks = []
        self.goals = []
        self.actions = []
        self.currentActions = []
        self.mentonPools = {}
        self.productions = None
        self.capacities  = None
        self.costs       = None
        self.priorities  = None

    def __call__(self):
        """Returns a dict mapping productions to booleans. Booleans
        represent whether their keys can fire at current simulation
        setp."""

        """Stolen directly from ME..."""

        # determine applicable productions

        print("Mind __call__")

        fire = {}
        for p in self.productions:
            fire[p] = p.precondition(p.system)

        # filter out productions that do not meet menton costs
        # make menton pool deductions
        applicable = self.prioritize([p for p in self.productions if fire[p]])
        for p in applicable:
            if self.executable(p):
                self.deduct(p)
            else:
                fire[p] = False

        # refresh menton pools
        self.updateMentons()
        return fire

    def updateMentons(self):
        """ Updates mentons. """

        print("Mind updateMentons")

        for i in range(len(self.mentonPools)):
            if self.mentonPools[i].replenishRate < self.mentonPools[i].maxMentons - self.mentonPools[i].mentons:
                self.mentonPools[i].mentons += self.mentonPools[i].replenishRate
            else:
                self.mentonPools[i].mentons = self.mentonPools[i].maxMentons

    def executable(self, production):
        """
        Will return true if it is possible to execute.
        If any one cost is too high then it will return false
        """

        print("Mind executable")

        costs = self.costs[production]
        i = 0
        for key in costs:
            if self.mentonPools[i].mentons < costs[key]:
                return False
            i += 1
        return True

    def deduct(self, production):
        """
        Deduct will deduct mentons from the menton pools based on
        production costs
        """

        print("Mind deduct")

        costs = self.costs[production]
        i = 0
        for key in costs:
            self.mentonPools[i].mentons -= costs[key]
            i += 1

    def prioritize(self, tosort):
        """
        returns list of productions that are sorted by priority
        """

        print("Mind prioritize")

        tosort.sort(self.compare)
        return tosort

    def compare(self, p, q):
        """  returns a bool p > q  """

        print("Mind compare")

        return self.priorities[p] < self.priorities[q]

    def bind(self, productions,(pools, capacities, rates, costs, priorities)):
        """
        takes: all the things needed to make a mind
        :return mind
        """

        print("Mind bind")

        pool_keys = pools.keys()
        pool_list = []

        for i in range(len(pool_keys)):
            pool = MentonPool(self.name, pool_keys[i], pools[pool_keys[i]], rates[pool_keys[i]])
            pool_list.append(pool)
        self.productions = productions
        self.mentonPools = pool_list
        self.capacities = capacities
        self.rates = rates
        self.costs = costs
        self.priorities = priorities

        return self

    def create_gaction(self, theName):

        print("Mind create_gaction")

        # create functionality old: name2object

        # first check to see if it is a name of a chunk.
        for aChunk in self.chunks:
            if theName == aChunk.name:
                return aChunk
        # next see if it's the name of an action.
        for action in self.actions:
            if theName == action.name:
                return action
        # next see if it's the name of a goal.
        for goal in self.goals:
            if theName == goal.name:
                return goal
        # next see if it's the name of a menton pool.
        for pool in self.mentonPools:
            if theName == pool.name:
                return pool
                # end def name2object

#class Clock:

class MentonPool:
    "a pool of mentons"
    def __init__(self, theMind, theName, mentonCapacity, replenishRate):

        print("MentonPool __init__")

        self.mind = theMind
        self.name = theName
        self.mentons = mentonCapacity
        self.maxMentons = mentonCapacity
        self.replenishRate = replenishRate
        self.temporaryListOfActions = []

    def replenish(self):

        print("MentonPool replenish")

        self.mentons = self.mentons + self.replenishRate
        if self.mentons > self.maxMentons:
            self.mentons = self.maxMentons

    def spend(self, spentMentons):

        print("MentonPool spend")

        self.mentons = self.mentons - spentMentons
        if self.mentons > -1:
            return spentMentons
        else:
            self.mentons = 0
            return spentMentons + self.mentons

class Goal:
    "the goals of the system"

    def __init__(self, theMind, theName, theImportance):

        print("Goal __init__")

        self.mind = theMind
        self.name = theName
        self.importance = theImportance
        self.drawing = ""

    def printGoal(self):

        print("Goal printGoal")

        print ("(", self.name, self.importance, ")")

    def nextActionName(self, theActions):
        # loop through all the actions, return the name of the action
        #   that matches the goal

        print("Goal nextActionName")

        for action in theActions:
            if action.goalName == self.name:
                return action.name
                # DEBUGGING print "The action is", action.name, "."

    def nextAction(self, theActions):
        # loop through all the actions, return the action
        #   that matches the goal

        print("Goal nextAction")

        for action in theActions:
            if action.goalName == self.name:
                return action
                # DEBUGGING print "The action is", action.name, "."

#def createGoal(theMind, theName, theImportance):

class Action:
    "actions are what are executed to achieve goals."

    def __init__(self, theMind, theName, theGoalList, theCost, theImportance, mentonPoolName):

        print("Action __init__")

        self.mind = theMind

    def hungryP(self):

        print("Action hungryP")

        print("not implemented!")
        print("more mentons wanted --> this is a bonus feature?")

    def getImportance(self, theGoalName=[]):
        # If there is no goal name input, then just take the default one.
        # If it's input just use it.

        print("Action getImportance")

        if theGoalName == []:
            return self.mind.name2object(self.goalName).importance
        else:
            return self.mind.name2object(theGoalName).importance

    # This method allows the top level loop to allocate mentons to the action.
    # It's important that this is done through the method, rather than directly,
    #    because the mentons still wanted variable needs to be updated.
    def getMentons(self, numberOfMentons):
        #the "spend" method returns the same number you put into it unless there
        #  are not enough mentons, then it returns what it can. It also removes
        #  mentons from the action's pool.

        print("Action getMentons")

        mentonsToGive = self.mind.name2object(self.mentonPoolName).spend(numberOfMentons)
        self.mentons = self.mentons + mentonsToGive
        self.mentonsStillWanted = abs(self.mentonsStillWanted - mentonsToGive)

    # this is what runs when the action is executed.
    # for now it's only printing.
    def execute(self, command='print "no command specified"'):
        # This is a placeholder for what the action would actually do.

        print("Action execute")

        print ("(", self.name, " executing at power", self.mentons, " for ", self.goalName, ")")
        # exec command
        # spend the mentons
        self.mentons = 0
        # reset the mentons still wanted variable for the next time we try to
        #    save enough mentons for it to execute again.
        self.mentonsStillWanted = self.cost

#def createAction(theMind, theName, theGoalList, theCost, theImportance, mentonPoolName="mainMentonPool"):

class Chunk:
    "defines the chunk class"

    # the input arguments are:
    #    theMind         for the mind that contains this chunk
    #    thingxARG       for the thingx
    #    relationARG     for the relation
    #    thingyARG       for the thingy
    #    beliefValueARG  for the belief value (optional)
    #    probabilityARG  for the probability value (optional)
    def __init__(self, theMind, thingxARG, relationARG, thingyARG, beliefValueARG=1.0, probabilityARG=1.0):

        print("Chunk __init__")

        self.thingx = thingxARG
        self.relation = relationARG
        self.thingy = thingyARG
        self.name = generateName(self)
        self.activation = 0.0
        self.beliefValue = beliefValueARG
        self.probability = probabilityARG

    # the succinct version of the chunk's Covlan representation
    def printChunk(self):
        # if the thingx is a string, that's what we'll print

        print("Chunk printChunk")

        if isinstance(self.thingx, str):
            thisThingx = self.thingx
        # but if the thingx is a chunk, we need to use its name
        elif isinstance(self.thingx, Chunk):
            thisThingx = self.thingx.name
        else:
            print ("ERROR: thingx is not string or chunk")
        # now do the same for thingy
        if isinstance(self.thingy, str):
            thisThingy = self.thingy
        elif isinstance(self.thingy, Chunk):
            thisThingy = self.thingy.name
        else:
            print ("ERROR: thingy is not string or chunk")
        # now print out what we've collected.
        print ("(", thisThingx, self.relation, thisThingy, ")")

    # the verbose version of its Covlan representation
    def printChunkVerbose(self):
        # if the thingx is a string, that's what we'll print

        print("Chunk printChunkVerbose")

        if isinstance(self.thingx, str):
            thisThingx = self.thingx
        # but if the thingx is a chunk, we need to use its name
        elif isinstance(self.thingx, Chunk):
            thisThingx = self.thingx.name
        else:
            print ("ERROR: thingx is not string or chunk")
        # now do the same for thingy
        if isinstance(self.thingy, str):
            thisThingy = self.thingy
        elif isinstance(self.thingy, Chunk):
            thisThingy = self.thingy.name
        else:
            print ("ERROR: thingy is not string or chunk")

        print ("(" \
               "(NAME ", self.name, ") " \
                                    "(THINGX ", thisThingx, ") " \
                                                            "(RELATION ", self.relation, ") " \
                                                                                         "(THINGY ", thisThingy, ") " \
                                                                                                                 ")")

#def createChunk(theMind, thingx, relation, thingy, beliefValue=1.0, probability=1.0):
