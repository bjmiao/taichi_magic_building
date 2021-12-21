import taichi as ti
from util_classes import Camera, Sphere, Hittable_list, Ray, QuadranglePlane, Cube
from util_rotation import Rotation, Quaternion
ti.init(arch=ti.gpu)

screen_width, screen_height = 640, 640
screen = ti.Vector.field(3, dtype=ti.f32, shape=(screen_width, screen_height))
camera = Camera()
samples_per_pixel = 100

@ti.func
def to_light_source(hit_point, light_source):
    return light_source - hit_point

# Lambertian reflection model
@ti.func
def ray_color(ray):
    default_color = ti.Vector([1.0, 1.0, 1.0])
    scattered_origin = ray.origin
    scattered_direction = ray.direction
    is_hit, hit_point, hit_point_normal, front_face, material, color = scene.hit(Ray(scattered_origin, scattered_direction))
    if is_hit:
        if material == 0:
            default_color = color
        else:
            hit_point_to_source = to_light_source(hit_point, ti.Vector([0, 5.4 - 3.0, -1]))
            default_color = color * ti.max(hit_point_to_source.dot(hit_point_normal) / (hit_point_to_source.norm() * hit_point_normal.norm()), 0.0)
    return default_color

@ti.kernel
def update_camera():
    for i, j in screen:
        u = (i + ti.random()) / screen_width
        v = (j + ti.random()) / screen_height
        color = ti.Vector([0.0, 0.0, 0.0])

        for n in range(samples_per_pixel):
            ray = camera.get_ray(u, v)
            color += ray_color(ray)
        color /= samples_per_pixel
        screen[i, j] = color


gui = ti.GUI("Magic building", (screen_width, screen_height))
start_mouse_x, start_mouse_y, stop_mouse_x, stop_mouse_y, dragging_mouse_x, dragging_mouse_y = 0, 0, 0, 0, 0, 0
is_dragging = False

scene = Hittable_list()
# plane = QuadranglePlane(
#     pointA=ti.Vector([-0.5, -0.5, 0.5]),
#     pointB=ti.Vector([-0.5, 0.5, 0.5]),
#     pointC=ti.Vector([0.5, 0.5, 0.5]),
#     pointD=ti.Vector([0.5, -0.5,  0.5]),
#     color = ti.Vector([0.12, 0.34, 0.56])      
# )

scene.add(Cube(origin = ti.Vector([0.5, 0.5, 0.5]), length = 1.0))

# Light source
scene.add(Sphere(center=ti.Vector([0, 5.4, -1]), radius=3.0, material=0, color=ti.Vector([10.0, 10.0, 10.0])))
# Ground
scene.add(Sphere(center=ti.Vector([0, -100.5, -1]), radius=100.0, material=1, color=ti.Vector([0.8, 0.8, 0.8])))
# ceiling
scene.add(Sphere(center=ti.Vector([0, 102.5, -1]), radius=100.0, material=1, color=ti.Vector([0.8, 0.8, 0.8])))
# back wall
scene.add(Sphere(center=ti.Vector([0, 1, 101]), radius=100.0, material=1, color=ti.Vector([0.8, 0.8, 0.8])))
# right wall
scene.add(Sphere(center=ti.Vector([-101.5, 0, -1]), radius=100.0, material=1, color=ti.Vector([0.6, 0.0, 0.0])))
# left wall
scene.add(Sphere(center=ti.Vector([101.5, 0, -1]), radius=100.0, material=1, color=ti.Vector([0.0, 0.6, 0.0])))

# # Diffuse ball
# scene.add(Sphere(center=ti.Vector([0, -0.2, -1.5]), radius=0.3, material=1, color=ti.Vector([0.8, 0.3, 0.3])))
# # Metal ball
# scene.add(Sphere(center=ti.Vector([-0.8, 0.2, -1]), radius=0.7, material=2, color=ti.Vector([0.6, 0.8, 0.8])))
# # Glass ball
# scene.add(Sphere(center=ti.Vector([0.7, 0, -0.5]), radius=0.5, material=3, color=ti.Vector([1.0, 1.0, 1.0])))
# # Metal ball-2
# scene.add(Sphere(center=ti.Vector([0.6, -0.3, -2.0]), radius=0.2, material=2, color=ti.Vector([0.8, 0.6, 0.2])))

