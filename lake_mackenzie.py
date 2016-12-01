# The Lake Cognitive Theory
# By Jim Davies (jim@jimdavies.org)

# Started 2006

VERBOSE = 1


class Mind:
    "one individual animal mind"

    def __init__(self, theName):
        self.name = theName
        self.chunks = []
        self.goals = []
        self.actions = []
        self.currentActions = []
        self.mentonPools = []

    def name2object(self, theName):
        '''takes in the name field of a chunk, action, or goal and returns the object.

        theName (string) is the name of the chunk, action, or goal.'''
        # usage: name2object(chunks[0].name)

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

class Clock:
    "keeps track of time"

    ## This is the clock for a given agent's mind, though
    ##   this class does not model anything in the animal mind. It just
    ##   keeps track of time. To make time go forward, just use the
    ##   increment method.

    def __init__(self, endtime=100):
        # the endtime is when the simulation will stop
        self.endtime = endtime
        # the time is what time it is, or, more explicitly,
        #   how many times the top level loop has iterated.
        self.time = 0

    # use this method to make time pass.
    # It will return true if there is still time left,
    #    and false if time has run out.
    def increment(self, howMuch=1):
        self.time = self.time + howMuch
        if VERBOSE:
            print ("time:", self.time)
        if self.time > self.endtime:
            self.time = self.endtime
            return 0
        else:
            return 1

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

def createMentonPool(theName, theMind, mentonCapacity, replenishRate):
    '''Takes in 3 arguments and creates a menton pool.

    theName is a string which identifies the pool.

    theMind is the mind the menton pool is in. 

    mentonCapacity is the maximum and starting number of mentons in the pool
    
    replenishRate is how many mentons it recovers per chip (unit time).
    '''

    # create a menton pool with the input parameters
    temporaryMentonPoolHolder = MentonPool(theMind, theName, mentonCapacity, replenishRate)
    # add the pool object to the global menton pool symbol.
    theMind.mentonPools.append(temporaryMentonPoolHolder)

    # returns the object
    return temporaryMentonPoolHolder

class Goal:
    "the goals of the system"

    # the input arguments are:
    #
    #    def _init_(self, satisfactionConditions, importance, urgency, deadline, beliefValue=1.0, context="current", justification):
    def __init__(self, theMind, theName, theImportance):
        self.mind = theMind
        self.name = theName
        self.importance = theImportance
        self.drawing = ""

    #        self.satisfactionConditions = satisfactionConditions
    #        self.importance = importance
    #        self.urgency = urgency
    #        self.deadline = deadline
    #        self.beliefValue = beliefValue
    #        self.context = context
    #        self.justification = justification

    # the succinct version of the chunk's Covlan representation
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
# TASK: theImportance needs to only accept a number between 0 and 1, there isn't currently a control for this!
def createGoal(theMind, theName, theImportance):
    '''Takes in two arguments and generates a goal. 

    theMind is the mind this goal resides in
    
    theName is just an arbitrary symbol to represent the goal.

    theImportance is a numeric value between 0 and 1.'''

    # create a goal with the input parameters
    temporaryGoalHolder = Goal(theMind, theName, theImportance)
    # add the chunk ID to the global chunks symbol.
    theMind.goals.append(temporaryGoalHolder)

    # this is for debugging. Prints out the created goal.
    # len(goals) returns the number of goals, so the index
    #  of the last goal is len(goals) - 1
    theMind.goals[(len(theMind.goals) - 1)].printGoal()

    # returns the chunk name
    return temporaryGoalHolder

