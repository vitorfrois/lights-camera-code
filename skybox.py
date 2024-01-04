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
     ['1.0', '-1.0', '-1.0'],
     ['1.0', '-1.0', '-1.0'],
     ['1.0',  '1.0', '-1.0'],
    ['-1.0',  '1.0', '-1.0'],
    ['-1.0', '-1.0',  '1.0'],
    ['-1.0', '-1.0', '-1.0'],
    ['-1.0',  '1.0', '-1.0'],
    ['-1.0',  '1.0', '-1.0'],
    ['-1.0',  '1.0',  '1.0'],
    ['-1.0', '-1.0',  '1.0'],   
     ['1.0', '-1.0', '-1.0'],
     ['1.0', '-1.0',  '1.0'],
     ['1.0',  '1.0',  '1.0'],
     ['1.0',  '1.0',  '1.0'],
     ['1.0',  '1.0', '-1.0'],
     ['1.0', '-1.0', '-1.0'],
    ['-1.0', '-1.0',  '1.0'],
    ['-1.0',  '1.0',  '1.0'],
     ['1.0',  '1.0',  '1.0'],
     ['1.0',  '1.0',  '1.0'],
     ['1.0', '-1.0',  '1.0'],
    ['-1.0', '-1.0',  '1.0'],
    ['-1.0',  '1.0', '-1.0'],
     ['1.0',  '1.0', '-1.0'],
     ['1.0',  '1.0',  '1.0'],
     ['1.0',  '1.0',  '1.0'],
    ['-1.0',  '1.0',  '1.0'],
    ['-1.0',  '1.0', '-1.0'],
    ['-1.0', '-1.0', '-1.0'],
    ['-1.0', '-1.0',  '1.0'],
     ['1.0', '-1.0', '-1.0'],
     ['1.0', '-1.0', '-1.0'],
    ['-1.0', '-1.0',  '1.0'],
     ['1.0', '-1.0',  '1.0']
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
            "right.jpg",
            "left.jpg",
            "top.jpg",
            "bottom.jpg",
            "back.jpg",
            "front.jpg"
        ]

        for i in range(6):
            filename = cube_images_filename_list[i]
            file_path = f"resources/{directory}/{filename}"
        
            img = Image.open(file_path)
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
        glEnable(GL_TEXTURE_2D)
        glDepthMask(GL_FALSE)
        glEnableVertexAttribArray(0)    
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.number)
        glDrawArrays(GL_TRIANGLES, self.start, self.n_vertices) ## renderizando
        # glBindTexture(GL_TEXTURE_2D, 0)
        glDepthMask(GL_TRUE)

# import OpenGL
# OpenGL.FORWARD_COMPATIBLE_ONLY = True 
# from OpenGL.GL import *

# from OpenGL.GL.ARB.vertex_program import glVertexAttribPointerARB

# import math
# import numpy
# from model import Model_Cube_Map

# class Cubemap:
    
    

#     def init_shaders(self,debug = False):
#         if self.vertex_shader == None or self.fragment_shader == None:
#             v_shader_source = [\
#             """
#             #version 330
#             in vec4 pos;
#             uniform mat4 mvpTransf;
#             varying vec3 ex_texcoord;
#             void main(void){
#             ex_texcoord = pos.xyz;
#             gl_Position = mvpTransf * pos;}
#             """]
#             f_shader_source = [\
#             """
#             #version 330
#             out vec4 fragColor;
#             uniform samplerCube cubemap;
#             varying vec3 ex_texcoord;
#             void main(void){fragColor = texture(cubemap, ex_texcoord);}
#             """]

#             self.cubemap_sampler_name = 'cubemap'
#             self.pos_attr_name = 'pos'
#             self.rot_transf_name = 'mvpTransf'

#         else:
#             v_shader_source = [open(self.vertex_shader,'r').read()]
#             f_shader_source = [open(self.fragment_shader,'r').read()]