# init direction
rotation = Rotation(
    ti.Vector([-1.0, 0.0, 0.0]),
    ti.Vector([0.0, 1.0, 0.0]),
    ti.Vector([0.0, 0.0, -1.0]),
    )
look_from = ti.Vector([0.0, 1.0, -5.0])
look_from_init = look_from

# We use a state recording method to implement a fluent long-press
is_pressed = [0, 0, 0, 0, 0, 0] # [S/down, W/up, D/right, A/left, LBM/cc-wise, RBM/c-wise]
is_going_forward = 0
while gui.running:
    for e in gui.get_events(ti.GUI.PRESS, ti.GUI.MOTION, ti.GUI.RELEASE):
        if e.type == ti.GUI.PRESS:
            if e.key == 's' or e.key == 'S':
                is_pressed[0] = 1
            elif e.key == 'w' or e.key == 'W':
                is_pressed[1] = 1
            elif e.key == 'd' or e.key == 'D':
                is_pressed[2] = 1
            elif e.key == 'a' or e.key == 'A':
                is_pressed[3] = 1
            elif e.key == ti.GUI.LMB:
                is_pressed[4] = 1
            elif e.key == ti.GUI.RMB:
                is_pressed[5] = 1
            elif e.key == ti.GUI.SPACE:
                is_going_forward = 1
            elif e.key == 'r' or e.key == 'R':
                look_from = look_from_init
                camera.reset()
                rotation.reset()

        if e.type == ti.GUI.RELEASE:
            if e.key == 's' or e.key == 'S':
                is_pressed[0] = 0
            elif e.key == 'w' or e.key == 'W':
                is_pressed[1] = 0
            elif e.key == 'd' or e.key == 'D':
                is_pressed[2] = 0
            elif e.key == 'a' or e.key == 'A':
                is_pressed[3] = 0
            elif e.key == ti.GUI.LMB:
                is_pressed[4] = 0
            elif e.key == ti.GUI.RMB:
                is_pressed[5] = 0
            elif e.key == ti.GUI.SPACE:
                is_going_forward = 0

    if (sum(is_pressed) > 0):
        rotation.rotate(ti.Vector([is_pressed[1] - is_pressed[0], is_pressed[3] - is_pressed[2], is_pressed[5] - is_pressed[4]]))
        camera.set_direction_w(*rotation.w, 0)
        camera.set_direction_u(*rotation.u, 0)
        camera.set_direction_v(*rotation.v, 1)  # We only need update camera parameter at last

    if (is_going_forward):
        look_from = look_from - rotation.w * 0.01
        camera.set_lookfrom(*look_from)

    update_camera()
    gui.set_image(screen)

    # gui.text(
    # content=f'Mouse_x, mouse_y = {now_mouse_x:.2f}, {now_mouse_y:.2f}', pos=(0.6, 0.95), color=0xFFFFFF)
    # gui.text(
    # content=f'start_x, start_y = {start_mouse_x:.2f}, {start_mouse_y:.2f}', pos=(0.6, 0.9), color=0xFFFFFF)
    # gui.text(
    # content=f'dragging_x, dragging_y = {dragging_mouse_x:.2f}, {dragging_mouse_y:.2f}', pos=(0.6, 0.85), color=0xFFFFFF)
    # gui.text(
    # content=f'stop_x, stop_y = {stop_mouse_x:.2f}, {stop_mouse_y:.2f}', pos=(0.6, 0.8), color=0xFFFFFF)

    # gui.text(
    # content=f'({a[0]:.2f}, {a[1]:.2f}, {a[2]:.2f}),  ({b[0]:.2f}, {b[1]:.2f}, {b[2]:.2f})', pos=(0.6, 0.75), color=0xFFFFFF)
    
    gui.show()
