'''CGSC 4001/5001 Can Makik, Josh Noronha, and Zahrah Hajali'''


# This file provides the menton engine implementing menton dynamics as
# set out in the course requirements. MentonEngine is a decision
# procedure, see documentation.

class MentonEngine:
    def __init__(self):

        self.productions = None
        self.pools = None
        self.capacities = None
        self.rates = None
        self.costs = None
        self.priorities = None

    def __call__(self):
        """Returns a dict mapping productions to booleans. Booleans
        represent whether their keys can fire at current simulation
        setp."""

        # determine appilcable productions
        fire = {}
        for p in self.productions:
            fire[p] = p.precondition(p.system)

        # filter out productions that do not meet menton costs
        # make menton pool deductions
        applicable = self.prioritize([p for p in self.productions if fire[p]])
        for p in applicable:
            if self.payable(p):
                self.deduct(p)
            else:
                fire[p] = False

        # refresh menton pools
        self.refresh()
        return fire

    def bind(self, productions, (pools, capacities, rates, costs, priorities)):
        """Bind self to system productions with desired paramters.
        Menton pools is a dictionary that takes strings and floats.
        Where the strings are the names of the pools and the floats are the
        intial values. Menton Cost is also a dictionary that takes productions
        and maps them onto costs. The costs are dictionaries that take pools
        that map onto costs. (For every production theres a cost and for every
        cost you will know what pool it draws from and how much it costs.
        Refresh rate is a dictionary that takes pool names and maps them onto
        menton refresh rates."""

        self.productions = productions  # actions
        self.pools = pools  # pools is a dictionary that takes strings and floats.Where the strings are the names of the pools and the floats are the intial values
        self.capacities = capacities  # ??? presumably how many productions can be handled?
        self.rates = rates  # refresh rate
        self.costs = costs  # maps the menton cost of the productions
        self.priorities = priorities  # ??? presumably how important each task is

        return self

    def deduct(self, production):
        """ Deduct will deduct mentons from the menton pools based on
            production costs"""

        costs = self.costs[production]
        for pool in costs:
            self.pools[pool] -= costs[pool]

    def refresh(self):
        """Refresh mentons."""

        for pool in self.pools:
            if self.rates[pool] < self.capacities[pool] - self.pools[pool]:
                self.pools[pool] += self.rates[pool]
            else:
                self.pools[pool] = self.capacities[pool]

    def payable(self, production):
        """Will return true if it is payable. If any one cost is too high
            and can not be afforded, then it will return false"""

        costs = self.costs[production]
        for pool in costs:
            if self.pools[pool] < costs[pool]:
                return False
        return True

    def prioritize(self, satisfied):
        """priotize is going to return a list of prouductions that are
        applicable and are ordered by priority"""

        satisfied.sort(self.compare)
        return satisfied

    def compare(self, p, q):
        """compare is going to return a boolean for if p has higher priority
        then q"""

        return self.priorities[p] < self.priorities[q]
