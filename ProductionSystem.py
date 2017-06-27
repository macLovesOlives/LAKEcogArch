'''CGSC 4001/5001 Can Mekik, Josh Noronha, and Zahrah Hajali'''
""" minor edits and changes made by Mackenzie Ostler """

# This module provides the ProductionSystem class, which is a
# customizable production system building kit.

class _NetElt(object):
    """A _NetElt instance is an element of a semantic network. _NetElt
    instances are unique up to their labels.

    _NetElt is the base class for the knowledge structure of
    ProductionSystem. It provides definitions for several builtins and
    key methods.
    """

    instances = {}

    def __new__(cls, label):
        """If an instance of cls with label has not yet been created,
        create a new instance of cls with label and return it, otherwise
        return the existing instance."""

        if label in cls.instances:
            return cls.instances[label]
        obj = object.__new__(cls)
        cls.instances[label] = obj
        obj.__init__(label)
        return obj

    def __init__(self, label):
        """Initialize an instance of _NetElt."""

        self.label = label

    def __eq__(self, other):
        """Return if self is equal to other. Two _NetElt instances are
        considered equal if they represent the same thing (i.e. if they have
        the same label, see _NetElt.__init__)."""

        if isinstance(other, self.__class__):
            return self.label == other.label
        return False

    # Python requires __hash__ be implemented for instances to be passable
    # into lists, sets and other iterables.

    def __hash__(self):
        """Return hash of self."""

        return hash(self.label)

    def match(self, others):

        matches = []
        for other in others:
            matches.append(self.match_shape(other))
        return any(matches)

    def match_shape(self, other):

        if not self._match_shape(other):
            # clear variable _bindings for other
            return False
        else:
            return True

    def _match_shape(self, other):
        """Return True if self matches elt in shape. Add candidates to
        variables as you traverse elt."""

        # This method basically behaves like _NetElt.__eq__, but it does
        # tricky things when it encounters Variables. See
        # Variable.match_shape.

        if not isinstance(other, self.__class__):
            return False

        matches = set()
        for idx in range(len(self.label)):
            if not isinstance(self.label[idx], _NetElt):
                matches.add(self.label[idx] == other.label[idx])
            else:
                matches.add(self.label[idx].match_shape(other.label[idx]))
        if all(matches):
            Variable.add_variables(self, other)
            return True
        return False


class _Node(_NetElt):
    """_Node implements the __repr__ function for the Node and Variable
    classes."""

    instances = {}
    _repr = 'BN'

    def __init__(self, label):
        """Initialize an instance of _Node."""

        _NetElt.__init__(self, (label,))
        self._repr = self.__class__._repr

    def __repr__(self):
        """Return str representation of self."""

        return self._repr + '(' + str(self.label[0]) + ')'


class Node(_Node):
    """An atomic bit of memory. This was adapted from the Chunk1 class."""

    instances = {}
    _repr = 'N'


class Variable(_Node):
    """A node representing a named slot. To be used only in production
    preconditions or production actions. Variable objects will not cause
    interesting behaviour if they are placed in system knowledge."""

    instances = {}
    active = set()
    _repr = 'V'

    @classmethod
    def clear_active(cls):

        for variable in cls.active:
            variable.clear()

    @classmethod
    def add_variables(cls, self, other):
        """For each cpt of self if cpt is a variable, add corresponding cpt
        of other to the variable _bindings of the variable cpt of self."""

        for idx in range(len(self.label)):
            if isinstance(self.label[idx], Variable):
                self.label[idx].add_candidate(self, other.label[idx])

    def __init__(self, label, pattern=None):
        """Initialize an instance of Variable, which is used to express rules
        and patterns.

        label is a string that represents the name of Variable."""

        _Node.__init__(self, label)

        # self._bindings is a dictionary of current binding candidates
        self._bindings = {}
        self.pattern = pattern

    def add_candidate(self, elt, k):
        """Assign self to _NetElt instance k."""

        if elt in self._bindings:
            self._bindings[elt].add(k)
        else:
            self._bindings[elt] = set().add(k)

    def clear(self):
        """Clear variable assignments for self."""

        self.__class__.active.remove(self)
        self._bindings = {}

    def matches(self):
        """Return the set of _NetElt instances matching constraints."""

        matches = {}
        for elt in self._bindings:
            matches |= self._bindings[elt]
        for elt in self._bindings:
            matches &= self._bindings[elt]
        return matches

    def _match_shape(self, elt):

        # elt better not be a Variable instance. Not sure what will
        # happen if it is.
        if isinstance(elt, _NetElt):
            return True
        else:
            return False


