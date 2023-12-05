import pynusmv
import sys
from pynusmv_lower_interface.nusmv.parser import parser 
from collections import deque
import pdb

specTypes = {'LTLSPEC': parser.TOK_LTLSPEC, 'CONTEXT': parser.CONTEXT,
    'IMPLIES': parser.IMPLIES, 'IFF': parser.IFF, 'OR': parser.OR, 'XOR': parser.XOR, 'XNOR': parser.XNOR,
    'AND': parser.AND, 'NOT': parser.NOT, 'ATOM': parser.ATOM, 'NUMBER': parser.NUMBER, 'DOT': parser.DOT,

    'NEXT': parser.OP_NEXT, 'OP_GLOBAL': parser.OP_GLOBAL, 'OP_FUTURE': parser.OP_FUTURE,
    'UNTIL': parser.UNTIL,
    'EQUAL': parser.EQUAL, 'NOTEQUAL': parser.NOTEQUAL, 'LT': parser.LT, 'GT': parser.GT,
    'LE': parser.LE, 'GE': parser.GE, 'TRUE': parser.TRUEEXP, 'FALSE': parser.FALSEEXP
}

basicTypes = {parser.ATOM, parser.NUMBER, parser.TRUEEXP, parser.FALSEEXP, parser.DOT,
              parser.EQUAL, parser.NOTEQUAL, parser.LT, parser.GT, parser.LE, parser.GE}
booleanOp = {parser.AND, parser.OR, parser.XOR, parser.XNOR, parser.IMPLIES, parser.IFF}

def spec_to_bdd(model, spec):
    """
    Given a formula `spec` with no temporal operators, returns a BDD equivalent to
    the formula, that is, a BDD that contains all the states of `model` that
    satisfy `spec`.
    The `model` is a symbolic representation of the loaded smv program that can be
    obtained with `pynusmv.glob.prop_database().master.bddFsm`.
    """
    bddspec = pynusmv.mc.eval_simple_expression(model, str(spec))
    return bddspec
    
def is_boolean_formula(spec):
    """
    Given a formula `spec`, checks if the formula is a boolean combination of base
    formulas with no temporal operators. 
    """
    if spec.type in basicTypes:
        return True
    if spec.type == specTypes['NOT']:
        return is_boolean_formula(spec.car)
    if spec.type in booleanOp:
        return is_boolean_formula(spec.car) and is_boolean_formula(spec.cdr)
    return False
    
def is_GF_formula(spec):
    """
    Given a formula `spec` checks if the formula is of the form GF f, where f is a 
    boolean combination of base formulas with no temporal operators.
    Returns True if `spec` is in the correct form, False otherwise 
    """
    # check if formula is of type GF f_i
    if spec.type != specTypes['OP_GLOBAL']:
        return False
    spec = spec.car
    if spec.type != specTypes['OP_FUTURE']:
        return False
    return is_boolean_formula(spec.car)

def parse_implication(spec):
    """
    Visit the syntactic tree of the formula `spec` to check if it is a simple 
    reactivity formula, that is wether the formula is of the form
    
                    GF f -> GF g
    
    where f and g are boolean combination of basic formulas.
    """
    # the root of a reactive formula should be of type IMPLIES
    if spec.type != specTypes['IMPLIES']:
        return False
    # Check if lhs and rhs of the implication are GF formulas
    return is_GF_formula(spec.car) and is_GF_formula(spec.cdr)
    
def parse_react(spec):
    """
    Visit the syntactic tree of the formula `spec` to check if it is a Reactivity 
    formula, that is wether the formula is of the form
    
        (GF f_1 -> GF g_1) & ... & (GF f_n -> GF g_n)
    
    where f_1, ..., f_n, g_1, ..., g_n are boolean combination of basic formulas.
    
    Returns True if `spec` is a Reactivity formula, False otherwise.
    """
    # the root of a spec should be of type CONTEXT
    if spec.type != specTypes['CONTEXT']:
        return None
    # the right child of a context is the main formula
    spec = spec.cdr
    # check all conjuncts of the main formula
    working = deque()
    working.append(spec)
    while working:
        # next formula to analyse
        head = working.pop()
        if head.type == specTypes['AND']:
            # push conjuncts into the queue
            working.append(head.car)
            working.append(head.cdr)
        else:
            # check if it is a GF f -> GF g formula
            if not parse_implication(head):
                return False
    # if we are here, all conjuncts are of the correct form
    return True

