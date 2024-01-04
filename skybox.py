import math
import glfw
import OpenGL.GL.shaders
import numpy as np
import logging

from dataclasses import dataclass
from OpenGL.GL import *
from matrix import Matrix
from logger_helper import LoggerHelper
from globject import GLObject
from PIL import Image

SKYBOX_VERTICES = [
    ['-1.0',  '1.0', '-1.0'],
    ['-1.0', '-1.0', '-1.0'],
    [ '1.0', '-1.0', '-1.0'],
    [ '1.0', '-1.0', '-1.0'],
    [ '1.0',  '1.0', '-1.0'],
    ['-1.0',  '1.0', '-1.0'],
    ['-1.0', '-1.0',  '1.0'],
    ['-1.0', '-1.0', '-1.0'],
    ['-1.0',  '1.0', '-1.0'],
    ['-1.0',  '1.0', '-1.0'],
    ['-1.0',  '1.0',  '1.0'],
    ['-1.0', '-1.0',  '1.0'],   
    [ '1.0', '-1.0', '-1.0'],
    [ '1.0', '-1.0',  '1.0'],
    [ '1.0',  '1.0',  '1.0'],
    [ '1.0',  '1.0',  '1.0'],
    [ '1.0',  '1.0', '-1.0'],
    [ '1.0', '-1.0', '-1.0'],
    ['-1.0', '-1.0',  '1.0'],
    ['-1.0',  '1.0',  '1.0'],
    [ '1.0',  '1.0',  '1.0'],
    [ '1.0',  '1.0',  '1.0'],
    [ '1.0', '-1.0',  '1.0'],
    ['-1.0', '-1.0',  '1.0'],
    ['-1.0',  '1.0', '-1.0'],
    [ '1.0',  '1.0', '-1.0'],
    [ '1.0',  '1.0',  '1.0'],
    [ '1.0',  '1.0',  '1.0'],
    ['-1.0',  '1.0',  '1.0'],
    ['-1.0',  '1.0', '-1.0'],
    ['-1.0', '-1.0', '-1.0'],
    ['-1.0', '-1.0',  '1.0'],
    [ '1.0', '-1.0', '-1.0'],
    [ '1.0', '-1.0', '-1.0'],
    ['-1.0', '-1.0',  '1.0'],
    [ '1.0', '-1.0',  '1.0']
]


class Skybox(GLObject):
    vertices: list
    texture: list

    def __init__(self, name):
        super().__init__(name)

    def init_obj(self, directory: str):
        """
        Files in directory should be named as
        right.jpg
        left.jpg
        top.jpg
        bottom.jpg
        back.jpg
        front.jpg
        """

        self.number = glGenTextures(1);
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.number);

        self.init_vertices(SKYBOX_VERTICES)
        self.n_vertices = len(SKYBOX_VERTICES)

        cube_images_filename_list = [
            "left.jpg",
            "right.jpg",
            "top.jpg",
            "bottom.jpg",
            "back.jpg",
            "front.jpg"
        ]

        for i in range(6):
            filename = cube_images_filename_list[i]
            file_path = f"resources/{directory}/{filename}"
        
            img = Image.open(file_path)
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            # img = img.transpose(Image.FLIP_LEFT_RIGHT)

            img_width = img.size[0]
            img_height = img.size[1]
            img_format = GL_RGB if img.mode == "RGB" else GL_RGBA
            image_data = img.tobytes("raw", "RGB", 0, -1)
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB, img_width, img_height, 0, img_format, GL_UNSIGNED_BYTE, image_data)
            # print(img)
            
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)  

    def draw_obj(self, program):
        glDepthFunc(GL_LEQUAL)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.number)
        glDrawArrays(GL_TRIANGLES, self.start, self.n_vertices) ## renderizando
        glBindVertexArray(0)
        glDepthFunc(GL_LESS)