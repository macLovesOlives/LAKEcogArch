from ProductionSystem import *
import lake

# knowledge: None
# if nothing exists:
#   Draw a circle
# if a circle exists
#   draw a second circle
# if two circles exist
#   get sh*t done
# if you got sh*t done AND you drew two circles
#   draw the f*cking owl

draw_head = Production(
    Precondition(
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
    Action({Node('Drawing circle')},
           {Node('Blank Slate'),
            Arrow((Node('Is'), Node('Paper'), Node('Blank'))),
            Node('Blank Slate'),
            Arrow((Node("Is"),
                   Node("Paper"),
                   Node("Blank"))
                  )
            })
)

draw_body = Production(
    Precondition(
        {Node('Drawing circle')}),
    Action({Node('Drawing second circle')}))

owl = Production(
    Precondition(
        {Node('Drawing circle'), Node('Drawing second circle'),
         Node('Getting SH*T done.')}),
    Action(
        {Node('Draw the f*cking owl')}))

done = Production(
    Precondition(
        {Node('Drawing circle'), Node('Drawing second circle')}),
    Action(
        {Node('Getting sh*t done.')}))


more_done = Production(
    Precondition(
        {Node('Drawing circle'), Node('Drawing second circle')}),
    Action(
        {Node('Getting SH*T done.')}))

productions = {draw_body, draw_head, owl, done, more_done}
knowledge = Knowledge({Node("No initial system knowledge")})

engine = lake.Mind("test_mind")

pools = {'Visuo-Spatial': 3, 'Motor/Planning': 3}
capacities = {'Visuo-Spatial': 5, 'Motor/Planning': 5}
rates = {'Visuo-Spatial': 2, 'Motor/Planning': 2}
costs = {draw_body: {'Visuo-Spatial': 1},
         draw_head: {'Visuo-Spatial': 1},
         owl: {'Visuo-Spatial': 1, 'Motor/Planning': 1},
         done: {'Visuo-Spatial': 1, 'Motor/Planning': 3},
         more_done: {'Visuo-Spatial': 3, 'Motor/Planning': 4}}
priorities = {draw_body: 1,
              draw_head: 1,
              owl: 1,
              done: 1,
              more_done: 3}

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
for i in range(5):
    system.step()
    print "\nState of the Mentons in step " + str(i + 2) + ": "
    for j in range(len(engine.mentonPools)):
        print(str(engine.mentonPools[j].name) + ": " + str(engine.mentonPools[j].mentons))

print '\n' + system.log