def check_explain_react_spec(spec):
    """
    Returns whether the loaded SMV model satisfies or not the reactivity formula
    `spec`, that is, whether all executions of the model satisfies `spec`
    or not. Returns also an explanation for why the model does not satisfy
    `spec`, if it is the case.

    The result is `None` if `spec` is not a reactivity formula, otherwise it is a 
    tuple where the first element is a boolean telling whether `spec` is satisfied, and the second element is either `None` if the first element is `True`, or an execution
    of the SMV model violating `spec` otherwise. 

    The execution is a tuple of alternating states and inputs, starting
    and ending with a state. The execution is looping: the last state should be 
    somewhere else in the sequence. States and inputs are represented by dictionaries
    where keys are state and inputs variable of the loaded SMV model, and values
    are their value.
    """
    if not parse_react(spec):
        return None
    
    def retrieve_base_formulas_couples(spec):
        # assert parse_react(spec)
        spec = spec.cdr  # the right child of a context is the main formula
        # extract base formulas from all conjuncts
        couples = []
        working = deque()
        working.append(spec)
        while working:
            # next formula
            head = working.pop()
            if head.type == specTypes['AND']:
                # push conjuncts into the queue
                working.append(head.car)
                working.append(head.cdr)
            else:
                # extract base formulas from implication
                # assert parse_implication(head)
                couples.append((head.car.car.car, head.cdr.car.car))
        return couples
    
    couples = retrieve_base_formulas_couples(spec)

    def check_repeatability(fsm, spec):
        """
        Returns a couple (True, None) if and only if
        the property spec (which must NOT be converted bdd)
        is repeatable basing on fsm, which is the symbolic representation
        of the loaded NuSMV model.

        Note that the second element of the couple should be
        a counter example whenever the property is not repeatable.
        But at the moment the computation of a counter example is not yet implemented.
        """
        def is_subset(first_set, second_set, fsm):
            """
            Returns True if and only if 
            the first set of states is included in the second set of states
            basing on fsm, which is the symbolic representation
            of the loaded NuSMV model 
            """
            return fsm.count_states(first_set.diff(second_set)) == 0
        bdd = spec_to_bdd(fsm, spec)
        reach = fsm.init
        new = fsm.init
        while new != None:
            new = None if is_subset(fsm.post(new), reach, fsm) else fsm.post(new).diff(reach)
            reach = reach if new == None else reach.union(new)
        assert reach.equal(fsm.reachable_states)
        recur = None if not reach.intersected(bdd) else reach.intersection(bdd)
        while recur != None:
            reach = None
            new = fsm.pre(recur)
            while new != None:
                reach = new if reach == None else reach.union(new)
                if (is_subset(recur, reach, fsm)):
                    assert pynusmv.mc.check_ltl_spec(pynusmv.prop.g(pynusmv.prop.f(spec))) 
                    return (True, None)
                new = None if is_subset(fsm.pre(new), reach, fsm) else fsm.pre(new).diff(reach)
            recur = None if not recur.intersected(reach) else recur.intersection(reach)
        assert not pynusmv.mc.check_ltl_spec(pynusmv.prop.g(pynusmv.prop.f(spec)))     
        return (False, None)
    
    fsm = pynusmv.glob.prop_database().master.bddFsm

    for couple in couples:
        check_repeatability(fsm, couple[0])
        check_repeatability(fsm, couple[0])

    return pynusmv.mc.check_explain_ltl_spec(spec)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:", sys.argv[0], "filename.smv")
        sys.exit(1)

    pynusmv.init.init_nusmv()
    filename = sys.argv[1]
    pynusmv.glob.load_from_file(filename)
    pynusmv.glob.compute_model()
    type_ltl = pynusmv.prop.propTypes['LTL']
    for prop in pynusmv.glob.prop_database():
        spec = prop.expr
        print(spec)
        if prop.type != type_ltl:
            print("property is not LTLSPEC, skipping")
            continue
        res = check_explain_react_spec(spec)
        if res == None:
            print('Property is not a Reactivity formula, skipping')
        elif res[0] == True:
            print("Property is respected")
        elif res[0] == False:
            print("Property is not respected")
            print("Counterexample:", res[1])

    pynusmv.init.deinit_nusmv()
