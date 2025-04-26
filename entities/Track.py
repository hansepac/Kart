from numpy import array
import numpy as np


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


# for checking the twisting stuff
import numpy as np

def orientation(a, b, c):
    val = (b[2] - a[2]) * (c[0] - b[0]) - (b[0] - a[0]) * (c[2] - b[2])
    if np.isclose(val, 0):
        return 0  # colinear
    return 1 if val > 0 else 2  # 1 = clockwise, 2 = counterclockwise

def on_segment(a, b, c):
    """Check if point c lies on segment ab"""
    return (min(a[0], b[0]) <= c[0] <= max(a[0], b[0]) and
            min(a[1], b[1]) <= c[1] <= max(a[1], b[1]))

def segments_intersect(p1, p2, q1, q2):
    o1 = orientation(p1, p2, q1)
    o2 = orientation(p1, p2, q2)
    o3 = orientation(q1, q2, p1)
    o4 = orientation(q1, q2, p2)

    # General case
    if o1 != o2 and o3 != o4:
        return True

    # Special cases (colinear points)
    if o1 == 0 and on_segment(p1, p2, q1): return True
    if o2 == 0 and on_segment(p1, p2, q2): return True
    if o3 == 0 and on_segment(q1, q2, p1): return True
    if o4 == 0 and on_segment(q1, q2, p2): return True

    return False


class Track:
    # some static options
    TRACK_TYPE_FLAT = 0
    TRACK_TYPE_MOUNTAIN = 1
    TRACK_TYPE_IRREGULARG = 2


    def __init__(self, trackorigin = array([0,0,0]), trackradius = 20, nodes=7, trackwidth=0.4, tracktype=TRACK_TYPE_FLAT):
        
        self.trackradius = trackradius
        self.trackwidth = trackwidth
        self.tracktype = tracktype
        self.trackorigin = trackorigin


        # here is where we generate the track
        # np.random.seed(45)
        # seed 45 was a good one with 10 nodes. and track radius 7 and trackwidth 0.2
        np.random.seed(50)

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

        # # Step 3: Sort points in rough circle order (optional, helps smoothness)
        # angles = np.arctan2(points[:,1], points[:,0])
        # order = np.argsort(angles)
        # points = points[order]

        # Step 4: Close the loop
        loop = list(points) + [points[0]]

        # Step 5: Smooth the loop
        loop = smooth_loop(loop, iterations=10, alpha=0.2)

        # # rescale loop so it has the right radius
        # avg_radius = np.mean([np.linalg.norm(p - trackorigin) for p in loop[:-1]])
        # scale_factor = trackradius / avg_radius
        # loop = [(p - trackorigin) * scale_factor + trackorigin for p in loop]
        

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
        last_track_verts = None
        for i in range(nodes):
            # first get the unit vectors of the edges
            e1 = (points[i - 1] - points[i])/np.linalg.norm(points[i - 1] - points[i])
            e2 = (loop[i] - loop[i + 1])/np.linalg.norm(loop[i] - loop[i + 1] )
            # now find the middle vector 
            emid = e1 - e2 

            # rotate emid so that it's perpendicular to the surface normals 
            emid = emid - (emid @ self.surface_normals[i])# /(np.linalg.norm(self.surface_normals[i]))
            emid = emid / np.linalg.norm(emid) # renormalize

            bend_angle = np.arccos(e1 @ e2)

            # now make the track vertices
            bend_account = abs(bend_angle)/20*emid
            track_vertices = [
                (loop[i] - emid*trackwidth/2 - bend_account), loop[i], (loop[i] + emid*trackwidth/2 + bend_account)
            ]

            # just minimizing distance doesn't work
            # just checking dot product between this one and the last doesnt work
            # just making unit vector positive doesn't work

            # the unit vector always points on the inside of the curve 
            if last_track_verts is not None:
                if segments_intersect(track_vertices[0], last_track_verts[0], track_vertices[1], last_track_verts[1]):
                    track_vertices[0], track_vertices[2] = track_vertices[2], track_vertices[0]
            last_track_verts = track_vertices

            # if last_track_verts is not None:
            #     current_ef = np.linalg.norm(track_vertices[0] - last_track_verts[0]) + np.linalg.norm(track_vertices[2] - last_track_verts[2])
            #     possible_alternative = np.linalg.norm(track_vertices[2] - last_track_verts[0]) + np.linalg.norm(track_vertices[0] - last_track_verts[2])
            #     if possible_alternative < current_ef:
            #         track_vertices[0], track_vertices[2] = track_vertices[2], track_vertices[0]

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
        self.track_rect_homocoords = []
        loop_verts = self.track_verts + [self.track_verts[-1]]
        for i in range(-1, nodes):
            self.track_edge_homocoords.append([array([*loop_verts[i][0], 1]), array([*loop_verts[i + 1][0], 1])])
            self.track_edge_homocoords.append([array([*loop_verts[i][2], 1]), array([*loop_verts[i + 1][2], 1])])

            self.track_rect_homocoords.append([array([*loop_verts[i][0], 1]), array([*loop_verts[i + 1][0], 1]), array([*loop_verts[i + 1][2], 1]), array([*loop_verts[i][2], 1])])



    def get_ground_height(self, location):
        min_distance = float('inf')
        closest_projection = None
        for p1, p2 in self.edges:
            line_vec = p2 - p1
            line_unitvec = line_vec / np.linalg.norm(line_vec)
            point_vec = location - p1
            projection_length = np.dot(point_vec, line_unitvec)
            projection = p1 + projection_length * line_unitvec
            distance = np.linalg.norm(location - projection)
            if distance < min_distance:
                min_distance = distance
                closest_projection = projection
        
        if closest_projection is None:
            return None
        
        return closest_projection[1]
    
    def is_on_track(self, location):
        min_distance = float('inf')
        closest_projection = None
        for p1, p2 in self.edges:
            line_vec = p2 - p1
            line_unitvec = line_vec / np.linalg.norm(line_vec)
            point_vec = location - p1
            projection_length = np.dot(point_vec, line_unitvec)
            projection = p1 + projection_length * line_unitvec
            distance = np.linalg.norm(location - projection)
            if distance < min_distance:
                min_distance = distance
                closest_edge = (p1, p2)
                closest_projection = projection
        
        if closest_projection is None:
            return False
        
        return np.linalg.norm(location - closest_projection) < self.trackwidth




