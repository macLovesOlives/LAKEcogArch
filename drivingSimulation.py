'''CGSC 4001/5001 Can Mekik, Josh Noronha, and Zahrah Hajali'''

#This is our model of Strayer and Johnston (2001). See our
# scientific writeup

from ProductionSystem import *
import random as r
from copy import deepcopy

#This is MentonEngine modified for the modeling requirements

class MentonEngine2:

    def __init__(self):

        self.productions = None
        self.pools = None
        self.rates = None
        self.costs = None
        self.priorities = None
        self.step_durations = None
        self.steps = 0

    def __call__(self):

        #refresh menton pools
        self.refresh()
        
        #determine appilcable productions
        fire = {}
        for p in self.productions:
            fire[p] = p.precondition(p.system)

        #filter out productions that do not meet menton costs
        #make menton pool deductions
        applicable = self.prioritize([p for p in self.productions if fire[p]])
        for p in applicable:
            if self.payable(p):
                self.deduct(p)
            else:
                fire[p] = False

        self.steps += 1

        return fire        
    
    def bind (self, productions, (pools, rates, costs, durations,
                                  priorities)):
        """Bind self to system productions with desired paramters.
        Menton pools is a dictionary that takes strings and floats.
        Where the strings are the names of the pools and the floats are the
        intial values. Menton Cost is also a dictionary that takes productions
        and maps them onto costs. The costs are dictionaries that take pools
        that map onto costs. (For every production theres a cost and for every
        cost you will know what pool it draws from and how much it costs.
        Refresh rate is a dictionary that takes pool names and maps them onto
        menton refresh rates."""

        self.productions = productions
        self.pools = pools
        self.rates = rates
        self.costs = costs
        self.priorities = priorities
        self.step_durations = durations

        return self
        
    def deduct (self, production):
        """Deduct will deduct mentons from the menton pools based on
            production costs"""
        
        costs = self.costs[production]
        for pool in costs:
            self.pools[pool] -= costs[pool]

    def refresh(self):
        """Refresh mentons."""

        for pool in self.pools:
            self.pools[pool] += self.rates['global'] *\
                          self.rates[pool] *\
                          self.step_durations[self.steps]

    def payable (self, production):
        """Will return true if it is payable. If any one cost is too high
            and can not be afforded, then it will return false"""
        
        costs = self.costs[production]
        for pool in costs:
            #print "self.pools " + str(self.pools[pool])
            #print "production cost " + str(costs[pool])
            if self.pools[pool] < costs[pool]:
                #print False
                return False
        return True

    def prioritize (self, satisfied):
        """priotize is going to return a list of prouductions that are
        applicable and are ordered by priority"""

        return r.sample(satisfied, len(satisfied))

    def reset(self):

        #participant mentons get allocated randomly per trial:
        # this is meant to model menton allocation IRL, but
        # assuming not much more than that it happens...
        raw_rates = []
        for p in self.rates:
            if not p == 'global':
                raw_rates.append(r.random())
        rates = [rate/float(sum(raw_rates)) for rate in raw_rates]
        for p in self.rates:
            if not p == 'global':
                self.rates[p] = rates.pop()

        #this resets menton pools for the next trials...
        # see justification in writeup.
        for pool in self.pools:
            self.pools[pool] = 0

        self.steps = 1
        

def initialize_participant(pools, factor=1):
    """Initialize participantReturns a random value r_p ~ Uniform(0.5, 1). This value represents
    a participant's menton renewal rate."""
    
    participant = {'global':factor*0.5*(1 + r.random())}
    for pool in pools:
        participant[pool] = 0

    return participant


def run_participant(task,
                    condition,
                    trials,
                    pools,
                    participant_rates,
                    task_costs,
                    task_durations):
    """Put participant through a trial."""

    #initialize 'experiment'
    engine = MentonEngine2()

    parameters = (pools,
                  participant_rates,
                  task_costs,
                  task_durations,
                  {pdctn : 1 for pdctn in condition})

    system = ProductionSystem(Knowledge(set()),
                              condition,
                              engine.bind,
                              parameters)

    return task(system, trials)


def Strayer_Johnston(system, trials):
    """Model of Strayer and Johnston (2001) experiment 1."""

    tally = 0
    for i in range(trials):
        #reset system knowledge
        system.knowledge.semanticCategories[True] = set()
        #clear mentons from previous trial, and
        # get new refresh rates
        system.interpreter.decisionProcedure.reset()
        #simulate the two stages of the trial
        system.step()
        system.knowledge.add({stimulus})
        system.step()
        if target in system.knowledge.semanticCategories[True]:
            tally += 1
    return tally