class Arrow(_NetElt):
    """A bit of memory that has 3 parts. This was adapted from the Chunk3
    class.

    To represent 'Mary loves Kate', simply write Arrow((loves, mary, kate)),
    where mary, loves and kate are Node instances each representing Mary,
    loving and Kate respectively. This is different from inputting
    Arrow((loves, kate, mary)) which should be understood as 'Kate loves
    Mary'."""

    instances = {}

    def __init__(self, (rel, src, tgt)):
        """Initialize an instance of Arrow, which is a  3-part piece of
        knowledge in memory. Essentially, Arrow captures a relation between
        source and target.

        rel is a Node instance
        src is a Node instance
        tgt is a Node instance
        """

        _NetElt.__init__(self, (rel, src, tgt))

        # Warning: Changing the referents of any of self.rel, self.src,
        # self.tgt risks corrupting the Arrow instance. Instead create a
        # new instance and remove the old one.
        self.rel = rel
        self.src = src
        self.tgt = tgt

    def __repr__(self):
        """Return str representation of self."""

        return str(self.rel) + ': ' + str(self.src) + ' -> ' + \
               str(self.tgt)


class Knowledge:
    """Represents some knowledge. Can check if two bits of knowledge match and
    if one bit is an instance of another bit. Knowledge is stored as a
    semantic network. Knowledge can be added and removed.

    The semantic network is represented as a list of Node and Arrow instances.
    For details, see the Node and Arrow classes.

    This was adapted from the Knowledge class."""

    catMarker = {True: '', False: '~'}

    # add and remove both depend on == working right, this is assured in
    # _NetElt.__eq__.

    def __init__(self, t, f=set()):
        """Initializes Knowledge object. t, f are set objects containing the
        nodes and vertices of a semantic network.

        t is a set representing true facts.
        f is a set representing false facts."""

        # self.semanticCategories facilitates redundancy control
        # in method code.
        self.semanticCategories = {True: t, False: f}

    def __repr__(self):
        """Return a representation of self. Returns a str representing every
        node and vertex in self.t and in self.f."""

        accumulator = [str(self.__class__.__name__)]
        for category in self.semanticCategories:
            for item in self.semanticCategories[category]:
                accumulator.append('    ' + \
                                   Knowledge.catMarker[category] + \
                                   str(item))
        return '\n'.join(accumulator) + '\n'

    def add(self, k, category=True):
        """Unions set k with self.t. If value is False, unions k with self.f
        instead."""

        self.semanticCategories[category] |= k

    def remove(self, k, category=True):
        """Removes elements of set k from self.t. If value is False, removes
        elements of set k from self.f instead."""

        self.semanticCategories[category] -= k

    def find(self, k, category=True):
        """Return True if k is a subset of self.t. If value is False, return
        true if k is a subset of self.f instead."""

        for item in k:
            if not item.match(self.semanticCategories[category]):
                return False
        return True

    def elements(self, category):
        """Returns all elements in a given semantic category."""

        return self.semanticCategories[category]


class Precondition(Knowledge):
    """Represents a production precondition."""

    def __call__(self, system):
        return system.knowledge.find(self.elements(True)) and \
               (self.elements(False) == set() or
                not system.knowledge.find(self.elements(False)))


class Action(Knowledge):
    """Represents a production action.

    Warning: Action instances do not do any conflict resolution. Production
    system knowledge may be rendered inconsistent if an action is fired
    without appropriate conflict resolution. Conflict resolution should be
    taken care of in the production system interpreter. See the Interpreter
    class."""

    def __call__(self, system):
        """Execute Action. Add knowledge to be added to system, remove
        knowledge to be removed. In that order."""

        system.knowledge.add(self.elements(True))
        system.knowledge.remove(self.elements(False))


