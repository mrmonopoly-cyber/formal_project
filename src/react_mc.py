import pynusmv
import sys
from collections import deque

from utils import *
from pretty_printing import *


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
        # `recur` is the region containing those states whose repeated occurrence indicates failure
        recur = (reach.intersection(f)).intersection(not_g) 
        while model.count_states(recur) > 0: # stop when `recur` is empty
            # `prereach` is the region containing all `recur`'s ancestors
            prereach = pynusmv.fsm.BDD.false(model) 
            new = model.pre(recur).intersection(not_g) # get `recur`'s direct ancestors
            while model.count_states(new) > 0: # stop when no more ancestors are found
                prereach = prereach.union(new)
                if recur.entailed(prereach): # stop when `prereach` is a superset of `recur`
                    # If at a certain iteration `i` `recur` becomes a subset of `prereach`,
                    # `recur` is basically an ancestor of itself and so a cycle has been found
                    return (False, get_counter_example(model, recur, prereach))
                new = ((model.pre(new)).intersection(not_g)).diff(prereach) # get the n-th region of `recur`'s ancestors
            recur = recur.intersection(prereach)
        # If at a certain iteration `i` `recur` becomes empty,
        # then an execution with length `i` starting from a reachable "bad" state
        # and built only with "bad" states doesn't exist.
        # `spec` is so satisfied
        return (True, None)
        # endregion

    def get_counter_example(model, recur, prereach):
        """
        Given a system model `model` represented as a bdd.
        a region `recur` represented with a BDD
        and a region `prereach` represented with a BDD such that:

        1. `recur` is the region containing those states whose repeated occurrence indicates failure
        2. `prereach` is the region containing all `recur`'s ancestors

        returns an execution such that:
        
        1. the execution starts from an initial state of `model`
        2. the execution reaches a state in `recur`
        3. the aforementioned state reappears as the last element of the execution, highlighting a loop
        """
        s = model.pick_one_state(recur)
        is_s_in_r = False
        frontiers = [] # to keep track of each computed `s`'s successor

        # region FIND_LOOP
        while not is_s_in_r:
            # start with an empty `r`
            r = pynusmv.fsm.BDD.false(model)    # `r` ≝ { t ∈ `recur` | t is reachable from `s`
                                                #                       with a path of length ≥ 1
                                                #                       entirely contained in `prereach` }
            # get `s`'s direct successors which are also in `prereach`
            new = (model.post(s)).intersection(prereach) 
            while model.count_states(new) > 0: # stop when no more successors in `prereach` are found
                frontiers.append(new)
                r = r.union(new)
                # get the n-th region of `s`'s successors which is also in `prereach`
                new = ((model.post(new)).intersection(prereach)).diff(r)
            r = r.intersection(recur)
            is_s_in_r = s.entailed(r)
            if not is_s_in_r:
                # if `s` is in not `r` then it is not reachable from itself
                # with a path entirely contained in `prereach`, so a new state must be picked
                s = model.pick_one_state(r)
                frontiers = []
        # endregion

        # region BUILD_LOOP
        k = 0
        while k < len(frontiers) and not s.entailed(frontiers[k]):
            # search the first region of ancestors containing `s`
            k = k + 1
        # tuples of the form (${inputs}, ${state}, ${does_loop_start_here})
        looping_path = [(model.pick_one_inputs(s), s, False)] 
        current = s
        for i in range(k-1,-1,-1):
            predecessor = (model.pre(current)).intersection(frontiers[i])
            current = model.pick_one_state(predecessor)
            looping_path.insert(0, (model.pick_one_inputs(current), current, False))
        # since it is a looping path, `s` must appear at the beginning and in the end
        looping_path.insert(0, (model.pick_one_inputs(s), s, True))
        # endregion

        # region COMPUTE_LEADING_PATH
        reach = model.init
        new = model.init
        leading_path = []

        while not s.entailed(new):
            leading_path.append((model.pick_one_inputs(new), model.pick_one_state(new), False))
            new = (model.post(new)).diff(reach)
            reach = reach.union(new)
        # endregion

        # region PASTE_LEADING_AND_LOOPING_PATH
        leading_path = list(map(
            lambda triple: 
                (   triple[0].get_str_values(), # get inputs as a dictionary
                    triple[1].get_str_values(), # get state variables as a dictionary
                    triple[2]    ), leading_path))
        
        looping_path = list(map(
            lambda triple: 
                (   triple[0].get_str_values(), # get inputs as a dictionary
                    triple[1].get_str_values(), # get state variables as a dictionary
                    triple[2]    ), looping_path))
    
        return leading_path + looping_path
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
            success("...property is respected!")
        else:
            error("...property is not respected, as demonstrated by the following counterexample:")
            i = 1
            for triple in res[1]:
                if triple[2]:
                    comment("Loop starts here")
                comment("-> State: %d <-" % i)
                # region PRINT_INPUTS
                for key, value in triple[0].items() :
                    print("%s = %s" % (key, value))
                # endregion
                # region PRINT_STATE_VARIABLES
                for key, value in triple[1].items() :
                    print("%s = %s" % (key, value))
                # endregion
                i = i + 1
            error("Property checking stopped at the following conjunct:")
            error("G (F %s) -> G (F %s)" % (res[2][0], res[2][1]))
            error("This has happened since:")
            error("1. %s is repeatable" % res[2][0])
            error("2. the negation of %s is persistent" % res[2][1])

    pynusmv.init.deinit_nusmv()
