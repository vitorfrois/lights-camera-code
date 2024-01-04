import math 
import glfw
import OpenGL.GL.shaders
import math
import logging
import glm

import numpy as np

from OpenGL.GL import *
from globject import GLObject
from objhelper import ObjHelper
from logger_helper import LoggerHelper
from matrix import Matrix
from skybox import Skybox
from shader import Shader

logger = LoggerHelper.get_logger(__name__)
offset = ctypes.c_void_p(0)


class Environment:
    window: None
    program: None
    loc: None
    texture_loc: None
    normal_loc: None
    buffer: None
    total_vertices: int
    n_objects: int
    obj_list: list[GLObject]
    list_vertices: list
    list_texture: list
    skybox_obj: GLObject

    def __init__(self, x=600, y=480):
        self.n_objects = 0
        self.total_vertices = 0
        self.obj_list = []
        self.list_vertices = []
        self.list_texture = []
        self.list_normals = []

        glfw.init()
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE);
        self.window = glfw.create_window(x, y, "Trabalho 2", None, None)
        glfw.make_context_current(self.window)
        
        # Request a program and shader slots from GPU
        self.skybox_shader = Shader('shaders/skybox_shader_vs', 'shaders/skybox_shader_fs')
        self.skybox_shader.use()
        self.skybox_shader.set_1int("skybox", 0)
    
        self.main_shader = Shader('shaders/main_shader_vs', 'shaders/main_shader_fs')
        self.main_shader.use()

        # Init textures
        glEnable(GL_TEXTURE_2D)
        qtd_texturas = 2
        # textures = glGenTextures(qtd_texturas)

        # Request a buffer slot from GPU
        self.buffer = glGenBuffers(5)
        self.buffer_counter = 0
        # Make this buffer the default one

        self.loc = glGetAttribLocation(self.main_shader.ID, "position")
        glEnableVertexAttribArray(self.loc)

        self.texture_loc = glGetAttribLocation(self.main_shader.ID, "texture_coord")
        glEnableVertexAttribArray(self.texture_loc)

        self.normal_loc = glGetAttribLocation(self.main_shader.ID, "normals")
        glEnableVertexAttribArray(self.normal_loc)

        loc_ka = glGetUniformLocation(self.main_shader.ID, "ka") # recuperando localizacao da variavel ka na GPU
        glUniform1f(loc_ka, 0.5) ### envia ka pra gpu
        
        loc_kd = glGetUniformLocation(self.main_shader.ID, "kd") # recuperando localizacao da variavel ka na GPU
        glUniform1f(loc_kd, 0.5) ### envia kd pra gpu 

        loc_light_pos = glGetUniformLocation(self.main_shader.ID, "lightPos") # recuperando localizacao da variavel lightPos na GPU
        glUniform3f(loc_light_pos, -1.5, 1.7, 2.5) ### posicao da fonte de luz

        glEnable(GL_DEPTH_TEST) 
        
        self.show_window()
        
    @staticmethod
    def compile_shader(shader):
        # Compile shaders
        glCompileShader(shader)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(shader).decode()
            print(error)
            raise RuntimeError("Erro de compilacao do Shader")

    def get_window(self):
        return self.window

    def get_program(self):
        return self.main_shader.ID

    def get_loc(self):
        return self.loc

    def get_texture_loc(self):
        return self.texture_loc

    def get_normal_loc(self):
        return self.normal_loc

    def get_list_objects(self) -> list[GLObject]: 
        return self.obj_list

    def get_vertices(self):
        return self.list_vertices

    def get_texture(self):
        return self.list_texture

    def get_total_vertices(self):
        return self.total_vertices

    def set_key_callback(self, key_event_function):
        glfw.set_key_callback(self.window, key_event_function)

    def set_mouse_callback(self, key_event_function):
        glfw.set_cursor_pos_callback(self.window, key_event_function)

    def show_window(self):
        glfw.show_window(self.window)

    def add_skybox(self, obj: Skybox):
        obj.start = self.total_vertices

        for v in obj.vertices['position']:
            self.list_vertices.append(v)

        logger.info(f'{obj.start}, {obj.n_vertices}')
        
        self.skybox_obj = obj
        self.total_vertices += obj.n_vertices
        self.n_objects += 1

    def add_object(self, obj: GLObject):
        obj.start = self.total_vertices

        for v in obj.vertices['position']:
            self.list_vertices.append(v)

        for t in obj.texture['position']:
            self.list_texture.append(t)
            
        for n in obj.normals['position']:
            self.list_normals.append(n)

        # loc = self.get_loc()
        # center_obj_mat = obj.center_obj()
        # glUniformMatrix4fv(loc, 1, GL_TRUE, center_obj_mat)
        logger.info(f'{obj.start}, {obj.n_vertices}')
        
        self.obj_list.append(obj)
        self.total_vertices += obj.n_vertices
        self.n_objects += 1

    def send_vertices(self):
        vertices = np.zeros(self.total_vertices, [("position", np.float32, 3)])
        vertices['position'] = self.list_vertices

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer[0])
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        stride = vertices.strides[0]

        loc = self.get_loc()
        glEnableVertexAttribArray(loc)
        glVertexAttribPointer(loc, 3, GL_FLOAT, False, stride, offset)

    def send_texture(self):
        texture = np.zeros(len(self.list_texture), [("position", np.float32, 2)])
        texture['position'] = self.list_texture

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer[1])
        glBufferData(GL_ARRAY_BUFFER, texture.nbytes, texture, GL_STATIC_DRAW)
        stride = texture.strides[0]    

        texture_loc = self.get_texture_loc()
        glVertexAttribPointer(texture_loc, 2, GL_FLOAT, False, stride, offset)
        glEnableVertexAttribArray(texture_loc)

    def send_normals(self):
        normals = np.zeros(len(self.list_normals), [("position", np.float32, 3)]) # três coordenadas
        normals['position'] = self.list_normals

        # Upload coordenadas normals de cada vertice
        glBindBuffer(GL_ARRAY_BUFFER, buffer[2])
        glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)
        stride = normals.strides[0]

        normal_loc = self.get_normal_loc()
        glVertexAttribPointer(normal_loc, 3, GL_FLOAT, False, stride, offset)
        glEnableVertexAttribArray(normal_loc)

   