def go_Nogo(system, trials):
    """Model of the go trials of a go_Nogo task."""

    tally = 0
    for i in range(trials):

        #reset system knowledge
        system.knowledge.semanticCategories[True] = {stimulus}
        #clear mentons from previous trial, and
        # get new refresh rates
        system.interpreter.decisionProcedure.reset()
        system.step()
        if target in system.knowledge.semanticCategories[True]:
            tally += 1
    return tally


def run_condition(task,
                  condition,
                  trials,
                  pools,
                  participants,
                  task_costs,
                  task_durations):
    """Run one condition of an experiment. Returns count of successful trials.
    """

    tally = 0
    
    for p in participants:
        tally += run_participant(task,
                                 condition,
                                 trials,
                                 deepcopy(pools),
                                 p,
                                 task_costs,
                                 task_durations)

    return tally


def run_experiment(task,
                   conditions,
                   trials,
                   pools,
                   participants,
                   task_costs,
                   task_durations):
    """Run an experiment. Returns counts of successful trials for each
    condition.
    """

    tallies = {}
    for condition in conditions:
        tallies[condition] = 0
        
    for condition in conditions:
        tallies[condition] += run_condition(task,
                                            conditions[condition],
                                            trials,
                                            deepcopy(pools),
                                            participants,
                                            task_costs,
                                            task_durations)
    return tallies


def get_results(experiment, n_participants, trials):
    """Returns error rates on each condition given experiment, counts of
    successful trials for each condition, n_participants and trials, the
    number of participants and trials (per condition) respectively."""

    results = {}
    for condition in experiment:
        results[condition] = 1-experiment[condition]/\
                             float(n_participants*trials)
    return results


def calibration_error(task,
                      n_samples,
                      conditions,
                      calib_trials,
                      menton_pools,
                      participants,
                      stop_cost,
                      stop_time):
    samples = []
    for i in range(n_samples):
        samples.append(get_results(run_experiment(task,
                                                  conditions,
                                                  calib_trials,
                                                  menton_pools,
                                                  participants,
                                                  stop_cost,
                                                  stop_time),
                                   len(participants),
                                   calib_trials))
    r = {}
    for c in conditions:
        m = sum([sample[c] for sample in samples])/float(n_samples)
        sd = sum([(sample[c]-m)**2 for sample in samples])/\
                float(n_samples-1)
        r[c] = {'m' : m, 'sd' : sd}
    return r

#target and stimulus
stimulus = Arrow(('is', 'light', 'red'))
target = Node('participant stopped')


#task productions
drive = Production(
    Precondition(
        set(),
        {stimulus}),
    Action({Node('participant driving')},
           set()))


cellphone = Production(
    Precondition(
        set(),
        {stimulus}),
    Action({Node('participant in conversation'),
            Node('participant performing secondary task')},
           set()))


radio = Production(
    Precondition(
        set(),
        {stimulus}),
    Action({Node('participant listening to radio'),
            Node('participant performing secondary task')},
           set()))

#As decided by considerations, there are two menton pools.
# See paper.
menton_pools = {1 : 0, 2 : 0}

#We chose to have 40 participants. Arbitrarily.
n_participants = 40

#need to calibrate model for stop cost
# stop essentially is a go/no-go task, on a sample from cognitivefun.net 
# error rates for visual go/no-go is about %12 for mean RT about 0.4 sec
# we will use this for calibration

stop_c = Production(
    Precondition({stimulus},
                 set()),
    Action({target},
           set()))
n_samples = 10
calib_trials = 20
stop_time = {1 : 0.4}
stop_target = {stop_c : 0.12}
stop_cost = {stop_c : {1 : 0.5, 2 : 0.5}}
factor = 15.85
participants = [initialize_participant(menton_pools, factor)
                for i in range(n_participants)]

print calibration_error(go_Nogo,
                        n_samples,
                        {'calibration' : {stop_c}},
                        calib_trials,
                        menton_pools,
                        participants,
                        stop_cost,
                        stop_time)

#For factor = 15.85, calibration_error gave
# (0.1203125, 0.00019300881410256362).
# good enough.
# We know that the base capacity of participants is ~U(0,1)
# (that's how the model is set up). On average, that means we get a global
# refresh rate of 0.5*factor=7.925. Using equations in our paper,
# you will find that over one second, people have 7.925 mentons available
# (we assume refresh rates are in mentons/second)

#Next, we need to find menton consumption for the control task. Average error
# on this task is 0.028*2/3+0.036/3 = 0.031-ish for average trial time approx
# 7.5 sec + time to stop. want to get close to that. Do it as above.
# split task evenly between groups, arbitrarily. future work should
# address this.

