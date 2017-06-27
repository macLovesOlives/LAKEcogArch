from ProductionSystem import *
import lake


def draw_the_owl():
    """ source: Pulsatrix perspicillata
        http://www.ascii-art.de/ascii/mno/owl.txt """
    print "                             ____"
    print "                          ,''    ''."
    print "                         / `-.  .-' \\"
    print "                        /( (O))((O) )"
    print "                       /'-..-'/\`-..|"
    print "                     ,'\   `-.\/.--'|"
    print "                   ,' ( \           |"
    print "                 ,'( (   `._        |"
    print "                /( (  ( ( | `-._ _,-;"
    print "               /( (  ( ( (|     '  ;"
    print "              / ((  (    /        /"
    print "             //         /        /"
    print "             //  / /  ,'        /"
    print "            // /    ,'         /"
    print "            //  / ,'          ;"
    print "            //_,-'          ;"
    print "            // /,,,,..-))-))\    /|"
    print "              /; ; ;\ `.  \  \  / |"
    print "             /; ; ; ;\  \.  . \/./"
    print "            (; ; ;_,_,\  .: \   /"
    print "             `-'-'     | : . |:|"
    print "                       |. | : .|"


draw_head = Production(
    Precondition(
        {
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
           {Node('No initial system knowledge'),
            Arrow((Node('Is'), Node('Paper'), Node('Blank'))),
            Arrow((Node("Is"),
                   Node("Paper"),
                   Node("Blank"))
                  )
            })
)

draw_body = Production(
    Precondition(
        {Node('Drawing circle')}),
    Action({Node('Drawing second circle'), Node('Top circle')}, {Node('Drawing circle')}))

owl_lame = Production(
    Precondition(
        {Node('Top circle'), Node('Bottom circle'),
         Node('Getting sh*t done.')}),
    Action(
        {Node('Draw the owl')}))

owl_cool = Production(
    Precondition(
        {Node('Top circle'), Node('Bottom circle'),
         Node('Getting SH*T done.')}),
    Action(
        {Node('Draw the f*cking owl')}))

done = Production(
    Precondition(
        {Node('Top circle'), Node('Drawing second circle')}),
    Action(
        {Node('Getting sh*t done.'), Node('Bottom circle')}, {Node('Drawing second circle')}))


more_done = Production(
    Precondition(
        {Node('Top circle'), Node('Drawing second circle')}),
    Action(
        {Node('Getting SH*T done.'), Node('Bottom circle')}, {Node('Drawing second circle')}))


mic_drop = Production(
    Precondition(
        {Node('Draw the f*cking owl')}
    ),
    Action(
        {Node('MIC DROP')}
    )
)

productions = {draw_body, draw_head, owl_lame, owl_cool, more_done, mic_drop}
knowledge = Knowledge({Node("No initial system knowledge")})

engine = lake.Mind("Shopify's mind")

pools = {'Visuo-Spatial': 1000, 'Motor/Planning': 1000}
capacities = {'Visuo-Spatial': 1000, 'Motor/Planning': 1000}
rates = {'Visuo-Spatial': 400, 'Motor/Planning': 400}
costs = {draw_body: {'Visuo-Spatial': 200},
         draw_head: {'Visuo-Spatial': 200},
         owl_lame:  {'Visuo-Spatial': 200, 'Motor/Planning': 200},
         owl_cool:  {'Visuo-Spatial': 400, 'Motor/Planning': 400},
         # done:      {'Visuo-Spatial': 200, 'Motor/Planning': 600},
         more_done: {'Visuo-Spatial': 600, 'Motor/Planning': 800},
         mic_drop:  {'Visuo-Spatial': 200, 'Motor/Planning': 600}}
priorities = {draw_body: 1,
              draw_head: 1,
              owl_lame: 1,
              owl_cool: 3,
              # done: 1,
              more_done: 3,
              mic_drop: 3}

parameters = (pools, capacities, rates, costs, priorities)
system = ProductionSystem(knowledge, productions, engine.bind, parameters)

system.step()
print "State of the Mentons in step 1: "
for i in range(len(engine.mentonPools)):
    print(str(engine.mentonPools[i].name) + ": " + str(engine.mentonPools[i].mentons))
system.knowledge.add({Arrow((Node("Is"),
                             Node("Paper"),
                             Node("Blank")))})
for i in range(5):
    system.step()
    print "\nState of the Mentons in step " + str(i + 2) + ": "
    for j in range(len(engine.mentonPools)):
        print(str(engine.mentonPools[j].name) + ": " + str(engine.mentonPools[j].mentons))

print '\n' + system.log

draw_the_owl()

