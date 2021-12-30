from locale import normalize
import taichi as ti
import numpy as np
from util_classes import Camera, Sphere, Hittable_list, Ray, QuadranglePlane, Cube
from util_rotation import Rotation, Quaternion
# from util_building import generate_block
ti.init(arch=ti.gpu,kernel_profiler=False)

screen_width, screen_height = 640, 640
screen = ti.Vector.field(3, dtype=ti.f32, shape=(screen_width, screen_height))
camera = Camera()
samples_per_pixel = 1

@ti.func
def to_light_source(hit_point, light_source):
    return light_source - hit_point

# Lambertian reflection model
@ti.func
def ray_color(ray):
    default_color = ti.Vector([0.0, 0.0, 0.0])
    scattered_origin = ray.origin
    scattered_direction = ray.direction
    is_hit, closest_t, hit_point, hit_point_normal, front_face, material, color = scene.hit(Ray(scattered_origin, scattered_direction))
    if is_hit:
        if material == 0:
            # default_color = color
            normalize_dist = closest_t / 2.8
            if (normalize_dist < 1):
                default_color = color
            else:
                default_color = color / normalize_dist / normalize_dist
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
        # TODO: restrict an angle-to-center to mimic the light focus
        screen[i, j] = color


gui = ti.GUI("Magic building", (screen_width, screen_height))
start_mouse_x, start_mouse_y, stop_mouse_x, stop_mouse_y, dragging_mouse_x, dragging_mouse_y = 0, 0, 0, 0, 0, 0
is_dragging = False
scene = Hittable_list()
# building_map = np.zeros(shape=(2,1,3), dtype='int')
# building_map[0,:,:] = 1
# building_map[:,0,:] = 1
# building_map[:,:,0] = 1
# x_ofs, y_ofs, z_ofs = 1.5, 1.5, 1.5
# lcube = 1
# for i,j,k in zip(*building_map.nonzero()):
#     print(i,j,k)
#     scene.add(QuadranglePlane(color=[1.0, 0.0, 0.0]))

def cube_add(scene, origin, length):
    point_LFD = origin
    point_RFD = origin + ti.Vector([length, 0.0, 0.0])
    point_LBD = origin + ti.Vector([0.0, length, 0.0])
    point_RBD = origin + ti.Vector([length, length, 0.0])
    point_LFU = origin + ti.Vector([0.0, 0.0, length])
    point_RFU = origin + ti.Vector([length, 0.0, length])
    point_LBU = origin + ti.Vector([0.0, length, length])
    point_RBU = origin + ti.Vector([length, length, length])
    # Front
    scene.add_wall(QuadranglePlane(
            point_LFD, point_LFU, point_RFU, point_RFD, color = ti.Vector([1.0, 0.0, 0.0])
    ))
    # Back
    scene.add_wall(QuadranglePlane(
            point_LBD, point_LBU, point_RBU, point_RBD, color = ti.Vector([0.0, 1.0, 0.0])
    ))
    # Left
    scene.add_wall(QuadranglePlane(
        point_LBD, point_LFD, point_LFU, point_LBU, color = ti.Vector([0.0, 0.0, 1.0])
    ))
    # right
    scene.add_wall(QuadranglePlane(
        point_RBD, point_RFD, point_RFU, point_RBU, color = ti.Vector([0.0, 1.0, 1.0])
    ))
    # Up
    scene.add_wall(QuadranglePlane(
        point_LBU, point_RBU, point_RFU, point_LFU, color = ti.Vector([1.0, 1.0, 0.0])
    ))
    # Down
    scene.add_wall(QuadranglePlane(
        point_LBD, point_RBD, point_RFD, point_LFD, color = ti.Vector([1.0, 0.0, 1.0])
    ))
# cube_add(scene, ti.Vector([1.0, 1.0, 1.0]), 2)


cube_add(scene, ti.Vector([-3.0, -3.0, -3.0]), 6)
    # scene.add(Cube(ti.Vector([i * lcube + x_ofs, j * lcube + y_ofs, k * lcube + z_ofs]), length = lcube))

# plane = QuadranglePlane(
#     pointA=ti.Vector([-0.5, -0.5, 0.5]),
#     pointB=ti.Vector([-0.5, 0.5, 0.5]),
#     pointC=ti.Vector([0.5, 0.5, 0.5]),
#     pointD=ti.Vector([0.5, -0.5,  0.5]),
#     color = ti.Vector([0.12, 0.34, 0.56])      
# )

# scene.add(Cube(origin = ti.Vector([0.5, 0.5, 0.5]), length = 1.0))

