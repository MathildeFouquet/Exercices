from functools import partial

import gurobipy as gp
from gurobipy import GRB


class CallbackData:
    def __init__(self):
        self.last_gap_change_time = -GRB.INFINITY
        self.last_gap = GRB.INFINITY


def callback(model, where, *, cbdata):
    if where != GRB.Callback.MIP:
        return
    if model.cbGet(GRB.Callback.MIP_SOLCNT) == 0:
        return

    best = model.cbGet(GRB.Callback.MIP_OBJBST)
    bound = model.cbGet(GRB.Callback.MIP_OBJBND)
    gap = abs((bound - best) / best)
    time = model.cbGet(GRB.Callback.RUNTIME)
    if gap < cbdata.last_gap - epsilon_to_compare_gap:
        # The gap has decreased, store new gap and reset the time
        cbdata.last_gap = gap
        cbdata.last_gap_change_time = time
        print(f"Storing new gap: {gap}, {time}")
        return
    print(time - cbdata.last_gap_change_time)
    if time - cbdata.last_gap_change_time > max_time_between_gap_updates:
        # No change since too long
        print("It's been too long...")
        model.terminate()


with gp.read("../data/mkp.mps.bz2") as model:
    # Global variables used in the callback function
    max_time_between_gap_updates = 15
    epsilon_to_compare_gap = 1e-4

    # Initialize data passed to the callback function
    callback_data = CallbackData()
    callback_func = partial(callback, cbdata=callback_data)

    model.optimize(callback_func)