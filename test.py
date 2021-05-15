from sko.GA import GA
from compute import *

lb = [3.14e-5, 2.36e-5, 3.85e-4, 7.07e-5, 3.85e-4]
ub = [2.83e-4, 2.12e-4, 6.36e-4, 1.96e-4, 6.36e-4]


ga = GA(func=compute, n_dim=5, lb=lb, ub=ub, max_iter=5)
best_x, best_y = ga.fit()