import taichi as ti
class Rotation:
    def __init__(self, u, v, w, omega = 0.01):
        """ u: left to screen
            v: up to the screen
            w: my eye to screen center
            omega: angular velocity in theta per timestamp """
        self.u_init = u
        self.v_init = v
        self.w_init = w

        self.u = u
        self.v = v
        self.w = w
        self.omega = omega

    def reset(self):
        self.u = self.u_init
        self.v = self.v_init
        self.w = self.w_init

    @staticmethod
    def _rotate_matrix(axis: ti.Vector, theta):
        cos_theta = ti.cos(theta)
        sin_theta = ti.sin(theta)

        R = ti.Matrix([[
            cos_theta + axis[0] * axis[0] * (1 - cos_theta),
            axis[0] * axis[1] * (1 - cos_theta) - axis[2] * sin_theta,
            axis[0] * axis[2] * (1 - cos_theta) + axis[1] * sin_theta
          ], [
            axis[1] * axis[0] * (1 - cos_theta) + axis[2] * sin_theta,
            cos_theta + axis[1] * axis[1] * (1 - cos_theta),
            axis[1] * axis[2] * (1 - cos_theta) - axis[0] * sin_theta
          ], [
            axis[2] * axis[0] * (1 - cos_theta) - axis[1] * sin_theta,
            axis[2] * axis[1] * (1 - cos_theta) + axis[0] * sin_theta,
            cos_theta + axis[2] * axis[2] * (1 - cos_theta)
          ]
        ])
        return R
    def rotate(self, direction = ti.Vector([0, 0, 0])):
        # direction: [-1/0/1, -1/0/1, -1/0/1]
        # first dim: rotate along u
        # second dim: rotate along v
        # third dim: rotate along w
        if direction[0] == -1:
            R = Rotation._rotate_matrix(self.u, -self.omega)
            self.v = R @ self.v
            self.w = R @ self.w
        elif direction[0] == 1:
            R = Rotation._rotate_matrix(self.u, self.omega)
            self.v = R @ self.v
            self.w = R @ self.w

        if direction[1] == -1:
            R = Rotation._rotate_matrix(self.v, -self.omega)
            self.u = R @ self.u
            self.w = R @ self.w
        elif direction[1] == 1:
            R = Rotation._rotate_matrix(self.v, self.omega)
            self.u = R @ self.u
            self.w = R @ self.w

        if direction[2] == -1:
            R = Rotation._rotate_matrix(self.w, -self.omega)
            self.u = R @ self.u
            self.v = R @ self.v
        elif direction[2] == 1:
            R = Rotation._rotate_matrix(self.w, self.omega)
            self.u = R @ self.u
            self.v = R @ self.v
        return