#         self.vertex_shader_id = glCreateShader(GL_VERTEX_SHADER)
#         glShaderSource(self.vertex_shader_id,v_shader_source)
        
#         self.fragment_shader_id = glCreateShader(GL_FRAGMENT_SHADER)
#         glShaderSource(self.fragment_shader_id,f_shader_source)
        
#         program = glCreateProgram()
#         glAttachShader(program,self.vertex_shader_id)
#         glAttachShader(program,self.fragment_shader_id)
        
#         glCompileShader(self.vertex_shader_id)
#         glCompileShader(self.fragment_shader_id)
        
#         glLinkProgram(program)
#         glValidateProgram(program)

#         print "////////////////Cubemap shaders status:"
#         print glGetShaderInfoLog(self.vertex_shader_id)
#         print glGetShaderInfoLog(self.fragment_shader_id)
#         print glGetProgramInfoLog(program)
#         print "///////////////////////////////////////"
#         self.program = program
#         return True

#     def set_textures(self,xp,xn,yp,yn,zp,zn,debug = False):
#         if self.program == None:
#             print 'No program defined'
#             return False
#         self.texture = Model_Cube_Map('cubemap')
#         self.texture.set_textures(xp,xn,yp,yn,zp,zn)

#     def bindTexture(self,tex):
#         glUseProgram(self.program)
#         loc = glGetUniformLocation(self.program,'cubemap')
#         tex.bind()
#         glUniform1i(loc,0)

#     def use_program(self):
#         glUseProgram(self.program)

#     def draw(self,rotTransf):

#         if self.cubemap_sampler_name == None:
#             print "Error: No cubemap sampler name defined"
#             return False

#         glBindBuffer(GL_ARRAY_BUFFER,self.cubemap_pos_buf)
#         glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.cubemap_elem_buf)

#         pos_attr_loc = glGetAttribLocation(self.program,self.pos_attr_name)
#         glEnableVertexAttribArray(pos_attr_loc)
#         glVertexAttribPointerARB(pos_attr_loc,3,GL_FLOAT,GL_FALSE,0,vbo_offset(0))

#         location = glGetUniformLocation(self.program,self.rot_transf_name)
#         glUniformMatrix4fv(location, 1, GL_FALSE, rotTransf)


#         glDrawElements(GL_TRIANGLES,36,GL_UNSIGNED_INT,None)

#         if glGetError() != GL_NO_ERROR:
#             print "Error: " + str(glGetError())
            
#         glBindBuffer(GL_ARRAY_BUFFER,0)
#         glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,0)


# def cubemapVals(radius, clockwise = True):

#     a = math.sqrt(3 * (radius**2))
        
#     #ZPOS
#     pos =  [(-a,a,a),(a,a,a),(-a,-a,a)]
#     pos += [(-a,-a,a),(a,a,a),(a,-a,a)]
#     #ZNEG
#     pos += [(a,a,-a),(-a,a,-a),(-a,-a,-a)]
#     pos += [(a,a,-a),(-a,-a,-a),(a,-a,-a)]
#     #XNEG
#     pos += [(-a,a,-a),(-a,a,a),(-a,-a,-a)]
#     pos += [(-a,-a,-a),(-a,a,a),(-a,-a,a)]
#     #XPOS
#     pos += [(a,a,a),(a,a,-a),(a,-a,-a)]
#     pos += [(a,a,a),(a,-a,-a),(a,-a,a)]
#     #YPOS
#     pos += [(-a,a,a),(-a,a,-a),(a,a,a)]
#     pos += [(a,a,a),(-a,a,-a),(a,a,-a)]
#     #YNEG
#     pos += [(-a,-a,-a),(-a,-a,a),(a,-a,a)]
#     pos += [(-a,-a,-a),(a,-a,a),(a,-a,-a)]

#     if not clockwise:
#         for i in range(0,36,3):
#             vn = pos[i]
#             pos[i] = pos[i+1]
#             pos[i+1] = vn

#     return pos

# def vbo_offset(offset):
#     return ctypes.c_void_p(offset * 4)


