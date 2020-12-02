import sys
from sys import stdout as out
import os
from mip import Model, xsum, minimize, BINARY
import numpy as np
from itertools import chain, combinations, product

# powerset
# generates all the sub-sets possible given a certain range of numbers
# def powerset(iterable):
#    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
#    s = list(iterable)
#    return chain.from_iterable(combinations(s, r) for r in range(2, len(s)-1))

# get_distance_matrix
# given a list of tuples, returns a matrix with the euclidian distance between those tuples
def get_distance_matrix(coords):
    matrix = []
    
    for x in coords:
        dists = []
    
        for y in coords:
            dists.append(np.linalg.norm(np.array(x)  - np.array(y)))
    
        matrix.append(dists)
    
    return matrix


# solve
# builds and solves a model, given the problem
# receives: a list of coordenates; a list of names of the places
def solve(coords, places, problem_name):
    
    #path = os.path.join('./output', problem_name)
    #if(os.path.isfile(path + '.lp')):
    #    model.read(path + '.lp')    
    #else:
    # print(len(coords))
    # número de nós e lista de vértices
    n, V = len(coords), set(range(len(coords)))
    
    # matriz de distâncias completa
    c = get_distance_matrix(coords)

    # print(c)
    # modelo
    model = Model()

    # variáveis binárias indicando se arco (i,j) é usado na rota
    x = [[model.add_var(var_type=BINARY) for j in V] for i in V]

    # variáveis contínuas para prevencção de sub-rotas: cada cidade terá
    # um identificador numérico maior na rota, excetuando-se a primeira
    y = [model.add_var() for i in V]
    # funcção objetivo: minimizar custo total
    model.objective = minimize(xsum(c[i][j]*x[i][j] for i in V for j in V))

    # restrição : sair de cada cidade somente uma vez
    for i in V:
        model += xsum(x[i][j] for j in V - {i}) == 1

    # restrição : entrar em cada cidade somente uma vez
    for i in V:
        model += xsum(x[j][i] for j in V - {i}) == 1

    # eliminação de sub-rotas
    # for s in powerset(range(len(coords))):
    #     model += xsum(x[i][j] for i in s for j in V - set(s)) >= 1

    # eliminação de sub-rotas
    for (i, j) in product(V - {0}, V - {0}):
        if i != j:
            model += y[i] - (n+1)*x[i][j] >= y[j]-n

    model.verbose = 1

    # otimização com limite de tempo de 30 segundos
    print(model.optimize(max_seconds=600, relax=False))
    
    # verificando se ao menos uma solução válida foi encontrada
    if model.num_solutions > 0:
        print('route with total distance %g found: %s'
            % (model.objective_value, places[0]))
        nc = 0
        while True:
            for i in V:
                if x[nc][i].x >= 1:
                    nc = i
                    break
                
            print(' -> %s' % places[nc])
            if nc == 0:
                break
        print('\n')
        model.write('solution.sol')
        #model.write(path + '.lp')
    else:
        print('no feasible solution found, upper bound is: {}'.format(model.objective_bound))




# MAIN CODE-----------------------------------------

# toy problem places
places = ['Gusty Garden Galaxy', 'Freezeflame Galaxy', 'Dusty Dune Galaxy', 'Honeyclimb Galaxy', 'Bigmouth Galaxy']

# toy problem coordenates
coords = [(3, 2), (4, 4), (10, 6), (12, 4), (14, 8)]

if(len(sys.argv) == 2):

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

    elif(os.path.isdir(sys.argv[1])):

        for file in os.listdir(sys.argv[1]):
            
            try:
                coords = []
                places = []
                # lê as coordenadas do arquivo de entrada
                with open(os.path.join(sys.argv[1], file), 'r') as f:

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
                solve(coords, places, sys.argv[1])

            except Exception as e:

                print('ERROR: Failed to solve problem from file \'' + file + '\'')
                print(e)


    else:
        print('ERROR: Specified path is nither a file or a directory')

else:
    # resolve o toy problem
    solve(coords, places, 'Toy Problem')