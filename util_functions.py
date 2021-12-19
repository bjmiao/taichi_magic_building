import taichi as ti

def get_rotation(x1, y1, x2, y2):
    radius = 0.5 # the screen axis is [0, 1], radius = 0.5
    center_x, center_y = 0.5, 0.5
    x1 = (x1 - center_x) / radius
    x2 = (x2 - center_x) / radius
    y1 = (y1 - center_y) / radius
    y2 = (y2 - center_y) / radius
    z1, z2 = 0, 0
    r1 = x1 * x1 + y1 * y1
    if r1 > 1.0:
        s = 1.0 / ti.sqrt(r1)
        x1 *= s
        y1 *= s
        z1 = 0
    else:
        z1 = ti.sqrt(1.0 - r1)
    r2 = x2 * x2 + y2 * y2
    if r2 > 1.0:
        s = 1.0 / ti.sqrt(r2)
        x2 *= s
        y2 *= s
        z2 = 0
    else:
        z2 = ti.sqrt(1.0 - r2)
    p1 = ti.Vector([x1, y1, z1])
    p2 = ti.Vector([x2, y2, z2])
    rotation_theta = ti.acos(p1.dot(p2))
    rotation_axis = p1.cross(p2)
    if rotation_axis.norm() > 1e-2:
        rotation_axis = rotation_axis.normalized()
    else:
        rotation_theta = 0 # do not rotate
    print(rotation_theta, rotation_axis)
    return rotation_theta, rotation_axis
    # return (x1, y1, z1), (x2, y2, z2)


class Quaternion:
    def __init__(self, theta, x, y, z):
        self.w = ti.sin(theta)
        cos_theta = ti.cos(theta)
        self.x = cos_theta * x
        self.y = cos_theta * y
        self.z = cos_theta * z
    def __str__(self):
        return f"({self.w:.2f} {self.x:.2f} {self.y:.2f} {self.z:.2f})"
 
    def prod(self, rhs):
        w = self.w * rhs.w - self.x * rhs.x - self.y * rhs.y - self.z * rhs.z
        x = self.w * rhs.x + self.x * rhs.w + self.y * rhs.z - self.z * rhs.y
        y = self.w * rhs.y - self.x * rhs.z + self.y * rhs.w + self.z * rhs.x
        z = self.w * rhs.z + self.x * rhs.y - self.y * rhs.x + self.z * rhs.w
        return Quaternion(w, x, y, z)

    def norm(self):
        return self.w * self.w + self.x * self.x + self.y * self.y + self.z * self.z 

    def get_elements(self):
        return self.x, self.y, self.z
    # @classmethod
    # def multiply(i: Quaternion, j: Quaternion):
    #     pass

def get_direction_after_rotation(old_dir, theta, axis):
    print(axis)
    axis_x, axis_y, axis_z = axis
    old_x, old_y, old_z = old_dir
    q = Quaternion(theta / 2, axis_x, axis_y, axis_z)
    p = Quaternion(0, old_x, old_y, old_z)
    q_inverse = Quaternion(-theta/2, axis_x, axis_y, axis_z)
    print("===")
    print(q)
    print(p)
    print(q_inverse)
    new_dir_quad = q.prod(p).prod(q_inverse)
    print(new_dir_quad)
    new_dir = new_dir_quad.get_elements()
    new_dir = ti.Vector(new_dir).normalized()
    return new_dir
