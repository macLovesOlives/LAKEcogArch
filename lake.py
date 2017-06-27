# The Lake Cognitive Theory
# By Jim Davies (jim@jimdavies.org)
# Started 2006
# Extended and implemented by Mackenzie Ostler (mackenzie.ostler@gmail.com)
# Python 2.7


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
        """
        Returns a dict mapping productions to booleans. Booleans
        represent whether their keys can fire at current simulation
        step.
        """

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
                self.mentonPools[i].print_pool()

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
            self.mentonPools[i].print_pool()
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


class MentonPool:
    """a pool of mentons"""

    def __init__(self, the_mind, the_name, menton_capacity, current_mentons, replenish_rate):

        self.mind = the_mind
        self.name = the_name
        self.mentons = current_mentons
        self.maxMentons = menton_capacity
        self.replenishRate = replenish_rate
        self.temporaryListOfActions = []

        self.print_pool()

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

