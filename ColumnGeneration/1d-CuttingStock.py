from gurobipy import *

demands = [5,10,20,18,11] # Amount of demand to be produced for each specific width

width = [1, 2, 3, 4, 5] # The list of widths that are demanded

W = 10 # The width of the stock material that will be cut into different dimensions

A = [[1,0,0,0,0], [0,1,0,0,0], [0,0,1,0,0], [0,0,0,1,0], [0,0,0,0,1],[2,0,0,0,0]] # Initial matrix that consists of initial cutting patterns. Note that each list in A corresponds to a column in the A matrix, and although there are limited number of patterns at the beginning for this small instance, there will be other columns (patterns) to be added throughout the solution.


def MasterProblem():  # Master problem that is solved for finding optimal patterns among the given set of patterns. Dual variables from this problem will be used in the column generation (subproblem).
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


def SubProblem(shadow_prices): # Subproblem is solved for getting a pattern (column) that improves the result of the master problem given the shadow prices from the master problem.
    sub = Model("SubProblem") # Subproblem is basically a knapsack problem and it is not hard to solve optimally for such small instances. Otherwise, it could be approximated by some other algorithms
    y = sub.addVars([j for j in range(len(demands))],vtype=GRB.INTEGER, lb=0, ub=GRB.INFINITY, name="X")

    # objective function
    S = 1-quicksum(shadow_prices[j]*y[j] for j in range(len(demands)))  # Since the objective of the master problem is to minimize the number of stock that are cut, it can be only improved by adding columns (patterns) to the master problem that leads to utilization of less stocks. For this reason, the reduced cost of the variable that will be introduced to the master problem must be less than 0. Thus, the subproblem tries to minimize the reduced cost. Otherwise, we know that the master problem is already optimal.
    
    sub.setObjective(S, GRB.MINIMIZE)

    # Length constraint

    sub.addConstr((quicksum(width[j]*y[j] for j in range(len(demands)))<=W), "Length Constraint") # We need to create patterns such that the width of the stock material is not exceeded.
    sub.optimize()
    return sub.objVal, sub.getAttr("X") # Here we obtain the sequence of variables y_j which correspond to a cutting pattern to be used in the master problem.


sub_obj = -1

while sub_obj < 0: # We solve each of the problems consecutively untill we can not find a pattern that yields a better solution for the master problem.
    pi = MasterProblem()
    sub_obj, new_pattern = SubProblem(pi)
    A.append(new_pattern) # It could be the case that the non-basic patterns were removed from the matrix A for the sake of efficiency. But, this approach might have some drawbacks as well. Anyway, for such a small problem, it is not a big deal to cope with the matrix A in this way.

######### Final solution ############

master = Model("MasterProblem")  # Observe that the previous master problem is the linear relexation of the original problem. This is the original problem (although it is called master problem here) with integrality constraint on the decision variables. We use the matrix A obtained previously by adding columns, for the solution of the original problem.

x = master.addVars([i for i in range(len(A))], vtype=GRB.INTEGER, lb=0, ub=GRB.INFINITY, name="X") # variable type= GRB. INTEGER --> this is the integrality constraint on the decision variables

# objective function
Z = quicksum(x[i] for i in range(len(A)))

master.setObjective(Z, GRB.MINIMIZE)

# Demand satisfaction constraint
master.addConstrs((quicksum(x[i] * A[i][j] for i in range(len(A))) >= demands[j] for j in range(len(demands))),
                 "Demand Satisfaction")

master.optimize()
master.printAttr("X")

variables = master.getAttr("X") # Finally we are printing the cutting patterns that are included in the optimal solution.
for i in range(len(variables)):
    if variables[i] != 0:
        print(A[i])
