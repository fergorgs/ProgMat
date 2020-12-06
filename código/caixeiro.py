from __future__ import print_function
from ortools.linear_solver import pywraplp
from itertools import chain, combinations, product
import matplotlib.pyplot as plt
import numpy as np
import sys
from sys import stdout as out
import os

def get_hint_from_file(file_path, num_of_ys):

    vals = []
    with open(file_path, 'r') as f:
        lines = f.readlines()

    for val in lines:
        try:
            vals.append(float(val))
        except:
            continue

    # print(vals)

    # for x in range(0, num_of_ys):
    #     vals.append(x)
        
    return vals


def get_distance_matrix(coords):
    matrix = []
    
    for x in coords:
        dists = []
    
        for y in coords:
            dists.append(np.linalg.norm(np.array(x)  - np.array(y)))
    
        matrix.append(dists)
    
    return matrix


def solve(coords, places, problem_name):

    n, V = len(coords), set(range(len(coords)))
        
    # matriz de distâncias completa
    c = get_distance_matrix(coords)

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # SET VARIABLES-----------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    infinity = solver.infinity()
    x = [[solver.BoolVar('x' + str(i) + str(j)) for j in V] for i in V]
    y = [solver.IntVar(0.0, infinity, 'y') for i in V]

    print('Number of variables =', solver.NumVariables())

    # SET CONSTRAINS-----------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    for i in V:
        solver.Add(sum(x[i][j] for j in V - {i}) == 1)
    for i in V:
        solver.Add(sum(x[j][i] for j in V - {i}) == 1)
    for (i, j) in product(V - {0}, V - {0}):
        if i != j:
            solver.Add(y[i] - (n+1)*x[i][j] >= y[j]-n)

    # DEFINE OBJECTIVE-----------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    solver.Minimize(sum(c[i][j]*x[i][j] for i in V for j in V))

    # SOLVE-----------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    solver.SetTimeLimit(10*60000)
    solver.EnableOutput()

    # gets hint from file
    if(len(sys.argv) == 3):

        file_path = sys.argv[2]
        hint = get_hint_from_file(file_path, len(V))

        solver.SetHint(solver.variables()[:-len(V)], hint)

    try:
        status = solver.Solve()
    except KeyboardInterrupt:
        print('Trying to finish the solving process')
        solver.InterruptSolve()

    # DISPLAY SOLUTION-----------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------
    print('Objective value =', solver.Objective().Value())
    print('Nodes = ' + str(solver.nodes()))

    nc = 0
    polygon = []
    while True:
        for i in V:
            if x[nc][i].solution_value() >= 1:
                nc = i
                break
            
        print(' -> ' + str(coords[nc]))
        polygon.append([coords[nc][0], coords[nc][1]])
        if nc == 0:
            break

    polygon.append(polygon[0]) #repeat the first point to create a 'closed loop'

    xs, ys = zip(*polygon) #create lists of x and y values

    plt.figure()
    plt.scatter(*zip(*polygon), linewidths=0.00001)
    plt.plot(xs,ys) 
    plt.show() # if you need...

    print('------------------------------------------------\n')









# MAIN CODE-----------------------------------------

# toy problem places
places = ['Gusty Garden Galaxy', 'Freezeflame Galaxy', 'Dusty Dune Galaxy', 'Honeyclimb Galaxy', 'Bigmouth Galaxy']

# toy problem coordenates
coords = [(3, 2), (4, 4), (10, 6), (7, 4), (14, 8)]

if(len(sys.argv) > 1):

    if(os.path.isfile(sys.argv[1])):
        coords = []
        places = []
        # lê as coordenadas do arquivo de entrada
        with open(sys.argv[1], 'r') as f:

            lines = f.readlines()

            if('EOF' in lines[-1]):
                lines = lines[:len(lines)-1]

            crit_zone = False
            for line in lines:
                if(not crit_zone and 'NODE_COORD_SECTION' in line):
                    crit_zone = True
                elif(crit_zone):
                    coords.append((float(line.split()[1]), float(line.split()[2])))

            for x in range(1, len(coords)+1):
                places.append('City ' + str(x))

        # resolve o problema
        solve(coords, places, sys.argv[1][8:])

    else:
        print('ERROR: Specified path is not a file')

else:
    # resolve o toy problem
    solve(coords, places, 'Toy Problem')
