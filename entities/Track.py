from numpy import array, arccos, exp
import numpy as np
from numpy.linalg import norm
import numpy.random as rand
from random import shuffle, randrange, random


def angle_between(a, b, c):
    ab = b - a
    bc = c - b
    cos_angle = np.dot(ab, bc) / (np.linalg.norm(ab) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
    return np.degrees(angle)

def smooth_loop(loop, iterations=10, alpha=0.3):
    for _ in range(iterations):
        new_loop = []
        n = len(loop) - 1  # skip duplicated last point
        for i in range(n):
            prev = loop[i - 1]
            curr = loop[i]
            next = loop[(i + 1) % n]
            smoothed = (prev + next) / 2
            curr = curr * (1 - alpha) + smoothed * alpha
            new_loop.append(curr)
        new_loop.append(new_loop[0])  # close the loop
        loop = new_loop
    return loop


class Track:
    # some static options
    TRACK_TYPE_FLAT = 0
    TRACK_TYPE_MOUNTAIN = 1
    TRACK_TYPE_IRREGULARG = 2


    def __init__(self, trackorigin = array([0,0,0]), trackradius = 7, nodes=8, trackwidth=0.2, tracktype=TRACK_TYPE_FLAT):
        # here is where we generate the track

        # NEW METHOD
        # Step 1: Generate points roughly on a circle
        theta = np.linspace(0, 2 * np.pi, nodes, endpoint=False)
        radii = (1 + 0.3 * np.random.randn(nodes))*trackradius
        y_vals = np.random.randn(nodes) * trackradius/30
        points = np.stack([
            radii * np.cos(theta),
            y_vals,  # 3rd dimension, all zeros
            radii * np.sin(theta)
        ], axis=1)
        points = points + trackorigin

        # Step 2: (Optional) Shuffle a little
        np.random.shuffle(points)

        # Step 3: Sort points in rough circle order (optional, helps smoothness)
        # angles = np.arctan2(points[:,1], points[:,0])
        # order = np.argsort(angles)
        # points = points[order]

        # Step 4: Close the loop
        loop = list(points) + [points[0]]

        # Step 5: Smooth the loop
        loop = smooth_loop(loop, iterations=10, alpha=0.2)

        self.nodes = loop[:-1]

        # now pack cycle as a set of edges
        edges = []
        for i in range(nodes):
            newedge = [loop[i], loop[i+1]]
            edges.append(newedge)

        self.edges = edges


        # generate gravity vectors 
        self.g_vecs = np.tile(np.array([0, 1, 0]), (nodes, 1))
        # generate surface normal vectors 
        self.surface_normals = self.g_vecs # for now have them be the same. 

        # make track width vertices
        track_verts = []
        points = loop[:-1]
        for i in range(nodes):
            # first get the unit vectors of the edges
            e1 = (points[i - 1] - points[i])/np.linalg.norm(points[i - 1] - points[i])
            e2 = (loop[i + 1] - loop[i])/np.linalg.norm(loop[i + 1] - loop[i])
            # now find the middle vector 
            emid = e1 + e2 

            # rotate emid so that it's perpendicular to the surface normals 
            emid = emid - emid @ self.surface_normals[i]
            emid = emid / np.linalg.norm(emid) # renormalize

            # now make the track vertices
            track_vertices = [
                (loop[i] - emid*trackwidth/2), loop[i], (loop[i] + emid*trackwidth/2)
            ]

            track_verts.append(track_vertices)
        self.track_verts = track_verts


        ## GENERATE HOMOCOORDS
        self.node_homocoords = []
        for node in self.nodes:
            self.node_homocoords.append(array([*node, 1]))

        self.edge_homocoords = []
        for edge in self.edges:
            self.edge_homocoords.append([array([*edge[0], 1]), array([*edge[1], 1])])
        
        self.track_verts_homocoords = []
        for track_vert in self.track_verts:
            self.track_verts_homocoords.append(array([*(track_vert[0]), 1]))
            self.track_verts_homocoords.append(array([*(track_vert[1]), 1]))
            self.track_verts_homocoords.append(array([*(track_vert[2]), 1]))

        self.track_edge_homocoords = []
        loop_verts = self.track_verts + [self.track_verts[-1]]
        for i in range(-1, nodes):
            self.track_edge_homocoords.append([array([*loop_verts[i][0], 1]), array([*loop_verts[i + 1][0], 1])])
            self.track_edge_homocoords.append([array([*loop_verts[i][2], 1]), array([*loop_verts[i + 1][2], 1])])


        



