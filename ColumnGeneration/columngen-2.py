from gurobipy import *

demands = [5,10,20,18,11]

width = [1, 2, 3, 4, 5]

W = 10

A = [[1,0,0,0,0], [0,1,0,0,0], [0,0,1,0,0], [0,0,0,1,0], [0,0,0,0,1],[2,0,0,0,0]]


def MasterProblem():
    master = Model("MasterProblem")

    x = master.addVars([i for i in range(len(A))], vtype=GRB.CONTINUOUS, lb=0, ub=GRB.INFINITY, name="X")

    # objective function
    Z = quicksum(x[i] for i in range(len(A)))

    master.setObjective(Z, GRB.MINIMIZE)

    # Demand satisfaction constraint
    master.addConstrs((quicksum(x[i] * A[i][j] for i in range(len(A))) >= demands[j] for j in range(len(demands))),
                     "Demand Satisfaction")

    master.optimize()
    return master.getAttr("Pi")


def SubProblem(shadow_prices):
    sub = Model("SubProblem")
    y = sub.addVars([j for j in range(len(demands))],vtype=GRB.INTEGER, lb=0, ub=GRB.INFINITY, name="X")

    # objective function
    S = 1-quicksum(shadow_prices[j]*y[j] for j in range(len(demands)))
    sub.setObjective(S, GRB.MINIMIZE)

    # Length constraint

    sub.addConstr((quicksum(width[j]*y[j] for j in range(len(demands)))<=W), "Length Constraint")
    sub.optimize()
    return sub.objVal, sub.getAttr("X")


sub_obj = -1

while sub_obj < 0:
    pi = MasterProblem()
    sub_obj, new_pattern = SubProblem(pi)
    A.append(new_pattern)



######### Final solution ############

master = Model("MasterProblem")

x = master.addVars([i for i in range(len(A))], vtype=GRB.INTEGER, lb=0, ub=GRB.INFINITY, name="X")

# objective function
Z = quicksum(x[i] for i in range(len(A)))

master.setObjective(Z, GRB.MINIMIZE)

# Demand satisfaction constraint
master.addConstrs((quicksum(x[i] * A[i][j] for i in range(len(A))) >= demands[j] for j in range(len(demands))),
                 "Demand Satisfaction")

master.optimize()
master.printAttr("X")

variables = master.getAttr("X")
for i in range(len(variables)):
    if variables[i] != 0:
        print(A[i])
