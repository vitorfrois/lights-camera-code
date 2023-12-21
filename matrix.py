import numpy as np
import math
import glm

def get_trigonometric(angle):
    c = math.cos( math.radians(angle) )
    s = math.sin( math.radians(angle) )
    return s, c

class Matrix:
    @staticmethod
    def get_identity():
        identity_matrix = np.array([  1.0, 0.0, 0.0, 0.0, 
                                    0.0, 1.0, 0.0, 0.0, 
                                    0.0, 0.0, 1.0, 0.0, 
                                    0.0, 0.0, 0.0, 1.0], np.float32)
        return identity_matrix

    @staticmethod
    def get_x_inplace_rotation(center, angle):
        s, c = get_trigonometric(angle)

        center_matrix = Matrix.get_translation(-center[0], -center[1])
        back_matrix = Matrix.get_translation(center[0], center[1])

        x_rotation_matrix = np.array([  1 , 0.0, 0, 0.0, 
                                    0  , c  , -s, 0.0, 
                                    0, s, c, 0.0, 
                                    0.0, 0.0, 0.0, 1.0], np.float32)
        return Matrix.multiply(back_matrix, x_rotation_matrix, center_matrix)

    @staticmethod
    def get_x_rotation(center, angle):
        s, c = get_trigonometric(angle)

        x_rotation_matrix = np.array([  1 , 0.0, 0, 0.0, 
                                    0  , c  , -s, 0.0, 
                                    0, s, c, 0.0, 
                                    0.0, 0.0, 0.0, 1.0], np.float32)
        return x_rotation_matrix
    
    @staticmethod
    def get_y_inplace_rotation(center, angle):
        s, c = get_trigonometric(angle)

        center_matrix = Matrix.get_translation(-center[0], -center[1])
        back_matrix = Matrix.get_translation(center[0], center[1])

        y_rotation_matrix = np.array([  c  , 0.0, s, 0.0, 
                                    0  , 1  , 0.0, 0.0, 
                                    -s, 0.0, c, 0.0, 
                                    0.0, 0.0, 0.0, 1.0], np.float32)

        return Matrix.multiply(back_matrix, y_rotation_matrix, center_matrix)

    @staticmethod
    def get_y_rotation(center, angle):
        s, c = get_trigonometric(angle)

        y_rotation_matrix = np.array([  c  , 0.0, s, 0.0, 
                                    0  , 1  , 0.0, 0.0, 
                                    -s, 0.0, c, 0.0, 
                                    0.0, 0.0, 0.0, 1.0], np.float32)

        return y_rotation_matrix

    @staticmethod
    def get_z_inplace_rotation(center, angle):
        s, c = get_trigonometric(angle)

        center_matrix = Matrix.get_translation(-center[0], -center[1])
        back_matrix = Matrix.get_translation(center[0], center[1])
        
        z_rotation_matrix = np.array([  c  , -s, 0.0, 0.0, 
                                    s  , c  , 0.0, 0.0, 
                                    0.0, 0.0, 1, 0.0, 
                                    0.0, 0.0, 0.0, 1.0], np.float32)
        return Matrix.multiply(back_matrix, z_rotation_matrix, center_matrix)

    @staticmethod
    def get_z_rotation(center, angle):
        s, c = get_trigonometric(angle)

        z_rotation_matrix = np.array([  c  , -s, 0.0, 0.0, 
                                    s  , c  , 0.0, 0.0, 
                                    0.0, 0.0, 1, 0.0, 
                                    0.0, 0.0, 0.0, 1.0], np.float32)
        return z_rotation_matrix
    
    @staticmethod
    def get_scale(center, x_factor, y_factor = None, z_factor = None):
        if y_factor == None:
            y_factor = x_factor
        if z_factor == None:
            z_factor = x_factor

        center_matrix = Matrix.get_translation(-center[0], -center[1])
        back_matrix = Matrix.get_translation(center[0], center[1])

        scale_matrix =    np.array([  x_factor  , 0.0 , 0.0, 0.0, 
                                    0.0  , y_factor  , 0.0, 0.0, 
                                    0.0, 0.0, x_factor, 0.0, 
                                    0.0, 0.0, 0.0, 1.0], np.float32)
        return Matrix.multiply(back_matrix, scale_matrix, center_matrix)
    
    @staticmethod
    def get_translation(x_factor, y_factor, z_factor = 0):
        translation_matrix = np.array([  1.0, 0.0, 0.0, x_factor, 
                                    0.0, 1.0, 0.0, y_factor, 
                                    0.0, 0.0, 1.0, z_factor, 
                                    0.0, 0.0, 0.0, 1.0], np.float32)
        return translation_matrix

    @staticmethod
    def _multiply2(a, b):
        m_a = a.reshape(4,4)
        m_b = b.reshape(4,4)
        m_c = np.dot(m_a,m_b)
        c = m_c.reshape(1,16)
        return c

    @staticmethod
    def multiply(*matrices):
        result = Matrix.get_identity()
        for matrix in matrices:
            result = Matrix._multiply2(result, matrix)

        return result

    @staticmethod
    def transform_vertex(matrix, vertex):
        v = vertex
        v = np.append(v, 1)

        # print(f'new vertex: {v}')
        v = matrix @ v
        return v[:2]

    @staticmethod
    def model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z):
        angle = math.radians(angle)

        matrix_transform = glm.mat4(1.0) # instanciando uma matriz identidade
        # aplicando rotacao
        matrix_transform = glm.rotate(matrix_transform, angle, glm.vec3(r_x, r_y, r_z))
        # aplicando translacao
        matrix_transform = glm.translate(matrix_transform, glm.vec3(t_x, t_y, t_z))    
        # aplicando escala
        matrix_transform = glm.scale(matrix_transform, glm.vec3(s_x, s_y, s_z))
        matrix_transform = np.array(matrix_transform).T # pegando a transposta da matriz (glm trabalha com ela invertida)

        return matrix_transform

    @staticmethod
    def view(cameraPos, cameraFront, cameraUp):
        mat_view = glm.lookAt(cameraPos, cameraPos + cameraFront, cameraUp);
        mat_view = np.array(mat_view)
        return mat_view

    @staticmethod
    def projection(altura, largura):
        # perspective parameters: fovy, aspect, near, far
        mat_projection = glm.perspective(glm.radians(45.0), largura/altura, 0.1, 1000.0)
        mat_projection = np.array(mat_projection)    
        return mat_projection