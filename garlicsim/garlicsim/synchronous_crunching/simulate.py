# Copyright 2009-2010 Ram Rachum.
# This program is distributed under the LGPL2.1 license.

'''
This module defines the `simulate` function.

See its documentation for more info.
'''

import copy
import warnings

from garlicsim.general_misc import cute_iter_tools

import garlicsim
import garlicsim.misc
import history_browser as history_browser_module # Avoiding name clash

__all__ = ["simulate"]


def simulate(state, iterations=1, *args, **kwargs):
    '''
    Simulate from the given state for the given number of iterations.

    If you wish, in `*args` and `**kwargs` you may specify simulation parameters
    and/or a specific step function to use. (You may specify a step function
    either as the first positional argument or the `step_function` keyword
    argument.) You may also pass in an existing step profile as first argument.
    
    Returns the final state of the simulation.
    '''
    simpack_grokker = garlicsim.misc.SimpackGrokker.create_from_state(state)
    
    parse_arguments_to_step_profile = garlicsim.misc.StepProfile.build_parser(
        simpack_grokker.default_step_function
    )
    step_profile = parse_arguments_to_step_profile(*args, **kwargs)

    if not hasattr(state, 'clock'):
        state = copy.deepcopy(
            state,
            garlicsim.general_misc.persistent.DontCopyPersistent()
        )
        state.clock = 0
    
    if simpack_grokker.history_dependent:
        return __history_simulate(simpack_grokker, state, iterations,
                                  step_profile)
    else: # It's a non-history-dependent simpack
        return __non_history_simulate(simpack_grokker, state, iterations,
                                      step_profile)

    
def __history_simulate(simpack_grokker, state, iterations=1, step_profile=None):
    '''    
    Simulate from the given state for the given number of iterations.
    
    (Internal function, for history-dependent simulations only)

    A simpack grokker must be passed as the first parameter. A step profile may
    be passed to be used with the step function.
    
    Returns the final state of the simulation.
    '''
    if step_profile is None:
            step_profile = garlicsim.misc.StepProfile(
                simpack_grokker.default_step_function
            )
            
    tree = garlicsim.data_structures.Tree()
    root = tree.add_state(state, parent=None)
    path = root.make_containing_path()
    history_browser = history_browser_module.HistoryBrowser(path)
    
    iterator = simpack_grokker.get_step_iterator(history_browser, step_profile)
    finite_iterator = cute_iter_tools.shorten(iterator, iterations)
    
    current_node = root
    current_state = current_node.state
    
    try:
        for current_state in finite_iterator:
            current_node = tree.add_state(current_state, parent=current_node)
    except garlicsim.misc.WorldEnded:
        pass
        
    final_state = current_state
    # Which is still here as the last value from the for loop
    
    return final_state


def __non_history_simulate(simpack_grokker, state, iterations=1,
                           step_profile=None):
    '''
    Simulate from the given state for the given number of iterations.
    
    (Internal function, for non-history-dependent simulations only.)

    A simpack grokker must be passed as the first parameter. A step profile may
    be passed to be used with the step function.
    
    Returns the final state of the simulation.
    '''
    if step_profile is None:
            step_profile = garlicsim.misc.StepProfile(
                simpack_grokker.default_step_function
            )
            
    iterator = simpack_grokker.get_step_iterator(state, step_profile)
    finite_iterator = cute_iter_tools.shorten(iterator, iterations)
    current_state = state
    
    try:
        for current_state in finite_iterator:
            pass
    except garlicsim.misc.WorldEnded:
        pass    
    
    final_state = current_state
    # Which is still here as the last value from the for loop
    
    return final_state