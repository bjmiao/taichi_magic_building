import taichi as ti

PI = 3.14159265359

@ti.data_oriented
class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction
    def at(self, t):
        return self.origin + t * self.direction

# @ti.func
# def area_triangle(pointA, pointB, pointC):
#     s1 = pointB - pointA
#     s2 = pointC - pointA
#     return 0.5 * s1.cross(s2).norm()

@ti.data_oriented
class QuadranglePlane:
    # def __init__(self, color):
    def __init__(self, pointA, pointB, pointC, pointD, color):
        self.pointA = pointA
        self.pointB = pointB
        self.pointC = pointC
        self.pointD = pointD
        print(pointA, pointB, pointC, pointD)
        self.color = color
        self.material = 0 # not used yet
        self.norm_direction = (self.pointA - self.pointC).cross(self.pointB - self.pointD).normalized()
        self.D = -self.pointA.dot(self.norm_direction)

    @ti.func
    def hit(self, ray, t_min = 0.001, t_max = 10e8):
        is_hit = False
        front_face = False
        root = 0.0
        hit_point =  ti.Vector([0.0, 0.0, 0.0])
        hit_point_normal = self.norm_direction
        # print(f"{ray.direction=}, {ray.origin=}")
        if ti.abs(ray.direction.dot(self.norm_direction)) < 1e-5:
            # print("Ray Perpendicular to plane. Not hit")
            is_hit = False
        else:
            root = (self.pointA - ray.origin).dot(self.norm_direction) / ray.direction.dot(self.norm_direction)
            # print(f"{root=}")
            if (root < 0):
                # print("Not hit")
                is_hit = False
            else:
                hit_point = ray.origin + root * ray.direction
                # print(f"Intersection: {hit_point=}")
                # check whether P is in this quadrangle
                area_q1 = 0.5 * (self.pointB - self.pointA).cross(self.pointC - self.pointA).norm()
                area_q2 = 0.5 * (self.pointB - self.pointD).cross(self.pointC - self.pointD).norm()
                area_t1 = 0.5 * (self.pointA - hit_point).cross(self.pointB - hit_point).norm()
                area_t2 = 0.5 * (self.pointB - hit_point).cross(self.pointC - hit_point).norm()
                area_t3 = 0.5 * (self.pointC - hit_point).cross(self.pointD - hit_point).norm()
                area_t4 = 0.5 * (self.pointD - hit_point).cross(self.pointA - hit_point).norm()
                # area_q1 = area_triangle(self.pointA, self.pointB, self.pointC)
                # area_q2 = area_triangle(self.pointD, self.pointB, self.pointC)
                # # print(f"{area_q1=}, {area_q2=}")
                # area_t1 = area_triangle(hit_point, self.pointA, self.pointB)
                # area_t2 = area_triangle(hit_point, self.pointB, self.pointC)
                # area_t3 = area_triangle(hit_point, self.pointC, self.pointD)
                # area_t4 = area_triangle(hit_point, self.pointD, self.pointA)
                # # print(f"{area_t1=}, {area_t2=}, {area_t3=}, {area_t4=}")
                if abs(area_t1 + area_t2 + area_t3 + area_t4 - area_q1 - area_q2) < 1e-3:
                    # print("Hit")
                    is_hit = True
                else:
                    # print("No hit")
                    is_hit = False
        return is_hit, root, hit_point, hit_point_normal, front_face, self.material, self.color


