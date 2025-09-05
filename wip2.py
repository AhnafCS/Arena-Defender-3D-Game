from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random

# ---------- Window ----------
W, H = 1200, 720

# ---------- Rooms config ----------
rooms = [
    {"name": "Start Room", "size": 60, "wall_height": 25.0, "wall_thick": 0.5, "floor_color": (1, 0.21, 0.88)},
    {"name": "Middle Room", "size": 90, "wall_height": 30.0, "wall_thick": 0.5, "floor_color": (0.5, 0.8, 0.5)},
    {"name": "Final Room", "size": 110, "wall_height": 35.0, "wall_thick": 0.5, "floor_color": (0.537, 0.655, 1)}
]


current_room_index = 0
DOOR_WIDTH = 10
enemy_types = ["rolling_ball", "cube_bot", "spider"]
enemies = []  # list of dicts for each enemy

MAX_ENEMIES_PER_ROOM = 5
# ---------- Camera ----------
camera = {
    "distance": 25.0,   # third person distance
    "height": 15.0,     # above player
    "angle": 180.0,     # horizontal orbit (degrees)
    "pitch": 0.0        # vertical tilt
}

# ---------- Player ----------
player = {
    "x": 0.0,
    "y": 0.0,
    "z": 0.0,
    "speed": 1.0,
    "size": 1.0,
    "angle": 180
}

# ---------- OpenGL Init ----------
def init_gl():
    glClearColor(0.05, 0.07, 0.10, 1.0)

def reshape(w, h):
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, w/float(h), 0.1, 500.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

# ---------- Drawing Functions ----------
def draw_player():
    glPushMatrix()
    glTranslatef(player["x"], 1.0, player["z"])
    glRotatef(player["angle"], 0, 1, 0)

    # Body
    glPushMatrix()
    glScalef(0.90, 1.8, 0.7)
    glTranslatef(0,0.6,0)
    glColor3f(0.2, 0.6, 1.0)
    glutSolidSphere(player["size"], 16, 16)
    glPopMatrix()

    # Head
    glPushMatrix()
    glTranslatef(0.0, 3.1, 0.0)
    glColor3f(1.0, 0.8, 0.6)
    glutSolidSphere(0.6, 16, 16)
    glPopMatrix()

    # Hair
    glPushMatrix()
    glTranslatef(0.0, 3.7, 0)
    glScalef(1.3, 0.4, 0.7)
    glColor3f(0, 0, 0)
    glutSolidCube(1)
    glPopMatrix()

    # Arms
    glPushMatrix()
    glTranslatef(-1.0, 1.2, 0.0)
    glRotatef(90, 0, 0, 1)
    glColor3f(1.0, 0.8, 0.6)
    gluCylinder(gluNewQuadric(),0.2,0.1, 1.2, 8, 8)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(1.0, 1.2, 0.0)
    glRotatef(-90, 0, 0, 1)
    glColor3f(1.0, 0.8, 0.6)
    gluCylinder(gluNewQuadric(),0.2,0.1, 1.2, 8, 8)
    glPopMatrix()

    # Legs
    glPushMatrix()
    glTranslatef(-0.4, -0.2, 0.0)
    glRotatef(90, 1, 0, 0)
    glColor3f(0.3, 0.3, 0.8)
    gluCylinder(gluNewQuadric(), 0.25, 0.15, 1.5, 8, 8)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.4, -0.2, 0.0)
    glRotatef(90, 1, 0, 0)
    glColor3f(0.3, 0.3, 0.8)
    gluCylinder(gluNewQuadric(), 0.25, 0.15, 1.5, 8, 8)
    glPopMatrix()

    glPopMatrix()

def clamp_player():
    margin = 2.0
    room = rooms[current_room_index]
    limit = room["size"] - margin

    # Allow player to move through door on north wall
    if player["z"] >= room["size"] - 5:  # near north wall
        player["x"] = max(-DOOR_WIDTH/2, min(DOOR_WIDTH/2, player["x"]))
        # Allow z to slightly exceed north wall
        player["z"] = min(room["size"] + 5, player["z"])
    else:
        player["x"] = max(-limit, min(limit, player["x"]))
        player["z"] = max(-limit, min(limit, player["z"]))

