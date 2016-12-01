'''CGSC 4001/5001 Can Mekik, Josh Noronha, and Zahrah Hajali'''

# This is a toy model demonstrating our system. It was what was
# run in our presentation

from ProductionSystem import *
from MentonEngine import *

#productions

#productions for driving task


# arrow => 
# node  =>
drive = Production(
    Precondition(
        set(),
        {
            Node('Light flash'),
            Arrow(
                (
                Node('Is'), 
                Node('Light flash'), 
                Node('Red')
                )
                )
        }
    ),
    Action({Node('Maintain course')})
)

lookout = Production(
    Precondition(
        set(),
        {Node('Observed light')}),
    Action({Node('Looking out')}))

observe = Production(
    Precondition(
        {Node('Light flash'), Node("Looking out")},
        {Node('Observed light')}),
    Action(
        {Node('Observed light')},
        {Node ("Looking out"), Node("Maintain course")}))

stop = Production(
    Precondition(
        {Node("Light flash"),
         Node("Observed light"),
         Arrow((Node("Is"), Node("Light flash"), Node("Red")))},
        {Node('Stopped')}),
    Action({Node("Stopped")}))

#dual task proudctions
#coming soon.

productions = {drive, lookout, observe, stop}
knowledge = Knowledge({Node("No initial system knowledge")})

#menton engine
engine = MentonEngine()
pools = {'Perceptual' : 3, 'Motor/Planning' : 3}
capacities = {'Perceptual' : 5, 'Motor/Planning' : 5}
rates = {'Perceptual' : 2, 'Motor/Planning' : 2}
costs = {drive : {'Perceptual' : 1, 'Motor/Planning' : 1},
         lookout : {'Perceptual' : 1},
         observe : {'Perceptual' : 1},
         stop : {'Motor/Planning' : 5}}
priorities = {drive : 1,
              lookout : 1,
              observe : 1,
              stop : 1}

parameters = (pools, capacities, rates, costs, priorities)
system = ProductionSystem(knowledge, productions, engine.bind, parameters)


system.step()
print "State of the Mentons in step 1: " + str(engine.pools)
system.knowledge.add({Node('Light flash'),
                      Arrow((Node("Is"),
                             Node("Light flash"),
                             Node("Red")))})
for i in range(3):
    system.step()
    print "State of the Mentons in step " + str(i+2) + ": " + str(engine.pools)
print '\n'+system.log