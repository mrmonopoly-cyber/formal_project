import pynusmv
import sys
from collections import deque

from utils import *
from pretty_printing import *
import pdb

def check_explain_react_spec(spec):


    def get_atomic_subformulas(spec):
        """
        If and only if `prop` is a reactivity formula,
        returns a list containing a pair (${atomic_premise}, ${atomic_conclusion})
        for each conjunct implication, where:
        
        1.  ${atomic_premise} is the atomic subformula corresponding to the premise of the implication
            without temporal operators  
        2.  ${atomic_conclusion} is the atomic subformula corresponding to the conclusion of the implication
            without temporal operators
        """
        spec = prop.expr
        spec = spec.cdr  # the right child of a context specification is the main formula
        # region EXTRACT_ATOMIC_SUBFORMULAS_COUPLES_FOR_EACH_CONJUNCT
        pairs = []
        working = deque()
        working.append(spec)
        while working:
            head = working.pop() # extract current formula from the queue
            if head.type == specTypes['AND']:
                # region PUSH_FIRST_CONJUNCT_AND_REMAINING_SUBFORMULA_INTO_THE_QUEUE
                working.append(head.car)
                working.append(head.cdr)
                # endregion
            else:
                pairs.append((head.car.car.car, head.cdr.car.car)) # retrieve atomic formulas from implication
        # endregion
        return pairs

    def check_reactivity_formula_conjunct(model, spec_f, spec_g):
        """
        Given a system model `model` represented as a bdd
        and two atomic specs `spec_f` and `spec_g`,
        returns True if and only if GF f -> GF g holds.

        Returns False otherwise
        """

        f = spec_to_bdd(model, spec_f)
        not_g = spec_to_bdd(model, spec_g).not_()

        # region GET_REACHABLE_STATES
        reach = model.init
        new = model.init

        while model.count_states(new) > 0:
            new = (model.post(new)).diff(reach)
            reach = reach.union(new)
        # endregion

        # region CHECK_REPEATABILITY_OF_BUCHI_AUTOMATON_BAD_STATE
        recur = (reach.intersection(f)).intersection(not_g)
        while model.count_states(recur) > 0:
            prereach = pynusmv.fsm.BDD.false(model) # start with an empty prereach 
            new = model.pre(recur).intersection(not_g)
            while model.count_states(new) > 0:
                prereach = prereach.union(new)
                if recur.entailed(prereach):
                    return (False, None)
                new = ((model.pre(new)).intersection(not_g)).diff(prereach)
            recur = recur.intersection(prereach)
        return (True, None)
        # endregion
    
    
    model = model = pynusmv.glob.prop_database().master.bddFsm
    couples = get_atomic_subformulas(spec)

    for couple in couples:
        result = check_reactivity_formula_conjunct(model, couple[0], couple[1])
        if not result[0]:
            return (result[0], result[1], couple)
    return (True, None, None)

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
        print()
        print("Analyzing property %s..." % spec)
        if prop.type != type_ltl:
            warn("...property is not LTLSPEC, skipping")
            continue
        if not parse_react(spec):
            warn("...property is not a Reactivity formula, skipping")
            continue
        res = check_explain_react_spec(spec)
        if res[0] == True:
            assert pynusmv.mc.check_ltl_spec(spec)
            success("...property is respected!")
        else:
            assert not pynusmv.mc.check_ltl_spec(spec)
            error("...property is not respected, as demonstrated by the following counterexample:")
            
    pynusmv.init.deinit_nusmv()