class Action:
    "actions are what are executed to achieve goals."

    def __init__(self, theMind, theName, theGoalList, theCost, theImportance, mentonPoolName):
        self.mind = theMind
        self.name = theName
        self.goalName = theGoalList
        self.cost = theCost
        self.code = ""
        # for now, the importance of the action will be the importance
        #  of its goal.
        self.importance = theImportance
        # FDO print "goal name is...", name2object(theGoalName)
        # this is where we will hold mentons allocated to this action.
        self.mentons = 0
        #this is the name of the menton pool it must draw from
        self.mentonPoolName = mentonPoolName
        # After the action has been allocated some mentons, it keeps track
        #    of how many it would still like with this variable.
        self.mentonsStillWanted = theCost
        # This is the proportion of the surplus mentons in the pool
        #   that will be allocated to the action. This number is
        #   changed by the function determineProportionsOfMentons(aListOfActions, mentonPoolName)
        self.mentonProportion = 0

    # returns true if the action still wants mentons, false otherwise.
    # called by actionsAreStillHungry(theActions)
    # the "P" in hungryP stands for predicate, as it's used in Lisp notation.
    def hungryP(self):
        if self.mentonsStillWanted > 0:
            return 1
        else:
            return 0

    # This method returns the importance of this action.
    # It is the same as the importance of the goal it's serving.
    # Therefore the goal is one of the function's arguments.
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
# QUESTION: theCost vs the importance? is theCost, what we assigned theImportance to when we created the goals?
def createAction(theMind, theName, theGoalList, theCost, theImportance, mentonPoolName="mainMentonPool"):
    '''Takes in three arguments and generates an action.

    theMind is the object that is the reasoner's mind.

    theName is just an arbitrary symbol to represent this action.

    theGoalList is a list of identifiers of the goals this action serves.

    theCost is the number of mentons per unit time this action uses.'''

    # create an action with the input parameters
    temporaryActionHolder = Action(theMind, theName, theGoalList, theCost, theImportance, mentonPoolName)
    print ("in createAction: name is ", temporaryActionHolder.name)
    # add the action ID to the global actions list.
    theMind.actions.append(temporaryActionHolder)

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

def createChunk(theMind, thingx, relation, thingy, beliefValue=1.0, probability=1.0):
    '''Takes in one to three arguments and generates a chunk. 

    theMind is the mind object that has this chunk in it.

    thingx is the first of the 3-tuple.

    relation is the relation between thingx and thingy.

    thingy is the final of the 3-tuple

    beliefValue is optional.

    probability is optional.'''

    # create a chunk with the input parameters
    temporaryChunkHolder = Chunk(theMind, thingx, relation, thingy, beliefValue, probability)
    # add the chunk ID to the global chunks symbol.
    theMind.chunks.append(temporaryChunkHolder)
    print
    # this is for debugging. Prints out the created chunk.
    # len(chunks) returns the number of chunks, so the index
    #  of the last chunk is len(chunks) - 1
    theMind.chunks[(len(theMind.chunks) - 1)].printChunk()

    # returns the chunk identifier
    return temporaryChunkHolder

def generateName(theChunk):
    # This is called to create self.name in the init.
    # if the thingx is a string, that's what we'll print
    if isinstance(theChunk.thingx, str):
        thisThingx = theChunk.thingx
    # but if the thingx is a chunk, we need to use its name
    elif isinstance(theChunk.thingx, Chunk):
        thisThingx = theChunk.thingx.name
    else:
        print ("ERROR: thingx is not string or chunk (generateName)")
    # now do the same for thingy
    if isinstance(theChunk.thingy, str):
        thisThingy = theChunk.thingy
    elif isinstance(theChunk.thingy, Chunk):
        thisThingy = theChunk.thingy.name
    else:
        print ("ERROR: thingy is not string or chunk (generateName)")
    return "[%s_%s_%s]" % (thisThingx, theChunk.relation, thisThingy)

def getAllActiveGoals(theMind):
    '''returns all currently active goals.

    theMind is the mind object that holds the goal list. '''
    # for now it returns everything in the goals list.
    # in the future it may do something different. 
    return theMind.goals


"""   MACKENZIE'S POOL   """

mackenzie_LAKE = Mind("Mackenzie Lake")
mackenzie_Clock= Clock(10) #don't understand what this is...
mackenzie_Pool = createMentonPool("mackenzie_mainPool", mackenzie_LAKE, 100, 100)#createMentonPool(theName, theMind, mentonCapacity, replenishRate)


createGoal(mackenzie_LAKE, "goal_washDishes", .60)
createGoal(mackenzie_LAKE, "goal_washDishes_paused", .20)
createGoal(mackenzie_LAKE, "goal_listenToRadio_casual", .20)
createGoal(mackenzie_LAKE, "goal_listenToRadio_intense", .60)

createAction(mackenzie_LAKE, "action_washDishes", 6, 8, "mainMentonPool")
createAction(mackenzie_LAKE, "action_washDishes_paused", 2, 6, "mainMentonPool")
createAction(mackenzie_LAKE, "action_listenToRadio_casual", 2, 6, "mainMentonPool")
createAction(mackenzie_LAKE, "action_listenToRadio_intense", 6, 8, "mainMentonPool")