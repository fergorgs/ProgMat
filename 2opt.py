from py2opt.routefinder import RouteFinder
import matplotlib.pyplot as plt
import numpy as np
import sys
from sys import stdout as out
import os

def get_distance_matrix(coords):
    matrix = []
    
    for x in coords:
        dists = []
    
        for y in coords:
            dists.append(np.linalg.norm(np.array(x)  - np.array(y)))
    
        matrix.append(dists)
    
    return matrix




def two_opt(dist_mat, cities_names):
    route_finder = RouteFinder(dist_mat, cities_names, iterations=5)
    best_distance, best_route = route_finder.solve()

    with open('hint.txt', 'w') as f:
        lines = []
        for adj in make_adjacent_matrix(best_route):
            for x in adj:
                lines.append(str(x)+'\n')
        f.writelines(lines)
    return best_route


def make_adjacent_matrix(best_route):
    lastIndex = -1
    cityIndex = -1
    n = len(best_route)
    matriz = np.zeros((n,n), dtype=np.float64)
    for i in range(n):
        cityName = best_route[i]
        cityIndex = int(cityName.split(' ')[1]) - 1
    
        if i != 0:
            # fazer adjacencia
            matriz[lastIndex][cityIndex] = 1

        lastIndex = cityIndex

    matriz[int(best_route[-1].split()[1])-1][0] = 1
    return matriz

def read_file():
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

            # calcula 2opt
            brt = two_opt(get_distance_matrix(coords), places)

            polygon = []
            for x in brt:

                polygon.append(coords[int(x.split()[1])-1])
            
            polygon.append(coords[0])
                
            xs, ys = zip(*polygon) #create lists of x and y values

            plt.figure()
            plt.scatter(*zip(*polygon), linewidths=0.00001)
            plt.plot(xs,ys) 
            plt.show() # if you need...





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
                    solve(get_distance_matrix(coords), places, sys.argv[1])

                except Exception as e:

                    print('ERROR: Failed to solve problem from file \'' + file + '\'')
                    print(e)
        else:
            print('ERROR: Specified path is nither a file or a directory')
    else:
        # resolve o toy problem
        two_opt([[0, 29, 15, 35], [29, 0, 57, 42], [15, 57, 0, 61], [35, 42, 61, 0]], ['A', 'B', 'C', 'D'])


read_file()