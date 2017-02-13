# The Lake Cognitive Theory
# By Jim Davies (jim@jimdavies.org)
# Started 2006
# Extended and implemented by Mackenzie Ostler (mackenzie.ostler@gmail.com)


class Mind:
    """" one individual animal mind """

    def __init__(self, name):
        self.name = name
        self.chunks = []
        self.goals = []
        self.actions = []
        self.currentActions = []
        self.mentonPools = {}
        self.productions = None
        self.capacities = None
        self.costs = None
        self.priorities = None
        self.rates = None

    def __call__(self):
        """Returns a dict mapping productions to booleans. Booleans
        represent whether their keys can fire at current simulation
        setp."""

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
        self.update_mentons()
        return fire

    def update_mentons(self):
        """ Updates mentons. """

        for i in range(len(self.mentonPools)):
            if self.mentonPools[i].replenishRate < self.mentonPools[i].maxMentons - self.mentonPools[i].mentons:
                self.mentonPools[i].mentons += self.mentonPools[i].replenishRate
            else:
                self.mentonPools[i].mentons = self.mentonPools[i].maxMentons
                # self.mentonPools[i].print_pool()

    def executable(self, production):
        """
        Will return true if it is possible to execute.
        If any one cost is too high then it will return false
        """

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

        costs = self.costs[production]
        i = 0
        for key in costs:
            self.mentonPools[i].mentons -= costs[key]
            # self.mentonPools[i].print_pool()
            i += 1

    def prioritize(self, tosort):
        """
        returns list of productions that are sorted by priority
        """

        tosort.sort(self.compare)
        return tosort

    def compare(self, p, q):
        """  returns a bool p > q  """

        return self.priorities[p] < self.priorities[q]

    def bind(self, productions, (pools, capacities, rates, costs, priorities)):
        """ binds a mind to a production system """

        pool_keys = pools.keys()
        pool_list = []

        for i in range(len(pool_keys)):
            pool = MentonPool(self.name, pool_keys[i], capacities[pool_keys[i]],
                              pools[pool_keys[i]], rates[pool_keys[i]])
            pool_list.append(pool)
        self.productions = productions
        self.mentonPools = pool_list
        self.capacities = capacities
        self.rates = rates
        self.costs = costs
        self.priorities = priorities

        return self

    def create_gaction(self, name):

        # create functionality old: name2object

        # first check to see if it is a name of a chunk.
        for aChunk in self.chunks:
            if name == aChunk.name:
                return aChunk
        # next see if it's the name of an action.
        for action in self.actions:
            if name == action.name:
                return action
        # next see if it's the name of a goal.
        for goal in self.goals:
            if name == goal.name:
                return goal
        # next see if it's the name of a menton pool.
        for pool in self.mentonPools:
            if name == pool.name:
                return pool
                # end def name2object


class MentonPool:
    """a pool of mentons"""

    def __init__(self, the_mind, the_name, menton_capacity, current_mentons, replenish_rate):

        self.mind = the_mind
        self.name = the_name
        self.mentons = current_mentons
        self.maxMentons = menton_capacity
        self.replenishRate = replenish_rate
        self.temporaryListOfActions = []

        # self.print_pool()

    def print_pool(self):
        print("\n\n****  POOL  ****")
        print("mind: " + str(self.mind))
        print("name: " + str(self.name))
        print("mentons: " + str(self.mentons))
        print("maxMentons: " + str(self.maxMentons))
        print("replenishRate: " + str(self.replenishRate))
        for i in range(len(self.temporaryListOfActions)):
            print("temporaryListOfActions " + str(i) + ": " + str(self.temporaryListOfActions[i]))
        print("****************\n\n")

    def replenish(self):

        self.mentons = self.mentons + self.replenishRate
        if self.mentons > self.maxMentons:
            self.mentons = self.maxMentons

    def spend(self, spent_mentons):

        self.mentons = self.mentons - spent_mentons
        if self.mentons > -1:
            return spent_mentons
        else:
            self.mentons = 0
            return spent_mentons + self.mentons


