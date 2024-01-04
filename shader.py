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

class Shader:
    ID: None
    def __init__(self, vertex_filename: str, fragment_filename: str):
        # Request a program and shader slots from GPU
        self.ID  = glCreateProgram()
        with open(vertex_filename, 'r') as file:
            vertex_code = file.read()
        
        with open(fragment_filename, 'r') as file:
            fragment_code = file.read()

        vertex   = glCreateShader(GL_VERTEX_SHADER)
        fragment = glCreateShader(GL_FRAGMENT_SHADER)

        # Set shaders source
        glShaderSource(vertex, vertex_code)
        glShaderSource(fragment, fragment_code)

        self.compile_shader(vertex)
        self.compile_shader(fragment)

        # Attach shader objects to the program
        glAttachShader(self.ID, vertex)
        glAttachShader(self.ID, fragment)

        # Build program
        glLinkProgram(self.ID)
        if not glGetProgramiv(self.ID, GL_LINK_STATUS):
            logger.error(glGetProgramInfoLog(self.ID))
            raise RuntimeError('Linking error')
    
    def use(self):
        glUseProgram(self.ID)

    @staticmethod
    def compile_shader(shader):
        # Compile shaders
        glCompileShader(shader)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(shader).decode()
            print(error)
            raise RuntimeError("Erro de compilacao do Shader")

    def set_mat4(self, name: str, matrix, gl_bool = GL_TRUE):
        loc = glGetUniformLocation(self.ID, name)
        glUniformMatrix4fv(loc, 1, gl_bool, matrix)

    def set_3float(self, name: str, x, y, z):
        loc = glGetUniformLocation(self.ID, name)
        glUniform3f(loc, x, y, z)

    def set_1float(self, name: str, x):
        loc = glGetUniformLocation(self.ID, name) # recuperando localizacao da variavel ka na GPU
        glUniform1f(loc, x)

    def set_1int(self, name: str, x):
        loc = glGetUniformLocation(self.ID, name) # recuperando localizacao da variavel ka na GPU
        glUniform1i(loc, x)


    

