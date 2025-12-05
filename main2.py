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
UNIT_SCALE = 300       # Adjusted for better view
EYE_DEPTH = 2.0        # How far "behind" the screen your eyes are
ROOM_DEPTH = 8.0       # How deep the virtual room goes

NEON_BLUE = (0, 255, 255)
RED = (255, 0, 0)
DARK_RED = (100, 0, 0)
BLACK = (10, 10, 10)   # Slightly off-black for atmosphere

# ============================================================
# 2. Point3D Object
# ============================================================

class Point3D:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

# ============================================================
# 3. Off-Axis Projection Logic
# ============================================================

def project_off_axis(p: Point3D, hx, hy):
    """
    Projects a 3D point onto 2D screen based on head position (hx, hy).
    hx, hy are normalized (-1 to 1).
    """
    total_depth = EYE_DEPTH + p.z
    
    # Avoid division by zero or objects behind the camera
    if total_depth <= 0.1:
        return None

    ratio = EYE_DEPTH / total_depth
    
    # Parallax formula
    screen_x = hx + (p.x - hx) * ratio
    screen_y = hy + (p.y - hy) * ratio

    # Convert to pixel coordinates
    px = int(WIDTH/2 + screen_x * UNIT_SCALE)
    py = int(HEIGHT/2 + screen_y * UNIT_SCALE)
    return (px, py)

def rotate3d(p: Point3D, ax, ay, az):
    """Rotates a point around X, Y, Z axes."""
    x, y, z = p.x, p.y, p.z

    # Rotate X
    cosx, sinx = np.cos(ax), np.sin(ax)
    y2 = y*cosx - z*sinx
    z2 = y*sinx + z*cosx
    y, z = y2, z2

    # Rotate Y
    cosy, siny = np.cos(ay), np.sin(ay)
    x2 = x*cosy + z*siny
    z2 = -x*siny + z*cosy
    x, z = x2, z2

    # Rotate Z
    cosz, sinz = np.cos(az), np.sin(az)
    x2 = x*cosz - y*sinz
    y2 = x*sinz + y*cosz
    x, y = x2, y2

    return Point3D(x, y, z)

# ============================================================
# 4. Drawing Functions
# ============================================================

def draw_room_grid(surface, hx, hy):
    """Draws a 3D wireframe room to give perspective context."""
    w = 3.0  # Room half-width
    h = 2.0  # Room half-height
    
    # 1. Draw Longitudinal Lines (Depth lines)
    # Floor and Ceiling
    for x in np.arange(-w, w + 0.1, 1.0):
        p_start = project_off_axis(Point3D(x, h, 0), hx, hy)
        p_end   = project_off_axis(Point3D(x, h, ROOM_DEPTH), hx, hy)
        if p_start and p_end: pygame.draw.line(surface, NEON_BLUE, p_start, p_end, 1)

        p_start = project_off_axis(Point3D(x, -h, 0), hx, hy)
        p_end   = project_off_axis(Point3D(x, -h, ROOM_DEPTH), hx, hy)
        if p_start and p_end: pygame.draw.line(surface, NEON_BLUE, p_start, p_end, 1)

    # Walls
    for y in np.arange(-h, h + 0.1, 1.0):
        p_start = project_off_axis(Point3D(-w, y, 0), hx, hy)
        p_end   = project_off_axis(Point3D(-w, y, ROOM_DEPTH), hx, hy)
        if p_start and p_end: pygame.draw.line(surface, NEON_BLUE, p_start, p_end, 1)

        p_start = project_off_axis(Point3D(w, y, 0), hx, hy)
        p_end   = project_off_axis(Point3D(w, y, ROOM_DEPTH), hx, hy)
        if p_start and p_end: pygame.draw.line(surface, NEON_BLUE, p_start, p_end, 1)

    # 2. Draw Transverse Lines (Slices/Frames)
    for z in np.arange(0, ROOM_DEPTH + 0.1, 1.0):
        # Calculate corners for this slice
        tl = project_off_axis(Point3D(-w, -h, z), hx, hy)
        tr = project_off_axis(Point3D(w, -h, z), hx, hy)
        br = project_off_axis(Point3D(w, h, z), hx, hy)
        bl = project_off_axis(Point3D(-w, h, z), hx, hy)

        if tl and tr and br and bl:
            # Draw rectangle
            pygame.draw.line(surface, NEON_BLUE, tl, tr, 1)
            pygame.draw.line(surface, NEON_BLUE, tr, br, 1)
            pygame.draw.line(surface, NEON_BLUE, br, bl, 1)
            pygame.draw.line(surface, NEON_BLUE, bl, tl, 1)


