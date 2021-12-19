import taichi as ti
from utils import Camera, Sphere, Hittable_list, Ray
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

# Diffuse ball
scene.add(Sphere(center=ti.Vector([0, -0.2, -1.5]), radius=0.3, material=1, color=ti.Vector([0.8, 0.3, 0.3])))
# Metal ball
scene.add(Sphere(center=ti.Vector([-0.8, 0.2, -1]), radius=0.7, material=2, color=ti.Vector([0.6, 0.8, 0.8])))
# Glass ball
scene.add(Sphere(center=ti.Vector([0.7, 0, -0.5]), radius=0.5, material=3, color=ti.Vector([1.0, 1.0, 1.0])))
# Metal ball-2
scene.add(Sphere(center=ti.Vector([0.6, -0.3, -2.0]), radius=0.2, material=2, color=ti.Vector([0.8, 0.6, 0.2])))

while gui.running:
    for e in gui.get_events(ti.GUI.PRESS, ti.GUI.MOTION, ti.GUI.RELEASE):
        if e.type == ti.GUI.PRESS:
            if e.key == ti.GUI.LMB:
                is_dragging = True
                start_mouse_x, start_mouse_y = gui.get_cursor_pos()
                camera.set_lookat(1.0, 1.0, -1.0)
        elif e.type == ti.GUI.RELEASE:
            if e.key == ti.GUI.LMB:
                is_dragging = False
                stop_mouse_x, stop_mouse_y = gui.get_cursor_pos()
                camera.set_lookat(0, 1.0, -1.0)

    mouse_x, mouse_y = gui.get_cursor_pos()
    if (is_dragging):
        dragging_mouse_x, dragging_mouse_y = (mouse_x - start_mouse_x, mouse_y - start_mouse_y)
    gui.text(
    content=f'Mouse_x, mouse_y = {mouse_x:.2f}, {mouse_y:.2f}', pos=(0.6, 0.95), color=0xFFFFFF)
    gui.text(
    content=f'start_x, start_y = {start_mouse_x:.2f}, {start_mouse_y:.2f}', pos=(0.6, 0.9), color=0xFFFFFF)
    gui.text(
    content=f'dragging_x, dragging_y = {dragging_mouse_x:.2f}, {dragging_mouse_y:.2f}', pos=(0.6, 0.85), color=0xFFFFFF)
    gui.text(
    content=f'stop_x, stop_y = {stop_mouse_x:.2f}, {stop_mouse_y:.2f}', pos=(0.6, 0.8), color=0xFFFFFF)

    update_camera()
    gui.set_image(screen)
    gui.show()