# def draw_floor(size):
#     glPushMatrix()
#     max_radius = 2 * size
#     step = 6
#     for r in range(max_radius, 0, -step):
#         color_factor = r / max_radius
#         glColor3f(0.6 + 0.6*(1-color_factor),
#                   0.2 + 0.5*(1-color_factor),
#                   0.4 + 0.5*(1-color_factor))
#         glPushMatrix()
#         glScalef(r, 1, r)
#         glutSolidCube(1)
#         glPopMatrix()
#     glPopMatrix()
def draw_floor(size):
    room = rooms[current_room_index]
    base_color = room["floor_color"]

    glPushMatrix()
    max_radius = 2 * size
    step = 6
    for r in range(max_radius, 0, -step):
        color_factor = r / max_radius
        glColor3f(
            base_color[0] * color_factor,
            base_color[1] * color_factor,
            base_color[2] * color_factor
        )
        glPushMatrix()
        glScalef(r, 1, r)
        glutSolidCube(1)
        glPopMatrix()
    glPopMatrix()

def draw_walls():
    room = rooms[current_room_index]
    half = room["size"]
    h = room["wall_height"]
    t = room["wall_thick"]

    glColor3f(0, 0.078, 0.31)

    # Left part of north wall
    glPushMatrix()
    glTranslatef(-half + (half - DOOR_WIDTH)/2, h/2, half)
    glScalef(half - DOOR_WIDTH, h, t)
    glutSolidCube(1)
    glPopMatrix()

    # Right part of north wall
    glPushMatrix()
    glTranslatef(half - (half - DOOR_WIDTH)/2, h/2, half)
    glScalef(half - DOOR_WIDTH, h, t)
    glutSolidCube(1)
    glPopMatrix()


    # South wall
    glPushMatrix()
    glTranslatef(0, h/2, -half)
    glScalef(2*half, h, t)
    glutSolidCube(1)
    glPopMatrix()

    # East wall
    glPushMatrix()
    glTranslatef(half, h/2, 0)
    glScalef(t, h, 2*half)
    glutSolidCube(1)
    glPopMatrix()

    # West wall
    glPushMatrix()
    glTranslatef(-half, h/2, 0)
    glScalef(t, h, 2*half)
    glutSolidCube(1)
    glPopMatrix()

def spawn_enemies():
    """Spawn random enemies in the current room."""
    global enemies
    enemies = []
    room = rooms[current_room_index]
    half = room["size"] - 5  # keep away from walls

    for _ in range(MAX_ENEMIES_PER_ROOM):
        etype = random.choice(enemy_types)
        ex = random.uniform(-half, half)
        ez = random.uniform(-half, half)
        enemies.append({"type": etype, 
                        "x": ex, 
                        "z": ez, 
                        "dir": random.uniform(0, 360),
                        "size": 2.0
        })

def update_enemies():
    """Simple AI: move enemies forward along their direction (slower)."""
    room = rooms[current_room_index]
    half = room["size"] - 1

    for e in enemies:
        rad = math.radians(e["dir"])
        speed = 0.01  # slower for easier shooting
        e["x"] += math.sin(rad) * speed
        e["z"] += math.cos(rad) * speed

        # Bounce off walls
        if abs(e["x"]) > half or abs(e["z"]) > half:
            e["dir"] = (e["dir"] + 180) % 360

def draw_enemies():
    """Draw all enemies in the room."""
    for e in enemies:
        if e["type"] == "rolling_ball":
            draw_rolling_ball(e["x"], e["z"], e["size"])
        elif e["type"] == "cube_bot":
            draw_cube_bot(e["x"], e["z"], e["size"])
        elif e["type"] == "spider":
            draw_spider(e["x"], e["z"], e["size"])

# ---------- Enemy Drawing Functions ----------
def draw_rolling_ball(x, z, size):
    glPushMatrix()
    glTranslatef(x, size/2.5, z)
    glColor3f(1.0, 0.0, 0.0)
    glutSolidSphere(size/1.5, 16, 16)
    glPopMatrix()

    #middle sphere
    glPushMatrix()
    glTranslatef(x, size, z)
    glColor3f(1.0, 1.0, 1.0)
    glutSolidCube(2)
    glPopMatrix()
    
    #upper sphere
    glPushMatrix()
    glTranslatef(x, size+2, z)
    glColor3f(1.0, 0.0, 0.0)
    glutSolidSphere(size/2, 16, 16)
    glPopMatrix()

def draw_cube_bot(x, z, size):
    glPushMatrix()
    glTranslatef(x, size/2, z)

    # Body
    glPushMatrix()
    glScalef(size, size*1.5, size)
    glColor3f(0.596, 0.286, 0.949)
    glutSolidCube(1)
    glPopMatrix()


    # Legs
    glPushMatrix()
    glTranslatef(-0.3*size, -size, 0)
    glScalef(0.3*size, size, 0.3*size)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.3*size, -size, 0)
    glScalef(0.3*size, size, 0.3*size)
    glutSolidCube(1)
    glPopMatrix()
    
    # Arms
    glPushMatrix()
    glColor3f(1, 0.325, 0.718)
    glTranslatef(-0.75*size, 0.2*size, 0)
    glScalef(0.2*size, size, 0.2*size)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.75*size, 0.2*size, 0)
    glScalef(0.2*size, size, 0.2*size)
    glutSolidCube(1)
    glPopMatrix()


    glPopMatrix()