def draw_filled_cube(surface, hx, hy, angle):
    """Draws a rotating cube using Painter's Algorithm (sort by depth)."""
    size = 0.5
    cx, cy, cz = 0, 0, 4.0  # Center of the cube in the room

    # Define 8 corners of a cube
    # Base configuration
    base_points = [
        Point3D(-size, -size, -size), Point3D(size, -size, -size),
        Point3D(size, size, -size),   Point3D(-size, size, -size),
        Point3D(-size, -size, size),  Point3D(size, -size, size),
        Point3D(size, size, size),    Point3D(-size, size, size),
    ]

    # Rotate points
    rotated_points = [rotate3d(p, angle, angle * 0.5, angle * 0.2) for p in base_points]
    
    # Translate points to room location
    world_points = [Point3D(p.x + cx, p.y + cy, p.z + cz) for p in rotated_points]

    # Define faces (indices of vertices)
    # Order: Back, Front, Top, Bottom, Right, Left
    faces = [
        (0, 1, 2, 3), (4, 5, 6, 7), 
        (0, 1, 5, 4), (2, 3, 7, 6), 
        (1, 2, 6, 5), (3, 0, 4, 7)
    ]

    # Calculate average depth (Z) for each face for sorting
    face_depths = []
    for face_indices in faces:
        avg_z = sum(world_points[i].z for i in face_indices) / 4
        face_depths.append((avg_z, face_indices))

    # Sort faces from farthest to nearest (Painter's Algorithm)
    face_depths.sort(key=lambda x: x[0], reverse=True)

    # Draw faces
    for _, indices in face_depths:
        # Project 3D points to 2D screen
        poly_points = []
        for i in indices:
            p2d = project_off_axis(world_points[i], hx, hy)
            if p2d:
                poly_points.append(p2d)
        
        # Only draw if we have a valid polygon
        if len(poly_points) == 4:
            pygame.draw.polygon(surface, DARK_RED, poly_points)     # Fill
            pygame.draw.polygon(surface, RED, poly_points, 3)       # Outline

# ============================================================
# 5. Head Tracking Class
# ============================================================

class HeadTracking:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.head_x = 0.0
        self.head_y = 0.0
        self.running = True
        
        # Start tracking thread
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def _update_loop(self):
        while self.running and self.cap.isOpened():
            success, image = self.cap.read()
            if not success:
                time.sleep(0.1)
                continue

            # Flip horizontally for mirror view and convert color
            image = cv2.flip(image, 1)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            results = self.face_mesh.process(image_rgb)

            if results.multi_face_landmarks:
                # Get the nose tip or between eyes (landmark 168 is widely used for center)
                landmark = results.multi_face_landmarks[0].landmark[168]
                
                # Normalize coordinates to -1 to 1 range
                # (x - 0.5) * scale
                self.head_x = (landmark.x - 0.5) * 2.0
                self.head_y = (landmark.y - 0.5) * 2.0

            time.sleep(0.01) # Small sleep to save CPU

    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)
        self.cap.release()

# ============================================================
# 6. MAIN EXECUTION
# ============================================================

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Off-Axis Head Tracking Illusion")
    clock = pygame.time.Clock()

    # Initialize Tracker
    print("Starting Webcam...")
    tracker = HeadTracking()

    # Animation state
    angle = 0.0
    running = True

    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Update Logic
        hx = tracker.head_x * 1.5  # Multiply to exaggerate movement sensitivity
        hy = tracker.head_y * 1.5
        angle += 0.02             # Rotation speed

        # Draw
        screen.fill(BLACK)
        
        # Draw background grid
        draw_room_grid(screen, hx, hy)
        
        # Draw floating object
        draw_filled_cube(screen, hx, hy, angle)

        pygame.display.flip()
        clock.tick(60)

    # Cleanup
    tracker.stop()
    pygame.quit()
    cv2.destroyAllWindows()
    print("Program ended.")

if __name__ == "__main__":
    main()