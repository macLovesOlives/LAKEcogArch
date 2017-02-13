from ProductionSystem import *
import lake

# knowledge: None
# if nothing exists:
#   Draw a circle
# if a circle exists
#   draw a second circle
# if two circles exist
#   draw the fucking owl

draw_head = Production(
    Precondition(
        set(),
        {
            Node('Blank Slate'),
            Arrow(
                (
                Node('Is'),
                Node('Paper'),
                Node('Blank')
                )
                )
        }
    ),
    Action({Node('Drawing circle')})
)

draw_body = Production(
    Precondition(
        set(),
        {Node('Drawing circle')}),
    Action({Node('Drawing second circle')}))

owl = Production(
    Precondition(
        {Node('Drawing circle'), Node('Drawing second circle'),
         Node('Getting sh*t done.')}),
    Action(
        {Node('Draw the f*cking owl')}))

done = Production(
    Precondition(
        {Node('Drawing circle'), Node('Drawing second circle')}),
    Action(
        {Node('Getting sh*t done.')}))


productions = {draw_body, draw_head, owl}
knowledge = Knowledge({Node("No initial system knowledge")})

engine = lake.Mind("test_mind")

pools =              {'Visuo-Spatial': 3, 'Motor/Planning': 3}
capacities =         {'Visuo-Spatial': 5, 'Motor/Planning': 5}
rates =              {'Visuo-Spatial': 2, 'Motor/Planning': 2}
costs = {draw_body:  {'Visuo-Spatial': 1},
         draw_head:  {'Visuo-Spatial': 1},
         owl:        {'Visuo-Spatial': 1, 'Motor/Planning': 1},
         done:       {'Visuo-Spatial': 1, 'Motor/Planning': 3}}
priorities = {draw_body: 1,
              draw_head: 1,
              owl: 1,
              done: 1}

parameters = (pools, capacities, rates, costs, priorities)
system = ProductionSystem(knowledge, productions, engine.bind, parameters)


system.step()
print "State of the Mentons in step 1: "
for i in range(len(engine.mentonPools)):
    print(str(engine.mentonPools[i].name) + ": " + str(engine.mentonPools[i].mentons))
system.knowledge.add({Node('Blank Slate'),
                      Arrow((Node("Is"),
                             Node("Paper"),
                             Node("Blank")))})
for i in range(3):
    system.step()
    print "State of the Mentons in step " + str(i+2) + ": "
    for i in range(len(engine.mentonPools)):
        print(str(engine.mentonPools[i].name) + ": " + str(engine.mentonPools[i].mentons))

print '\n'+system.log