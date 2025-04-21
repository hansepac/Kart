import pygame
import numpy as np
import math
import sys

# ---------- Setup Pygame and Window ----------
WIDTH, HEIGHT = 800, 600
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple 3D Engine with OBJ Support")
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# ---------- Camera Setup ----------
camera_pos = np.array([0.0, 0.0, -5.0])   # Camera position in world space
camera_rot = np.array([0.0, 0.0])           # [pitch, yaw] in radians
move_speed = 0.1
mouse_sensitivity = 0.003

# ---------- Projection Function ----------
def project(point):
    """Basic perspective projection.
       Assumes point is in camera (view) coordinates."""
    if point[2] == 0:
        point[2] = 0.001  # Avoid division by zero
    factor = 200 / point[2]
    x = point[0] * factor + WIDTH / 2
    y = -point[1] * factor + HEIGHT / 2  # Invert y-axis for screen coordinates
    return np.array([x, y])

# ---------- Transform a point from world to camera coordinates ----------
def transform_point(point):
    # Translate relative to the camera
    p = point - camera_pos

    # Build rotation matrices for pitch (around X) and yaw (around Y)
    pitch, yaw = camera_rot
    cos_p, sin_p = math.cos(pitch), math.sin(pitch)
    cos_y, sin_y = math.cos(yaw), math.sin(yaw)

    R_pitch = np.array([
        [1,     0,      0],
        [0, cos_p, -sin_p],
        [0, sin_p,  cos_p]
    ])
    R_yaw = np.array([
        [cos_y, 0, sin_y],
        [0,     1,    0],
        [-sin_y, 0, cos_y]
    ])

    p = R_yaw @ (R_pitch @ p)
    return p

# ---------- OBJ Loader Function ----------
def load_obj(filename):
    """A minimal OBJ file parser.
       Returns a tuple: (list_of_vertices, list_of_faces)
       Faces are returned as tuples of vertex indices (0-indexed).
       Faces with more than 3 vertices are triangulated with a fan method."""
    vertices = []
    faces = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('v '):
                parts = line.strip().split()
                # Convert vertex coordinates to floats
                vertex = np.array([float(parts[1]), float(parts[2]), float(parts[3])])
                vertices.append(vertex)
            elif line.startswith('f '):
                parts = line.strip().split()
                face = []
                for part in parts[1:]:
                    # OBJ indices are 1-indexed; split by '/' in case texture/normal info exists.
                    idx = int(part.split('/')[0]) - 1
                    face.append(idx)
                # Triangulate if the face has more than 3 vertices
                if len(face) > 3:
                    for i in range(1, len(face)-1):
                        faces.append((face[0], face[i], face[i+1]))
                else:
                    faces.append(tuple(face))
    return vertices, faces

# ---------- Choose Object to Render ----------
# Set this to the path of your OBJ file (exported from Blender) if available.
# Otherwise, the code will default to a cube.
obj_file = None  # e.g., "blender_object.obj"

if obj_file is not None:
    try:
        obj_vertices, obj_faces = load_obj(obj_file)
        vertices = obj_vertices
        triangles = obj_faces
        print(f"Loaded {len(vertices)} vertices and {len(triangles)} faces from {obj_file}")
    except Exception as e:
        print("Error loading OBJ file:", e)
        sys.exit(1)
else:
    # ---------- Define a Cube in 3D Space (Fallback) ----------
    vertices = [
        np.array([-1, -1, -1]),
        np.array([ 1, -1, -1]),
        np.array([ 1,  1, -1]),
        np.array([-1,  1, -1]),
        np.array([-1, -1,  1]),
        np.array([ 1, -1,  1]),
        np.array([ 1,  1,  1]),
        np.array([-1,  1,  1]),
    ]
    triangles = [
        (0, 1, 2), (0, 2, 3),   # back face
        (1, 5, 6), (1, 6, 2),   # right face
        (5, 4, 7), (5, 7, 6),   # front face
        (4, 0, 3), (4, 3, 7),   # left face
        (3, 2, 6), (3, 6, 7),   # top face
        (0, 4, 5), (0, 5, 1)    # bottom face
    ]

# ---------- Light Direction for Shading ----------
light_dir = np.array([0, 0, -1], dtype=float)
light_dir /= np.linalg.norm(light_dir)

# ---------- Main Loop ----------
running = True
while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                break

    # --- Mouse Look ---
    mouse_dx, mouse_dy = pygame.mouse.get_rel()
    camera_rot[1] += mouse_dx * mouse_sensitivity  # yaw
    camera_rot[0] += -mouse_dy * mouse_sensitivity # pitch
    camera_rot[0] = max(-math.pi/2, min(math.pi/2, camera_rot[0]))

    # --- Keyboard Movement (WASD) ---
    keys = pygame.key.get_pressed()
    forward = np.array([0, 0, 1])
    right = np.array([1, 0, 0])
    cos_y, sin_y = math.cos(camera_rot[1]), math.sin(camera_rot[1])
    R_yaw = np.array([[cos_y, 0, sin_y],
                      [0, 1, 0],
                      [-sin_y, 0, cos_y]])
    forward = R_yaw @ forward
    right = R_yaw @ right
    if keys[pygame.K_w]:
        camera_pos += forward * move_speed
    if keys[pygame.K_s]:
        camera_pos -= forward * move_speed
    if keys[pygame.K_a]:
        camera_pos -= right * move_speed
    if keys[pygame.K_d]:
        camera_pos += right * move_speed

    screen.fill((30, 30, 30))
    projected_triangles = []

    # Process each triangle
    for tri in triangles:
        pts_world = [vertices[i] for i in tri]
        pts_cam = [transform_point(pt) for pt in pts_world]

        # Back-face culling: compute the normal
        v1 = pts_cam[1] - pts_cam[0]
        v2 = pts_cam[2] - pts_cam[0]
        normal = np.cross(v1, v2)
        norm_len = np.linalg.norm(normal)
        if norm_len == 0:
            continue
        normal /= norm_len

        # Skip triangles facing away (normal z >= 0)
        if normal[2] >= 0:
            continue

        avg_depth = np.mean([pt[2] for pt in pts_cam])
        try:
            pts_proj = [project(pt) for pt in pts_cam if pt[2] > 0]
            if len(pts_proj) < 3:
                continue
        except Exception as e:
            continue

        brightness = np.dot(normal, light_dir)
        brightness = max(0.1, brightness)
        base_color = np.array([50, 100, 255])
        color = (base_color * brightness).clip(0, 255).astype(int)
        color = tuple(color.tolist())

        projected_triangles.append((avg_depth, pts_proj, color))
    
    projected_triangles.sort(key=lambda item: item[0], reverse=True)
    for depth, pts, color in projected_triangles:
        if len(pts) >= 3:
            pygame.draw.polygon(screen, color, pts)

    pygame.display.flip()

pygame.quit()
sys.exit()
