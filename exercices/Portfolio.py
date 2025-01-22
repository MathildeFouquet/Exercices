import json
import pandas as pd
import numpy as np
import gurobipy as gp
from gurobipy import GRB

with open("../data/portfolio-example.json", "r") as f:
    data = json.load(f)

n = data["num_assets"]
sigma = np.array(data["covariance"])
mu = np.array(data["expected_return"])
mu_0 = data["target_return"]
k = data["portfolio_max_size"]


with gp.Model("portfolio") as model:
    # Variable de décision
    x = model.addVars(n, lb = 0, ub = 1, name = "x")
    y = model.addVars(n, lb = 0, vtype=GRB.BINARY, name = "y")

    # Objectif

    # Contraintes

    model.optimize()

    # Write the solution into a DataFrame
    portfolio = [var.X for var in model.getVars() if "x" in var.VarName]
    risk = model.ObjVal
    expected_return = model.getRow(model.getConstrByName("return")).getValue()
    df = pd.DataFrame(
        data=portfolio + [risk, expected_return],
        index=[f"asset_{i}" for i in range(n)] + ["risk", "return"],
        columns=["Portfolio"],
    )
    print(df)