def draw_spider(x, z, size):
    y = 0.5  # fixed height above floor
    glPushMatrix()
    glTranslatef(x, y, z)

    # Body
    glColor3f(0.349, 0.157, 0.106)
    glutSolidSphere(size, 16, 16)

    # Head
    glColor3f(0.749, 0.561, 0.514)
    glPushMatrix()
    glTranslatef(0, 0.6*size, size*0.6)
    glutSolidSphere(size*0.6, 12, 12)
    glPopMatrix()

    #front-left
    glPushMatrix()
    glTranslatef(-size, 0, size*0.5)
    glRotatef(-45, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 0.25, 0.15, 1.5, 8, 8)
    glPopMatrix()

    # Front-right
    glPushMatrix()
    glTranslatef(size, 0, size*0.5)
    glRotatef(45, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 0.25, 0.15, 1.5, 8, 8)
    glPopMatrix()

    # Rear-left leg
    glPushMatrix()
    glTranslatef(-size, 0, -size)
    glRotatef(45, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 0.25, 0.15, 1.5, 8, 8)
    glPopMatrix()

    # Rear-right leg
    glPushMatrix()
    glTranslatef(size+1, 0, -size)
    glRotatef(-45, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 0.25, 0.15, 1.5, 8, 8)
    glPopMatrix()


    glPopMatrix()

def check_door_transition():
    global current_room_index
    room = rooms[current_room_index]
    half = room["size"]

    if (player["z"] >= half - 1.0) and (-DOOR_WIDTH/2 <= player["x"] <= DOOR_WIDTH/2):
        if current_room_index < len(rooms) - 1:
            current_room_index += 1
            print("Entered:", rooms[current_room_index]["name"])
            load_room(current_room_index)

def load_room(index):
    # room = rooms[index]
    player["x"] = 0
    player["z"] = 0
    camera["angle"] = random.uniform(90,270)
    player["angle"] = camera["angle"]
    camera["pitch"] = 0
    spawn_enemies()

# ---------- Display & Camera ----------
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    rad = math.radians(camera["angle"])
    pitch_rad = math.radians(camera["pitch"])
    eye_x = player["x"] - camera["distance"] * math.sin(rad)
    eye_z = player["z"] - camera["distance"] * math.cos(rad)
    eye_y = player["y"] + camera["height"] + camera["distance"] * math.sin(pitch_rad)

    gluLookAt(eye_x, eye_y, eye_z,
              player["x"], 1.2, player["z"],
              0, 1, 0)

    room = rooms[current_room_index]
    draw_floor(room["size"])
    draw_walls()
    draw_player()
    update_enemies()
    draw_enemies()

    glutSwapBuffers()

def idle():
    glutPostRedisplay()

# ---------- Input ----------
def keyboard(key, x, y):
    step = player["speed"]
    rad = math.radians(player["angle"])

    if key == b'w':
        player["x"] += math.sin(rad) * step
        player["z"] += math.cos(rad) * step
    elif key == b's':
        player["x"] -= math.sin(rad) * step
        player["z"] -= math.cos(rad) * step
    elif key == b'd':
        player["x"] -= math.cos(rad) * step
        player["z"] += math.sin(rad) * step
    elif key == b'a':
        player["x"] += math.cos(rad) * step
        player["z"] -= math.sin(rad) * step

    clamp_player()
    check_door_transition()
    glutPostRedisplay()

def special_keys(key, x, y):
    if key == GLUT_KEY_RIGHT:
        camera["angle"] -= 6.0
        player["angle"] = camera["angle"]
    elif key == GLUT_KEY_LEFT:
        camera["angle"] += 6.0
        player["angle"] = camera["angle"]
    elif key == GLUT_KEY_UP:
        camera["pitch"] = min(camera["pitch"] + 2.0, 80.0)
    elif key == GLUT_KEY_DOWN:
        camera["pitch"] = max(camera["pitch"] - 2.0, -10.0)
    glutPostRedisplay()

# ---------- Main ----------
def main():
    glutInit([])
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(W, H)
    glutInitWindowPosition(100, 80)
    glutCreateWindow(b"3D Multi-Room Arena")
    init_gl()
    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    spawn_enemies()
    load_room(0)
    glutMainLoop()
    

if __name__ == "__main__":
    main()