@ti.data_oriented
class Cube:
    def __init__(self, origin, length):
        self.origin = origin # most left, down, near point
        self.length = length
        # Z axis
        # |   ____
        # | /    /|  /-- Y axis
        # |/ U  / | /
        # |----/ R|/
        # |    |  /
        # | F  | /
        # --------------X axis
        # ↑ Origin
        point_LFD = origin
        point_RFD = origin + ti.Vector([length, 0.0, 0.0])
        point_LBD = origin + ti.Vector([0.0, length, 0.0])
        point_RBD = origin + ti.Vector([length, length, 0.0])
        point_LFU = origin + ti.Vector([0.0, 0.0, length])
        point_RFU = origin + ti.Vector([length, 0.0, length])
        point_LBU = origin + ti.Vector([0.0, length, length])
        point_RBU = origin + ti.Vector([length, length, length])
        plain_list = []
        # Front
        plain_list.append(QuadranglePlane(
                point_LFD, point_LFU, point_RFU, point_RFD, color = ti.Vector([1.0, 0.0, 0.0])
        ))
        # Back
        plain_list.append(QuadranglePlane(
                point_LBD, point_LBU, point_RBU, point_RBD, color = ti.Vector([0.0, 1.0, 0.0])
        ))
        # Left
        plain_list.append(QuadranglePlane(
            point_LBD, point_LFD, point_LFU, point_LBU, color = ti.Vector([0.0, 0.0, 1.0])
        ))
        # right
        plain_list.append(QuadranglePlane(
            point_RBD, point_RFD, point_RFU, point_RBU, color = ti.Vector([0.0, 1.0, 1.0])
        ))
        # Up
        plain_list.append(QuadranglePlane(
            point_LBU, point_RBU, point_RFU, point_LFU, color = ti.Vector([1.0, 1.0, 0.0])
        ))
        # Down
        plain_list.append(QuadranglePlane(
            point_LBD, point_RBD, point_RFD, point_LFD, color = ti.Vector([1.0, 0.0, 1.0])
        ))
        self.plain_list = plain_list

    @ti.func
    def hit(self, ray, t_min = 0.001, t_max = 10e8):
        is_hit = False
        min_root = t_max
        final_hit_point = ti.Vector([0.0, 0.0, 0.0])
        final_hit_point_normal = ti.Vector([0.0, 0.0, 0.0])
        final_front_face = False
        final_material = 0
        final_color = ti.Vector([0.0, 0.0, 0.0])
        for index in ti.static(range(len(self.plain_list))):
            this_is_hit, root, hit_point, hit_point_normal, front_face, material, color = self.plain_list[index].hit(ray, t_min, t_max)
            # print("BBB", this_is_hit, root, hit_point, hit_point_normal, front_face, material, color)
            if this_is_hit:
                is_hit = True
                if (root < min_root):
                    min_root = root
                    final_hit_point = hit_point
                    final_hit_point_normal = hit_point_normal
                    final_front_face = front_face
                    final_material = material
                    final_color = color
        # print("AAA", is_hit, min_root, final_hit_point, final_hit_point_normal, final_front_face, final_material, final_color)
        return is_hit, min_root, final_hit_point, final_hit_point_normal, final_front_face, final_material, final_color

@ti.data_oriented
class Sphere:
    def __init__(self, center, radius, material, color):
        self.center = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.center[None] = center
        self.radius = radius
        self.material = material
        self.color = color
    def set_center(self, center):
        self.center[None] = center
        print("set center")

    @ti.func
    def hit(self, ray, t_min=0.001, t_max=10e8):
        oc = ray.origin - self.center[None]
        a = ray.direction.dot(ray.direction)
        b = 2.0 * oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius
        discriminant = b * b - 4 * a * c
        is_hit = False
        front_face = False
        root = 0.0
        hit_point =  ti.Vector([0.0, 0.0, 0.0])
        hit_point_normal = ti.Vector([0.0, 0.0, 0.0])
        if discriminant > 0:
            sqrtd = ti.sqrt(discriminant)
            root = (-b - sqrtd) / (2 * a)
            if root < t_min or root > t_max:
                root = (-b + sqrtd) / (2 * a)
                if root >= t_min and root <= t_max:
                    is_hit = True
            else:
                is_hit = True
        if is_hit:
            hit_point = ray.at(root)
            hit_point_normal = (hit_point - self.center[None]) / self.radius
            # Check which side does the ray hit, we set the hit point normals always point outward from the surface
            if ray.direction.dot(hit_point_normal) < 0:
                front_face = True
            else:
                hit_point_normal = -hit_point_normal
        return is_hit, root, hit_point, hit_point_normal, front_face, self.material, self.color