class Goal:
    """"the goals of the system"""

    def __init__(self, the_mind, the_name, the_importance):

        self.mind = the_mind
        self.name = the_name
        self.importance = the_importance
        self.drawing = ""

    def print_goal(self):
        print("(", self.name, self.importance, ")")

    def next_action_name(self, the_actions):
        for action in the_actions:
            if action.goalName == self.name:
                return action.name

    def next_action(self, the_actions):
        for action in the_actions:
            if action.goalName == self.name:
                return action
                # DEBUGGING print "The action is", action.name, "."


class Action:
    """actions are what are executed to achieve goals."""

    def __init__(self, the_mind):
        self.mind = the_mind
        self.mentons = None
        self.mentons_wanted = None

    @staticmethod
    def hungry():
        print("not implemented!")
        print("more mentons wanted --> this is a bonus feature?")

    def get_importance(self, goal_name=None):
        # If there is no goal name input, then just take the default one.
        # If it's input just use it.
        if goal_name is None:
            goal_name = []

        if not goal_name:
            return self.mind.name2object(self.goal_name).importance
        else:
            return self.mind.name2object(goal_name).importance

    # This method allows the top level loop to allocate mentons to the action.
    # It's important that this is done through the method, rather than directly,
    #    because the mentons still wanted variable needs to be updated.
    def get_mentons(self, number_of_mentons):
        # the "spend" method returns the same number you put into it unless there
        #  are not enough mentons, then it returns what it can. It also removes
        #  mentons from the action's pool.

        mentons_to_give = self.mind.name2object(self.mentonPoolName).spend(number_of_mentons)
        self.mentons = self.mentons + mentons_to_give
        self.mentons_wanted = abs(self.mentons_wanted - mentons_to_give)

    # this is what runs when the action is executed.
    # for now it's only printing.
    def execute(self):
        # This is a placeholder for what the action would actually do.

        print("(", self.name, " executing at power", self.mentons, " for ", self.goal_name, ")")
        # exec command
        # spend the mentons
        self.mentons = 0
        # reset the mentons still wanted variable for the next time we try to
        #    save enough mentons for it to execute again.
        self.mentons_wanted = self.cost


class Chunk:
    """"defines the chunk class"""
    """
    the input arguments are:
       theMind         for the mind that contains this chunk
       thingxARG       for the thingx
       relationARG     for the relation
       thingyARG       for the thingy
       beliefValueARG  for the belief value (optional)
       probabilityARG  for the probability value (optional)
    """

    def __init__(self, mind, thingx, relation, thingy, belief_value=1.0, probability=1.0):

        self.mind = mind
        self.thingx = thingx
        self.relation = relation
        self.thingy = thingy
        self.name = generateName(self)
        self.activation = 0.0
        self.beliefValue = belief_value
        self.probability = probability

    # the succinct version of the chunk's Covlan representation
    def print_chunk(self):
        # if the thingx is a string, that's what we'll print

        if isinstance(self.thingx, str):
            this_thingx = self.thingx
        # but if the thingx is a chunk, we need to use its name
        elif isinstance(self.thingx, Chunk):
            this_thingx = self.thingx.name
        else:
            print("ERROR: thingx is not string or chunk")
            return
        # now do the same for thingy
        if isinstance(self.thingy, str):
            this_thingy = self.thingy
        elif isinstance(self.thingy, Chunk):
            this_thingy = self.thingy.name
        else:
            print("ERROR: thingy is not string or chunk")
            return
        # now print out what we've collected.
        print("(", this_thingx, self.relation, this_thingy, ")")

    # the verbose version of its Covlan representation
    def print_chunk_long(self):
        # if the thingx is a string, that's what we'll print

        if isinstance(self.thingx, str):
            this_thingx = self.thingx
        # but if the thingx is a chunk, we need to use its name
        elif isinstance(self.thingx, Chunk):
            this_thingx = self.thingx.name
        else:
            print("ERROR: thingx is not string or chunk")
            return
        # now do the same for thingy
        if isinstance(self.thingy, str):
            this_thingy = self.thingy
        elif isinstance(self.thingy, Chunk):
            this_thingy = self.thingy.name
        else:
            print("ERROR: thingy is not string or chunk")
            return

        print("("
              "(NAME ", self.name, ") "
                                   "(THINGX ", this_thingx, ") "
                                                            "(RELATION ", self.relation, ") "
                                                                                         "(THINGY ", this_thingy, ") "
                                                                                                                  ")")
