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
        """ These should all be grouped in one pool? """
        self.goals = []
        self.actions = []
        self.currentActions = []
        """"""
        self.mentonPools = {}
        self.productions = None
        self.capacities = None
        # self.rates = mentonPool.replenishRate
        self.costs = None
        self.priorities = None

    def __call__(self):
        """Returns a dict mapping productions to booleans. Booleans
        represent whether their keys can fire at current simulation
        setp."""

        """Stolen directly from ME..."""

        # determine applicable productions
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
        """ Updates mentons."""

        for pool in self.mentonPools:
            if self.rates[pool] < self.capacities[pool] - self.mentonPools[pool]:
                self.mentonPools[pool] += self.rates[pool]
            else:
                self.mentonPools[pool] = self.capacities[pool]

    def executable(self, production):
        """
        Will return true if it is possible to execute.
        If any one cost is too high then it will return false
        """

        costs = self.costs[production]
        for pool in costs:
            if self.mentonPools[pool] < costs[pool]:
                return False
        return True

    def deduct(self, production):
        """
        Deduct will deduct mentons from the menton pools based on
        production costs
        """

        costs = self.costs[production]
        for pool in costs:
            self.mentonPools[pool] -= costs[pool]

    def prioritize(self, tosort):
        """
        returns list of productions that are sorted by priority
        """
        tosort.sort(self.compare)
        return tosort

    def compare(self, p, q):
        """  returns a bool p > q  """
        return self.priorities[p] < self.priorities[q]

    def bind(self, productions,(pools, capacities, rates, costs, priorities)):
        """
        takes: all the things needed to make a mind
        :return mind
        """

        self.productions = productions  # actions
        self.mentonPools = pools        # {} that takes str (names of the pools) and floats (initial values)
        self.capacities = capacities    # ??? presumably how many productions can be handled?
        self.rates = rates              # refresh rate
        self.costs = costs              # maps the menton cost of the productions
        self.priorities = priorities    # ??? presumably how important each task is

        return self

    def create_gaction(self, theName):
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
        # this menton pool is a part of an individual mind
        self.mind = theMind
        # The pool of mentons has a name to identify itself in the list
        #    of mentonPools.
        self.name = theName
        # The pool has a maximum capacity.
        self.mentons = mentonCapacity
        # When the pool is created, it starts at maximum capacity.
        self.maxMentons = mentonCapacity
        # The replenish rate is how fast it recovers from spent mentons.
        self.replenishRate = replenishRate
        # The temporary list of actions gets used in the top level loop.
        #    it holds those actions drawing on this pool that help the
        #    current goals.
        self.temporaryListOfActions = []

    # adds replenishRate mentons to number of mentons in pool,
    #    but not so that it overflows with mentons over maxMentons
    def replenish(self):
        self.mentons = self.mentons + self.replenishRate
        if self.mentons > self.maxMentons:
            self.mentons = self.maxMentons

    # Run this method to request mentons in the pool.
    # It returns the number of mentons that it can spare.
    # If there are plenty of mentons, the return value is
    #   the same as the input value.
    # If there are not enough resources, then it returns all
    #   it has left, and the current menton count goes to zero.
    def spend(self, spentMentons):
        self.mentons = self.mentons - spentMentons
        if self.mentons > -1:
            return spentMentons
        else:
            return spentMentons + self.mentons
            self.mentons = 0

#def createMentonPool(theName, theMind, mentonCapacity, replenishRate):


class Goal:
    "the goals of the system"

    def __init__(self, theMind, theName, theImportance):
        self.mind = theMind
        self.name = theName
        self.importance = theImportance
        self.drawing = ""

    def printGoal(self):
        print ("(", self.name, self.importance, ")")

    def nextActionName(self, theActions):
        # loop through all the actions, return the name of the action
        #   that matches the goal
        for action in theActions:
            if action.goalName == self.name:
                return action.name
                # DEBUGGING print "The action is", action.name, "."

    def nextAction(self, theActions):
        # loop through all the actions, return the action
        #   that matches the goal
        for action in theActions:
            if action.goalName == self.name:
                return action
                # DEBUGGING print "The action is", action.name, "."

#def createGoal(theMind, theName, theImportance):

class Action:
    "actions are what are executed to achieve goals."

    def __init__(self, theMind, theName, theGoalList, theCost, theImportance, mentonPoolName):
        self.mind = theMind

    def hungryP(self):
        print("not implemented!")
        print("more mentons wanted --> this is a bonus feature?")

    def getImportance(self, theGoalName=[]):
        # If there is no goal name input, then just take the default one.
        # If it's input just use it.
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
        mentonsToGive = self.mind.name2object(self.mentonPoolName).spend(numberOfMentons)
        self.mentons = self.mentons + mentonsToGive
        self.mentonsStillWanted = abs(self.mentonsStillWanted - mentonsToGive)

    # this is what runs when the action is executed.
    # for now it's only printing.
    def execute(self, command='print "no command specified"'):
        # This is a placeholder for what the action would actually do.
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
