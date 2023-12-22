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

logger = LoggerHelper.get_logger(__name__)
offset = ctypes.c_void_p(0)


vertex_code = """
        attribute vec3 position;
        attribute vec2 texture_coord;
        attribute vec3 normals;
        
       
        varying vec2 out_texture;
        varying vec3 out_fragPos;
        varying vec3 out_normal;
                
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;        
        
        void main(){
            gl_Position = projection * view * model * vec4(position,1.0);
            out_texture = vec2(texture_coord);
            out_fragPos = vec3(  model * vec4(position, 1.0));
            out_normal = vec3( model *vec4(normals, 1.0));            
        }
        """

fragment_code = """

        // parametro com a cor da(s) fonte(s) de iluminacao
        uniform vec3 lightPos; // define coordenadas de posicao da luz
        vec3 lightColor = vec3(1.0, 1.0, 1.0);
        
        // parametros da iluminacao ambiente e difusa
        uniform float ka; // coeficiente de reflexao ambiente
        uniform float kd; // coeficiente de reflexao difusa
        
        // parametros da iluminacao especular
        uniform vec3 viewPos; // define coordenadas com a posicao da camera/observador
        uniform float ks; // coeficiente de reflexao especular
        uniform float ns; // expoente de reflexao especular

        // parametros recebidos do vertex shader
        varying vec2 out_texture; // recebido do vertex shader
        varying vec3 out_normal; // recebido do vertex shader
        varying vec3 out_fragPos; // recebido do vertex shader
        uniform sampler2D samplerTexture;
        
        void main(){
        
            // calculando reflexao ambiente
            vec3 ambient = ka * lightColor;             
        
            // calculando reflexao difusa
            vec3 norm = normalize(out_normal); // normaliza vetores perpendiculares
            vec3 lightDir = normalize(lightPos - out_fragPos); // direcao da luz
            float diff = max(dot(norm, lightDir), 0.0); // verifica limite angular (entre 0 e 90)
            vec3 diffuse = kd * diff * lightColor; // iluminacao difusa
            
            // calculando reflexao especular
            vec3 viewDir = normalize(viewPos - out_fragPos); // direcao do observador/camera
            vec3 reflectDir = normalize(reflect(-lightDir, norm)); // direcao da reflexao
            float spec = pow(max(dot(viewDir, reflectDir), 0.0), ns);
            
            vec3 specular = ks * spec * lightColor;             
            
            // aplicando o modelo de iluminacao
            vec4 texture = texture2D(samplerTexture, out_texture);
            vec4 result = vec4((ambient + diffuse + specular),1.0) * texture; // aplica iluminacao
            gl_FragColor = result;

        }
        """

skybox_vertex_shader_1 = """
    #version 330 core
    layout (location = 0) in vec3 aPos;

    out vec3 TexCoords;

    uniform mat4 projection;
    uniform mat4 view;

    void main()
    {
        TexCoords = aPos;
        gl_Position = projection * view * vec4(aPos, 1.0);
    }
"""

skybox_vertex_shader_2 = """
#version 330 core
out vec4 FragColor;

in vec3 TexCoords;

uniform samplerCube skybox;

void main()
{    
    FragColor = texture(skybox, TexCoords);
}
"""


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
        self.program  = glCreateProgram()
        vertex   = glCreateShader(GL_VERTEX_SHADER)
        fragment = glCreateShader(GL_FRAGMENT_SHADER)

        # Set shaders source
        glShaderSource(vertex, vertex_code)
        glShaderSource(fragment, fragment_code)

        self.compile_shader(vertex)
        self.compile_shader(fragment)

        # Attach shader objects to the program
        glAttachShader(self.program, vertex)
        glAttachShader(self.program, fragment)

        # Build program
        glLinkProgram(self.program)
        if not glGetProgramiv(self.program, GL_LINK_STATUS):
            logger.error(glGetProgramInfoLog(self.program))
            raise RuntimeError('Linking error')

        # Make program the default program
        glUseProgram(self.program)

        # Init textures
        glEnable(GL_TEXTURE_2D)
        qtd_texturas = 2
        # textures = glGenTextures(qtd_texturas)

        # Request a buffer slot from GPU
        self.buffer = glGenBuffers(4)
        self.buffer_counter = 0
        # Make this buffer the default one

        self.loc = glGetAttribLocation(self.program, "position")
        glEnableVertexAttribArray(self.loc)

        self.texture_loc = glGetAttribLocation(self.program, "texture_coord")
        glEnableVertexAttribArray(self.texture_loc)

        self.normal_loc = glGetAttribLocation(self.program, "normals")
        glEnableVertexAttribArray(self.normal_loc)

        loc_ka = glGetUniformLocation(self.program, "ka") # recuperando localizacao da variavel ka na GPU
        glUniform1f(loc_ka, 0.5) ### envia ka pra gpu
        
        loc_kd = glGetUniformLocation(self.program, "kd") # recuperando localizacao da variavel ka na GPU
        glUniform1f(loc_kd, 0.5) ### envia kd pra gpu 

        loc_light_pos = glGetUniformLocation(self.program, "lightPos") # recuperando localizacao da variavel lightPos na GPU
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
        return self.program

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

        print(obj.vertices)
        for v in obj.vertices['position']:
            self.list_vertices.append(v)

        self.obj_list.append(obj)
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

   