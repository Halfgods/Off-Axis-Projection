import pygame
import cv2
import mediapipe as mp
import numpy as np
import threading
import time

# ============================================================
# 1. CONFIGURATION
# ============================================================

WIDTH, HEIGHT = 1000, 700
UNIT_SCALE = 350
EYE_DEPTH = 2.0
ROOM_DEPTH = 8.0

NEON_BLUE = (0, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# ============================================================
# 2. Point3D Object
# ============================================================

class Point3D:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

# ============================================================
# 3. Off-Axis Projection
# ============================================================

def project_off_axis(p: Point3D, hx, hy):
    total_depth = EYE_DEPTH + p.z
    if total_depth <= 0.1:
        return None

    ratio = EYE_DEPTH / total_depth
    screen_x = hx + (p.x - hx) * ratio
    screen_y = hy + (p.y - hy) * ratio

    px = int(WIDTH/2 + screen_x * UNIT_SCALE)
    py = int(HEIGHT/2 + screen_y * UNIT_SCALE)
    return (px, py)

# ============================================================
# 4. 3D ROTATIONS
# ============================================================

def rotate3d(p: Point3D, ax, ay, az):
    """Rotates a point around X, Y, Z axes."""
    x, y, z = p.x, p.y, p.z

    # X-axis
    cosx, sinx = np.cos(ax), np.sin(ax)
    y, z = y*cosx - z*sinx, y*sinx + z*cosx

    # Y-axis
    cosy, siny = np.cos(ay), np.sin(ay)
    x, z = x*cosy + z*siny, -x*siny + z*cosy

    # Z-axis
    cosz, sinz = np.cos(az), np.sin(az)
    x, y = x*cosz - y*sinz, x*sinz + y*cosz

    return Point3D(x, y, z)

# ============================================================
# 5. FILLED ROTATING CUBE
# ============================================================

def draw_filled_cube(surface, hx, hy, angle):
    size = 0.35                # <<< VERY SMALL CUBE
    cx, cy, cz = 0, 0, 4       # cube world position

    base = [
        Point3D(-size, -size, -size),
        Point3D(size, -size, -size),
        Point3D(size, size, -size),
        Point3D(-size, size, -size),

        Point3D(-size, -size, size),
        Point3D(size, -size, size),
        Point3D(size, size, size),
        Point3D(-size, size, size),
    ]

    # rotate
    rotated = [rotate3d(p, angle*0.6, angle, angle*0.4) for p in base]

    # translate
    verts = [Point3D(p.x + cx, p.y + cy, p.z + cz) for p in rotated]

    faces = [
        (0,1,2,3),  # back
        (4,5,6,7),  # front
        (0,1,5,4),  # top
        (2,3,7,6),  # bottom
        (1,2,6,5),  # right
        (3,0,4,7),  # left
    ]

    # depth sorting
    face_depths = []
    for f in faces:
        avg_z = sum(verts[i].z for i in f) / 4
        face_depths.append((avg_z, f))
    face_depths.sort(reverse=True)

    # draw
    for _, f in face_depths:
        pts = []
        for i in f:
            pp = project_off_axis(verts[i], hx, hy)
            if not pp:
                pts = []
                break
            pts.append(pp)

        if pts:
            pygame.draw.polygon(surface, (255, 50, 50), pts)    # fill
            pygame.draw.polygon(surface, (255, 0, 0), pts, 2)   # outline

# ============================================================
# 6. GLOWING DIAMOND
# ============================================================

def draw_diamond(surface, hx, hy, angle):
    d = 0.55
    cx, cy, cz = 1.3, 0, 4

    points = [
        Point3D(0, d, 0),
        Point3D(d, 0, 0),
        Point3D(0, -d, 0),
        Point3D(-d, 0, 0),
        Point3D(0, 0, d),
        Point3D(0, 0, -d),
    ]

    # rotate diamond very slightly
    rotated = [rotate3d(p, 0, angle*0.6, 0) for p in points]
    verts = [Point3D(p.x + cx, p.y + cy, p.z + cz) for p in rotated]

    edges = [
        (0,4),(1,4),(2,4),(3,4),
        (0,5),(1,5),(2,5),(3,5),
        (0,1),(1,2),(2,3),(3,0)
    ]

    # glow
    for glow in range(6):
        alpha = 255 - glow * 40
        col = (255, alpha, alpha)

        for e in edges:
            p1 = project_off_axis(verts[e[0]], hx, hy)
            p2 = project_off_axis(verts[e[1]], hx, hy)
            if p1 and p2:
                pygame.draw.line(surface, col, p1, p2, 2)

# ============================================================
# 7. GRID ROOM
# ============================================================

def draw_full_grid(surface, hx, hy):
    w_room = 3.0
    h_room = 2.2
    spacing = 1

    for x in np.arange(-w_room, w_room+0.1, spacing):
        p1 = project_off_axis(Point3D(x, -h_room, 0), hx, hy)
        p2 = project_off_axis(Point3D(x, -h_room, ROOM_DEPTH), hx, hy)
        if p1 and p2: pygame.draw.line(surface, NEON_BLUE, p1, p2, 1)

        p3 = project_off_axis(Point3D(x, h_room, 0), hx, hy)
        p4 = project_off_axis(Point3D(x, h_room, ROOM_DEPTH), hx, hy)
        if p3 and p4: pygame.draw.line(surface, NEON_BLUE, p3, p4, 1)

    for y in np.arange(-h_room, h_room+0.1, spacing):
        p1 = project_off_axis(Point3D(-w_room, y, 0), hx, hy)
        p2 = project_off_axis(Point3D(-w_room, y, ROOM_DEPTH), hx, hy)
        if p1 and p2: pygame.draw.line(surface, NEON_BLUE, p1, p2, 1)

        p3 = project_off_axis(Point3D(w_room, y, 0), hx, hy)
        p4 = project_off_axis(Point3D(w_room, y, ROOM_DEPTH), hx, hy)
        if p3 and p4: pygame.draw.line(surface, NEON_BLUE, p3, p4, 1)

    for z in np.arange(0, ROOM_DEPTH+0.1, spacing):
        tl = project_off_axis(Point3D(-w_room, h_room, z), hx, hy)
        tr = project_off_axis(Point3D(w_room, h_room, z), hx, hy)
        br = project_off_axis(Point3D(w_room, -h_room, z), hx, hy)
        bl = project_off_axis(Point3D(-w_room, -h_room, z), hx, hy)

        if tl and tr and br and bl:
            pygame.draw.line(surface, NEON_BLUE, tl, tr, 1)
            pygame.draw.line(surface, NEON_BLUE, bl, br, 1)
            pygame.draw.line(surface, NEON_BLUE, tl, bl, 1)
            pygame.draw.line(surface, NEON_BLUE, tr, br, 1)

# ============================================================
# 8. HEAD TRACKING
# ============================================================

class HeadTracking:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.mp = mp.solutions.face_mesh
        self.mesh = self.mp.FaceMesh(max_num_faces=1, refine_landmarks=True)

        self.head_x, self.head_y = 0.0, 0.0
        self.running = True

        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while self.running:
            ok, frame = self.cap.read()
            if not ok:
                time.sleep(0.1)
                continue

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = self.mesh.process(rgb)

            if res.multi_face_landmarks:
                pt = res.multi_face_landmarks[0].landmark[168]
                self.head_x = (pt.x - 0.5) * 2
                self.head_y = (pt.y - 0.5) * 2

            time.sleep(1/60)

    def stop(self):
        self.running = False
        self.cap.release()

# ============================================================
# 9. MAIN LOOP
# ============================================================

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    tracker = HeadTracking()
    angle = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)

        hx = tracker.head_x
        hy = tracker.head_y

        draw_full_grid(screen, hx, hy)
        draw_filled_cube(screen, hx, hy, angle)
        draw_diamond(screen, hx, hy, angle)

        pygame.display.flip()
        angle += 0.02
        clock.tick(60)

    tracker.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
