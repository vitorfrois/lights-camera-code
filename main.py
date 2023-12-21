import glfw
import OpenGL.GL.shaders
import math
import logging
import time
import glm

import numpy as np

from OpenGL.GL import *
from PIL import Image
from matrix import Matrix
from globject import GLObject
from objhelper import ObjHelper
from environment import Environment
from logger_helper import LoggerHelper

# Defines
logger = LoggerHelper.get_logger(__name__)
offset = ctypes.c_void_p(0)
polygonal_mode = False
list_obj = []
GLFW_PRESS = 1

linear_magnification = True
object_selection = 1

cameraPos   = glm.vec3(0.0,  0.0,  1.0)
cameraFront = glm.vec3(0.0,  0.0, -1.0)
cameraUp    = glm.vec3(0.0,  1.0,  0.0)

def key_event(window,key,scancode,action,mods):
    global cameraPos, cameraFront, cameraUp, polygonal_mode
    
    cameraSpeed = 0.05
    if key == 87 and (action==1 or action==2): # tecla W
        cameraPos += cameraSpeed * cameraFront
    
    if key == 83 and (action==1 or action==2): # tecla S
        cameraPos -= cameraSpeed * cameraFront
    
    if key == 65 and (action==1 or action==2): # tecla A
        cameraPos -= glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed
        
    if key == 68 and (action==1 or action==2): # tecla D
        cameraPos += glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed

    if key == 80 and action == GLFW_PRESS:
        polygonal_mode = not polygonal_mode

    if key == 86 and action == GLFW_PRESS:
        linear_magnification = not linear_magnification

    info_message = f"Pressed key: {key}"
    logging.info(info_message)

firstMouse = True
yaw = -90.0 
pitch = 0.0
lastX =  400
lastY =  400

def mouse_event(window, xpos, ypos):
    global firstMouse, cameraFront, yaw, pitch, lastX, lastY
    if firstMouse:
        lastX = xpos
        lastY = ypos
        firstMouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos
    lastX = xpos
    lastY = ypos

    sensitivity = 0.3 
    xoffset *= sensitivity
    yoffset *= sensitivity

    yaw += xoffset;
    pitch += yoffset;

    
    if pitch >= 90.0: pitch = 90.0
    if pitch <= -90.0: pitch = -90.0

    front = glm.vec3()
    front.x = math.cos(glm.radians(yaw)) * math.cos(glm.radians(pitch))
    front.y = math.sin(glm.radians(pitch))
    front.z = math.sin(glm.radians(yaw)) * math.cos(glm.radians(pitch))
    cameraFront = glm.normalize(front)




def main():
    env = Environment(1200, 900)
    env.set_key_callback(key_event)
    env.set_mouse_callback(mouse_event)
    window = env.get_window()

    loc = env.get_loc()

    # Adding objects

    box = GLObject('caixa')
    box.init_obj()
    env.add_object(box)

    # basset = GLObject('basset')
    # basset.init_obj()
    # env.add_object(basset)

    container = GLObject('container')
    container.init_obj()
    env.add_object(container)

    geladeira = GLObject('coffee')
    geladeira.init_obj()
    env.add_object(geladeira)

    # monstro = GLObject('monstro')
    # monstro.init_obj()
    # env.add_object(monstro)

    global x_inc, y_inc, yr_inc, zr_inc, s_inc
    global object_selection
    global list_obj
    global polygonal_mode
    global linear_magnification

    # MOVE
    x_inc = 0.0
    y_inc = 0.0

    # ROTATE
    yr_inc = 0.0
    zr_inc = 0.0

    # SCALE
    s_inc = 1.0

    object_selection = 1

    for obj in env.get_list_objects():
        logger.info(obj)

    env.send_vertices()
    env.send_texture()


    while not glfw.window_should_close(env.window):
        glfw.poll_events() 
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        loc_light_pos = glGetUniformLocation(env.program, "lightPos") 
        glUniform3f(loc_light_pos, 1.0, 0.0, 0.0)
        glClearColor(0.2, 0.2, 0.2, 1.0)


        if polygonal_mode:
            glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)

        if linear_magnification:
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        else:
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)


        # Bound increases
        if x_inc > 0.05: x_inc = 0.05
        if y_inc > 0.05: y_inc = 0.05
        if x_inc < -0.05: x_inc = -0.05
        if y_inc < -0.05: y_inc = -0.05

        if yr_inc > 20: yr_inc = 20
        if zr_inc > 20: zr_inc = 20
        if yr_inc < -20: yr_inc = -20
        if zr_inc < -20: zr_inc = -20

        # Get All Objects
        list_obj = env.get_list_objects()
        
        loc = env.get_loc()

        for obj_to_render in list_obj:
            # center = obj_to_render.get_center()
            # y_rotation = Matrix.get_y_inplace_rotation(center, yr_inc)
            # z_rotation = Matrix.get_x_inplace_rotation(center, zr_inc)
            # scale = Matrix.get_scale(center, s_inc)
            # translation = Matrix.get_translation(x_inc, y_inc)
            # mat_transform = Matrix.multiply(y_rotation, z_rotation, scale, translation)

            # final_matrix = obj_to_render.get_matrix()
            # obj_to_render.valid_transformation(mat_transform)
            # final_matrix = Matrix.multiply(mat_transform, final_matrix)
            # obj_to_render.set_matrix(final_matrix)

            glUniformMatrix4fv(loc, 1, GL_TRUE, Matrix.get_identity())
            obj_to_render.draw_obj()

        mat_view = Matrix.view(cameraPos, cameraFront, cameraUp)
        loc_view = glGetUniformLocation(env.program, "view")
        glUniformMatrix4fv(loc_view, 1, GL_FALSE, mat_view)

        mat_projection = Matrix.projection(1200, 900)
        loc_projection = glGetUniformLocation(env.program, "projection")
        glUniformMatrix4fv(loc_projection, 1, GL_FALSE, mat_projection)  

        glfw.swap_buffers(env.window)

    glfw.terminate()

if __name__ == '__main__':
    main()