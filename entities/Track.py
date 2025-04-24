from numpy import array, arccos, exp
from numpy.linalg import norm
import numpy.random as rand
from random import shuffle, randrange, random


def weightFunction(cycle):
    # this function is used to determine the "better" way to connect the lines
    # see Traveling Salesman Problem
    
    
    # the first thing we want to minimize is sharp angles 
    # we want to maximize this angle_score
    angle_score = 0
    for i in range(1, len(cycle) - 1):
        vec1 = cycle[i - 1] - cycle[i]
        vec2 = cycle[i + 1] - cycle[i]

        # get magnitudes
        vec1mag = (vec1[0]**2 + vec1[1]**2)**0.5
        vec2mag = (vec2[0]**2 + vec2[1]**2)**0.5

        # now find the angle
        angle_score += arccos((vec1 @ vec2)/vec1mag/vec2mag)


    # add a distance component 
    distance_score = 0
    for i in range(len(cycle) - 1):
        distance_score += norm(cycle[i + 1] - cycle[i])
        
        
    return 1/angle_score + distance_score # derivative reversed for minimization
 
        


class Track:
    # some static options
    TRACK_TYPE_FLAT = 0
    TRACK_TYPE_MOUNTAIN = 1
    TRACK_TYPE_IRREGULARG = 2


    def __init__(self, trackorigin = array([0,0,0]), trackradius = 10, nodes=8, tracktype=TRACK_TYPE_FLAT):
        # here is where we generate the track
        
        # first generate the points
        newpoints = []

        for _ in range(nodes):
            newpoint = rand.uniform(-trackradius, trackradius, 3) + trackorigin
            if tracktype == Track.TRACK_TYPE_FLAT:
                newpoint[1] = 0
            newpoints.append(newpoint)

        self.nodes = newpoints

        # now make lines
        shuffled = self.nodes[:]
        shuffle(shuffled) 

        cycle = shuffled + [shuffled[0]]

        # use simulated annealing to improve the cycle
        Tmax, Tmin = 10.0, 0.0001
        tau = 1e4
        t = 0
        T = Tmax 
        D = weightFunction(cycle)
        while T > Tmin:
            t += 1
            T = Tmax*exp(-t/tau)

            # choose two points and swap them
            i,j = randrange(1,nodes), randrange(1, nodes)
            while i == j:
                # get two different numbers
                i,j = randrange(1,nodes), randrange(1, nodes)

            # swap them and calculate the change in weightFunction
            oldD = D
            cycle[i], cycle[j] = cycle[j], cycle[i]
            D = weightFunction(cycle)
            deltaD = D - oldD

            # now use stat-mech model to see if we keep it
            if random() >= exp(-deltaD/T): 
                cycle[i], cycle[j] = cycle[j], cycle[i] # swap back
                D = oldD



        # now pack cycle as a set of edges
        edges = []
        for i in range(nodes):
            newedge = [cycle[i], cycle[i+1]]
            edges.append(newedge)

        self.edges = edges

    def get_edge_homocoords(self):
        # returns homogeneous coordinates for the track edges
        homocoords = []
        for edge in self.edges:
            homocoords.append([array([*edge[0], 1]), array([*edge[1], 1])])
        return homocoords


        