#When participants fail to drive, the task is a failure.
stop = Production(
    Precondition({stimulus, Node('participant driving')},
                 set()),
    Action({target},
           set()))
step_times = {1 : 7.5, 2 : 1}
drive_cost = 4.75
control_costs = {stop : {1 : 0.5, 2 : 0.5},
                 drive : {1 : drive_cost/float(2),
                          2 : drive_cost/float(2)}}

print calibration_error(Strayer_Johnston,
                        n_samples,
                        {'control' : {stop, drive}},
                        calib_trials,
                        menton_pools,
                        participants,
                        control_costs,
                        step_times)

#4.75 seems to work.

#Next, we adjust blocked experimental conditions' error rates using our
# values we got for the control task. error rates for each condition in expt
# are 0.07 (cellphone) and 0.043 (radio) respectively, there were twice as
# many participants in cellphone as radio so the average for the block is
# 0.061. Time constraints don't change.

#Why are we blocking? Our eternal problem is: we know the cost
# how do we split it up into the pools. The idea is that the
# difference in cost for a task across pools should be meaningful
# blocking helps us get that meaningfulness... (see below)


#When participants fail any of the tasks, it's a failure.
stop_b = Production(
    Precondition({stimulus,
                  Node('participant driving'),
                  Node('participant performing secondary task')},
                 set()),
    Action({target},
           set()))
block = Production(
    Precondition(
        set(),
        {stimulus}),
    Action({Node('participant performing secondary task')},
           set()))
blocked_cost = 4.5
#the pools for block are weighted 3 : 2 because presumably
# the tasks share a pool in common (for listening/comprehension)
# but cellphone use also uses another ability, and the numbers of.
# people in cellphone trials is twice those in radio.
# it's a rough estimate.
blocked_costs = {stop_b : {1 : 0.5, 2 : 0.5},
                 drive : {1 : drive_cost/float(2),
                          2 : drive_cost/float(2)},
                 block : {1 : blocked_cost*3/float(5),
                          2 : blocked_cost*2/float(5)}}

print calibration_error(Strayer_Johnston,
                        n_samples,
                        {'blocked' : {stop_b,
                                      drive,
                                      block}},
                        calib_trials,
                        menton_pools,
                        participants,
                        blocked_costs,
                        step_times)

#overall cost is 3.6

#Now we are looking for a p which will divide the menton quantity
# blocked_cost in to the constituent tasks.
# it should be that (2/3)*p*blocked_costs +
# (1/3)*(1-p)*blocked_costs = blocked_costs. It's trivial!
# BUT, it should also be that p makes each group have its
# correct error value.

p = 0.3
radio_costs = {stop_b : {1 : 0.5, 2 : 0.5},
               drive : {1 : drive_cost/float(2),
                        2 : drive_cost/float(2)},
               radio : {1 : p*blocked_cost,
                        2 : 0}}
cellphone_costs = {stop_b : {1 : 0.5, 2 : 0.5},
                   drive : {1 : drive_cost/float(2),
                            2 : drive_cost/float(2)},
                   cellphone : {1 : (1-p)*blocked_cost,
                            2 : (1-p)*blocked_cost}}

print calibration_error(Strayer_Johnston,
                        n_samples,
                        {'radio' : {stop_b,
                                      drive,
                                      radio}},
                        calib_trials,
                        menton_pools,
                        participants,
                        radio_costs,
                        step_times)

print calibration_error(Strayer_Johnston,
                        n_samples,
                        {'cellphone' : {stop_b,
                                      drive,
                                      cellphone}},
                        calib_trials,
                        menton_pools,
                        participants,
                        cellphone_costs,
                        step_times)

#p = 0.32 works! interesting that we simply had to remove
# the divisor in eq above to get it to work. treatment in
# writeup?

#now we have values for every task, AND an estimate of people's
# overall menton capacity!

print 'people\'s menton capacity as predicted by the go/no-go:'
print 'about ' + str(factor/2)
print 'cost of visual go/no-go: 1'
print 'cost of driving: '+str(sum([control_costs[drive][i+1] for i in range(2)]))
print 'cost of listening to radio: ' + str(sum([radio_costs[radio][i+1] for i in range(2)]))
print 'cost of talking on cellphone: ' + str(sum([cellphone_costs[cellphone][i+1] for i in range(2)]))

#we get nifty predictions from this. like that talking on the cellphone is harder
# than driving... (run the above) and also that listening to
# radio is harder than a go/no-go. these suggest new expts that
# can now work to confirm/reject menton theory!