class Production:
    """Checks preconditions, fires actions.

    Warning: Production objects must be bound to a ProductionSystem, otherwise
    they may not be fired (called). Binding can be done with the
    Production.bind class method.

    This was adapted from the Production class."""

    def __init__(self, precondition, action):
        """Initialize a Production.

        precondition is an instance of the Precondition class
        action is an instance of the Action class."""

        self.precondition = precondition
        self.action = action
        self.system = None

    def __call__(self):
        if self.system.interpreter.choose(self):
            self.action(self.system)
            self.system.publish(str(self))

    def __repr__(self):
        return ('Production\n    ' +
                str(self.precondition).replace('\n', '\n    ') +
                str(self.action).replace('\n', '\n    ').rstrip('    ')). \
                   rstrip() + '\n'

    def bind(self, system):
        """Bind self to system.

        This method lets the production know which ProductionSystem it should
        affect. Given the implementation of ProductionSystem.__init__,
        productions must be bound to the system after both they and the
        system are initialized."""

        self.system = system


class AllSatisfied:
    """A production system decision procedure. Fires every production whose
    preconditions are satisfied."""

    def __init__(self):
        """Initialize the procedure."""
        self.productions = None
        self.parameters = None

    def __call__(self):
        """Return a dictionary whose keys are system productions and whose
        values are booleans indicating whether a production fires in current
        simulation step or not."""

        fire = {}
        for p in self.productions:
            fire.__setitem__(p, p.precondition(p.system))
        return fire

    def bind(self, productions, parameters=None):
        """Bind self to system productions with desired parameters."""

        self.productions = productions
        self.parameters = parameters
        return self


class Interpreter:
    """Chooses which productions can be fired."""

    # This class can be extended to have dynamic decision procedures
    # such as adding or removing productions to the decision procedure.

    def __init__(self, productions, bind_procedure=AllSatisfied().bind,
                 parameters=None):
        """Initialize interpreter.

        productions is a the list of productions active in the production
        system.

        parameters is an optional list of parameters to be used with
        bind_procedure.

        bind_procedure is a callable. It should take the list of
        productions and any additional parameters (in the form of a list) and
        return a callable. The returned callable will be used to determine
        whether a given production will fire. The callable should return a
        dictionary where the keys are the production system's productions and
        the values are whether the production gets fired during the cycle. The
        callable should take care of all conflict resolution issues."""

        # Initialize decision procedure
        self.decisionProcedure = bind_procedure(productions, parameters)
        # Initialize production firing information
        self.fire = {}
        for p in productions:
            self.fire[p] = False

    def step(self):
        """Run one step of the decision procedure, update production firing
        information."""

        self.fire = self.decisionProcedure()

    def choose(self, production):
        """Return whether production can be fired."""

        return self.fire[production]


class ProductionSystem:
    """Runs productions, maintains knowledge."""

    # The log will probably work for small scale simulations, with larger
    # simulations memory might run out. Consider periodically dumping the log
    # into a file. This would require something like a self.name, and a
    # suitable adjustment to ProductionSystem._log_step

    def __init__(self, knowledge, productions,
                 bind_procedure=AllSatisfied().bind, parameters=None):
        """Initialize ProductionSystem.

        knowledge is an instance of the Knowledge class.
        productions is a set of Production instances.
        interpreter is an Interpreter object.

        For information about bind_procedure and parameters, see the
        Interpreter class."""

        self.knowledge = knowledge
        # Bind productions to self. See Production class.
        for p in productions:
            p.bind(self)
        self.productions = productions
        self.interpreter = Interpreter(productions, bind_procedure, parameters)
        # Initialize system log.
        self._init_log()

    def step(self):
        """Run through productions once."""

        self.interpreter.step()
        self._log_step()
        # Run through each production
        for production in self.productions:
            production()

    def publish(self, message):
        """Write message to self's log."""

        # See inline comments directly below class declaration.

        self.log += message

    def _init_log(self):
        """Initialize ProductionSystem log. Updated every step."""

        # See inline comments directly below class declaration.

        self.step_count = 0
        self.log = 'PRODUCTION SYSTEM INITIALIZED.\n\n' + 'System ' + \
                   str(self.knowledge) + '\n' + 'System Productions\n    ' + \
                   ''.join([str(p) for p in self.productions]). \
                       replace('\n', '\n    ')

    def _log_step(self):
        """Update ProductionSystem log with the state of the knowledge of the
        system, and which productions are firing in current step."""

        # See inline comments directly below class declaration.

        self.step_count += 1
        self.log += '\n\n' + 'STEP ' + str(self.step_count) + '\n\n' + \
                    'System ' + str(self.knowledge) + '\n'