# # Light source
# scene.add(Sphere(center=ti.Vector([0, 5.4, -1]), radius=3.0, material=0, color=ti.Vector([10.0, 10.0, 10.0])))
# # # Ground
# scene.add(Sphere(center=ti.Vector([0, -100.5, -1]), radius=100.0, material=1, color=ti.Vector([0.8, 0.8, 0.8])))
# # ceiling
# scene.add(Sphere(center=ti.Vector([0, 102.5, -1]), radius=100.0, material=1, color=ti.Vector([0.8, 0.8, 0.8])))
# # # back wall
# # scene.add(Sphere(center=ti.Vector([0, 1, 101]), radius=100.0, material=1, color=ti.Vector([0.8, 0.8, 0.8])))
# # right wall
# scene.add(Sphere(center=ti.Vector([-101.5, 0, -1]), radius=100.0, material=1, color=ti.Vector([0.6, 0.0, 0.0])))
# # left wall
# scene.add(Sphere(center=ti.Vector([101.5, 0, -1]), radius=100.0, material=1, color=ti.Vector([0.0, 0.6, 0.0])))

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
    ti.Vector([0.0, 0.0, -1.0])
    )
look_from = ti.Vector([0.0, 0.0, 0.0])
look_from_init = look_from

# We use a state recording method to implement a fluent long-press
is_pressed = [0, 0, 0, 0, 0, 0] # [S/down, W/up, D/right, A/left, LBM/cc-wise, RBM/c-wise]
is_going_forward = 0

def check_eaten_food(my_position, food_position):
    if (my_position - food_position).norm() < 1.5e-1:
        return True
    return False

def generate_food_position():
    food_position = ti.Vector([
        np.random.uniform(-2.8, 2.8),
        np.random.uniform(-2.8, 2.8),
        np.random.uniform(-2.8, 2.8),
    ])
    print(f"{food_position=}")
    return food_position
# food_position = generate_food_position()
init_position = ti.Vector([0, 0, 2])
food_position = ti.Vector([0, 0, 2])
# scene.add_food(Sphere(center=ti.Vector([-101.5, 0, -1]), radius=100.0, material=1, color=ti.Vector([0.6, 0.0, 0.0])))
food = Sphere(center=food_position, radius=0.1, material=2, color = ti.Vector([0.5, 0.2, 0.3]))
scene.add_food(food)

my_score = 0
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
                my_score = 0
                camera.reset()
                food.set_center(init_position)
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
        try_look_from = look_from - rotation.w * 0.03
        if abs(try_look_from[0]) < 2.8 and abs(try_look_from[1]) < 2.8 and abs(try_look_from[2]) < 2.8:
            look_from = try_look_from
            camera.set_lookfrom(*look_from)
            if check_eaten_food(look_from, food_position):
                my_score += 1
                # scene.clear_food()
                food_position = generate_food_position()
                food.set_center(food_position)
                # scene.add_food(Sphere(center=food_position, radius=0.1, material=0, color = ti.Vector([0.5, 0.2, 0.3])))


    update_camera() 

    # ti.print_kernel_profile_info('trace')
    # ti.print_profile_info()
    # exit()
    gui.set_image(screen)

    gui.text(
        content=f'W/A/S/D/Left-Click/Right-Click: rotate', pos=(0.03, 0.99), color=0x000000
    )
    gui.text(
        content=f'Space: go forward', pos=(0.03, 0.97), color=0x000000
    )
    gui.text(
        content=f'Eat the food (ball) in the cube', pos=(0.03, 0.93), color=0x000000
    )
    gui.text(
        content=f'Your score: {my_score}', pos=(0.03, 0.91), color=0x000000
    )
    gui.text(
        content=f'Your Position: {look_from}', pos=(0.03, 0.89), color=0x000000
    )
    gui.text(
        content=f'Food Position: {food_position}', pos=(0.03, 0.87), color=0x000000
    )
    gui.text(
        content=f'sky=X+, blue=X-, green=Y+, Red=Y-, yellow=Z+, pink=Z-', pos=(0.03, 0.85), color=0x000000
    )
    # gui.text(
    # content=f'start_x, start_y = {start_mouse_x:.2f}, {start_mouse_y:.2f}', pos=(0.6, 0.9), color=0xFFFFFF)
    # gui.text(
    # content=f'dragging_x, dragging_y = {dragging_mouse_x:.2f}, {dragging_mouse_y:.2f}', pos=(0.6, 0.85), color=0xFFFFFF)
    # gui.text(
    # content=f'stop_x, stop_y = {stop_mouse_x:.2f}, {stop_mouse_y:.2f}', pos=(0.6, 0.8), color=0xFFFFFF)

    # gui.text(
    # content=f'({a[0]:.2f}, {a[1]:.2f}, {a[2]:.2f}),  ({b[0]:.2f}, {b[1]:.2f}, {b[2]:.2f})', pos=(0.6, 0.75), color=0xFFFFFF)
    
    gui.show()
