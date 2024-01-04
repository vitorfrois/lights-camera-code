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
from skybox import Skybox

# Defines
logger = LoggerHelper.get_logger(__name__)
offset = ctypes.c_void_p(0)
polygonal_mode = False
list_obj = []
GLFW_PRESS = 1

angle = 45.0

r_x = 1.0; r_y = 1.0; r_z = 0.0;

# translacao
t_x = 0.0; t_y = 0.0; t_z = 0.0;

# escala
s_x = 0.1; s_y = 0.1; s_z = 0.1;

linear_magnification = True
object_selection = 1

cameraPos   = glm.vec3(0.0,  0.0,  1.0)
cameraFront = glm.vec3(0.0,  0.0, -1.0)
cameraUp    = glm.vec3(0.0,  1.0,  0.0)

lightx = 10.0
lighty = 10.0
lightz = 10.0

def key_event(window,key,scancode,action,mods):
    global cameraPos, cameraFront, cameraUp, polygonal_mode, lightx, lighty, lightz
    
    cameraSpeed = 0.5
    if key == 87: # tecla W
        cameraPos += cameraSpeed * cameraFront
    
    if key == 83: # tecla S
        cameraPos -= cameraSpeed * cameraFront
    
    if key == 65: # tecla A
        cameraPos -= glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed
        
    if key == 68: # tecla D
        cameraPos += glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed

    if key == 80 and action == GLFW_PRESS:
        polygonal_mode = not polygonal_mode

    if key == 86 and action == GLFW_PRESS:
        linear_magnification = not linear_magnification

    if key == 76 and action == GLFW_PRESS:
        lightx = -10


    # info_message = f"Pressed key: {key}"
    # logging.info(info_message)

firstMouse = True
yaw = -90.0 
pitch = 0.0
lastX =  600
lastY =  450

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

    # box = GLObject('caixa')
    # box.set_lightning(0.7, 0.5, 0.1, 0.1)
    # box.init_obj()
    # env.add_object(box)

    box2 = GLObject('caixa', t_x=3, t_y=3)
    box2.set_lightning(0.3, 0.3, 0.4, 0.4)
    box2.init_obj()
    env.add_object(box2)

    sphere = GLObject('sphere', t_x=-5)
    sphere.set_lightning(0.3, 0.5, 0.5, 1)
    sphere.init_obj()
    env.add_object(sphere)

    skybox = Skybox('skybox')
    skybox.set_lightning(1, 1, 1, 1)
    skybox.init_obj('cube')
    env.add_skybox(skybox)
    
    # skybox.draw_obj()

    # basset = GLObject('basset')
    # basset.init_obj()
    # env.add_object(basset)

    container = GLObject('container', s_x=0.1, s_y=0.1, s_z=0.1)
    container.set_lightning(0.8, 1, 0.4, 0.3)
    container.init_obj()
    env.add_object(container)

    # coffee = GLObject('coffee')
    # coffee.set_lightning(0.8, 1, 0.4, 0.3)
    # coffee.init_obj()
    # env.add_object(coffee)
    # coffee.draw_obj()

    # monstro = GLObject('monstro')
    # monstro.init_obj()
    # env.add_object(monstro)

    global x_inc, y_inc, yr_inc, zr_inc, s_inc
    global object_selection
    global list_obj
    global polygonal_mode
    global linear_magnification

    for obj in env.get_list_objects():
        logger.info(obj)

    env.send_vertices()
    env.send_texture()

    while not glfw.window_should_close(env.window):
        glfw.poll_events() 
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        env.main_shader.use()
        env.main_shader.set_3float("lightPos", lightx, lighty, lightz)
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

        # Create view and projection matrices
        mat_view = Matrix.view(cameraPos, cameraFront, cameraUp)
        mat_projection = Matrix.projection(1200, 900)

        # Draw the skybox
        env.skybox_shader.use()
        new_view = np.zeros((4,4))
        new_view[:3, :3] = mat_view[:3, :3]
        env.skybox_shader.set_mat4("view", new_view)
        env.skybox_shader.set_mat4("projection", mat_projection)
        env.skybox_obj.draw_obj(env.get_program())

        # Send main shader matrices
        env.main_shader.use()
        env.main_shader.set_mat4("view", mat_view)
        env.main_shader.set_mat4("projection", mat_projection)
        env.main_shader.set_3float("viewPos", cameraPos[0], cameraPos[1], cameraPos[2])

        # Render all objects
        list_obj = env.get_list_objects()
        loc_model = glGetUniformLocation(env.get_program(), "model")
        for obj_to_render in list_obj:
            obj_model_matrix = obj_to_render.get_matrix()
            glUniformMatrix4fv(loc_model, 1, GL_FALSE, obj_model_matrix)
            obj_to_render.draw_obj(env.get_program())

        glfw.swap_buffers(env.window)

        logger.info(cameraPos)

    glfw.terminate()

if __name__ == '__main__':
    main()