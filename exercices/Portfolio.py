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
    # Decision variables
    x = model.addVars(n, vtype=GRB.CONTINUOUS, name="x")
    y = model.addVars(n, vtype=GRB.BINARY, name="y")

    # Objective function
    model.setObjective(gp.quicksum(sigma[i,j] * x[i] * x[j] for i in range(n) for j in range(n)), sense=GRB.MINIMIZE)

    # Constraints
    model.addConstr(gp.quicksum(x[i] * mu[i] for i in range (n)) >= mu_0 , name = "return")
    model.addConstr(gp.quicksum(y[i] for i in range (n)) <= k, name = "number_of_invest_assets")
    model.addConstr(gp.quicksum(x[i] for i in range (n)) == 1, name = "sum_equals_1")

    for i in range (n):
        model.addConstr(x[i] <= y[i], name = "coupling")



    # Optimize the model
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