@ti.data_oriented
class Hittable_list:
    def __init__(self):
        self.objects = []
        self.walls = []
        self.foods = []
    def add_food(self, obj):
        self.foods.append(obj)
        self.objects = self.foods + self.walls
        print("add_food", self.objects)
    def add_wall(self, obj):
        self.walls.append(obj)
        self.objects = self.foods + self.walls
    # def add(self, obj):
    #     self.objects.append(obj)
    def reset_food(self):
        self.foods = []
        self.objects = self.foods + self.walls
        print("clear_food", self.objects)

    @ti.func
    def hit(self, ray, t_min=0.001, t_max=10e8):
        closest_t = t_max
        is_hit = False
        front_face = False
        hit_point = ti.Vector([0.0, 0.0, 0.0])
        hit_point_normal = ti.Vector([0.0, 0.0, 0.0])
        color = ti.Vector([0.0, 0.0, 0.0])
        material = 1
        for index in ti.static(range(len(self.objects))):
            is_hit_tmp, root_tmp, hit_point_tmp, hit_point_normal_tmp, front_face_tmp, material_tmp, color_tmp =  self.objects[index].hit(ray, t_min, closest_t)
            if is_hit_tmp and root_tmp < closest_t:
                closest_t = root_tmp
                is_hit = is_hit_tmp
                hit_point = hit_point_tmp
                hit_point_normal = hit_point_normal_tmp
                front_face = front_face_tmp
                material = material_tmp
                color = color_tmp
        return is_hit, closest_t, hit_point, hit_point_normal, front_face, material, color

    @ti.func
    def hit_shadow(self, ray, t_min=0.001, t_max=10e8):
        is_hit_source = False
        is_hit_source_temp = False
        hitted_dielectric_num = 0
        is_hitted_non_dielectric = False
        # Compute the t_max to light source
        is_hit_tmp, root_light_source, hit_point_tmp, hit_point_normal_tmp, front_face_tmp, material_tmp, color_tmp = \
        self.objects[0].hit(ray, t_min)
        for index in ti.static(range(len(self.objects))):
            is_hit_tmp, root_tmp, hit_point_tmp, hit_point_normal_tmp, front_face_tmp, material_tmp, color_tmp =  self.objects[index].hit(ray, t_min, root_light_source)
            if is_hit_tmp:
                if material_tmp != 3 and material_tmp != 0:
                    is_hitted_non_dielectric = True
                if material_tmp == 3:
                    hitted_dielectric_num += 1
                if material_tmp == 0:
                    is_hit_source_temp = True
        if is_hit_source_temp and (not is_hitted_non_dielectric) and hitted_dielectric_num == 0:
            is_hit_source = True
        return is_hit_source, hitted_dielectric_num, is_hitted_non_dielectric


@ti.data_oriented
class Camera:
    def __init__(self, fov=60, aspect_ratio = 1.0):
        self.lookfrom = ti.Vector.field(3, dtype=ti.f32, shape=())
        # self.lookat = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.vup = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.vdown = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.w = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.v = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.u = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.fov = fov
        self.aspect_ratio = aspect_ratio

        self.cam_lower_left_corner = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.cam_horizontal = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.cam_vertical = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.cam_origin = ti.Vector.field(3, dtype=ti.f32, shape=())
        self.reset()
    @ti.kernel
    def reset(self):
        self.vup[None] = [0.0, 1.0, 0.0] # TODO: seems unnecessary?

        self.lookfrom[None] = [0.0, 0.0, 0.0]
        self.u[None] = [-1.0, 0.0, 0.0]
        self.v[None] = [0.0, 1.0, 0.0]
        # self.w[None] = [0.0, -0.6, 0.8]
        self.w[None] = [0.0, 0.0, -1.0]

        # self.w[None] = (self.lookfrom[None] - self.lookat[None]).normalized()
        self.calculate_parameter()

    @ti.kernel
    def set_direction_w(self, w1:ti.f32, w2:ti.f32, w3:ti.f32, need_calculate_parameter: ti.i8):
        self.w[None] = ti.Vector([w1, w2, w3])
        if (need_calculate_parameter == 1):
            self.calculate_parameter()

    @ti.kernel
    def set_direction_u(self, u1:ti.f32, u2:ti.f32, u3:ti.f32, need_calculate_parameter: ti.i8):
        self.u[None] = ti.Vector([u1, u2, u3])
        if (need_calculate_parameter == 1):
            self.calculate_parameter()

    @ti.kernel
    def set_direction_v(self, v1:ti.f32, v2:ti.f32, v3:ti.f32, need_calculate_parameter: ti.i8):
        self.v[None] = ti.Vector([v1, v2, v3])
        if (need_calculate_parameter == 1):
            self.calculate_parameter()

    @ti.kernel
    def set_lookfrom(self, x:ti.f32, y:ti.f32, z:ti.f32):
        self.lookfrom[None] = [x, y, z]
        self.calculate_parameter()

    @ti.func
    def calculate_parameter(self):
        # print("====")
        # print(self.u[None])
        # print(self.v[None])
        # print(self.w[None])
        theta = self.fov * (PI / 180.0)
        half_height = ti.tan(theta / 2.0)
        half_width = self.aspect_ratio * half_height
        self.cam_origin[None] = self.lookfrom[None]
        self.cam_lower_left_corner[None] = ti.Vector([-half_width, -half_height, -1.0])
        self.cam_lower_left_corner[
            None] = self.cam_origin[None] - half_width * self.u[None] - half_height * self.v[None] - self.w[None]
        self.cam_horizontal[None] = 2 * half_width * self.u[None]
        self.cam_vertical[None] = 2 * half_height * self.v[None]

    @ti.func
    def get_ray(self, u, v):
        return Ray(self.cam_origin[None], self.cam_lower_left_corner[None] + u * self.cam_horizontal[None] + v * self.cam_vertical[None] - self.cam_origin[None])