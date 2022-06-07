#!/usr/bin/env python3

from asyncio import constants
import OpenGL.GL as GL
import glfw
import pyrr
import numpy as np
from cpe3d import Object3D
import time

class ViewerGL:
    def __init__(self):
        # initialisation de la librairie GLFW
        glfw.init()
        # paramétrage du context OpenGL
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        # création et paramétrage de la fenêtre
        glfw.window_hint(glfw.RESIZABLE, False)
        self.window = glfw.create_window(800, 800, 'OpenGL', None, None)
        # paramétrage de la fonction de gestion des évènements
        glfw.set_key_callback(self.window, self.key_callback)
        # activation du context OpenGL pour la fenêtre
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)
        # activation de la gestion de la profondeur
        GL.glEnable(GL.GL_DEPTH_TEST)
        # choix de la couleur de fond
        GL.glClearColor(0.5, 0.6, 0.9, 1.0)
        print(f"OpenGL: {GL.glGetString(GL.GL_VERSION).decode('ascii')}")

        self.objs = []
        self.touch = {}

    def run(self):
        global t_espace, t_right, t_left, t_pos, dt
        #initialisation de la variable t_espace pour le saut
        t_espace = 0
        t_right  = 0
        t_left   = 0
        t_pos    = 0
        # boucle d'affichage
        while not glfw.window_should_close(self.window):
            # nettoyage de la fenêtre : fond et profondeur
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            self.update_key()

            for obj in self.objs:
                GL.glUseProgram(obj.program)
                if isinstance(obj, Object3D):
                    self.update_camera(obj.program)
                obj.draw()

            #On centre la caméra sur notre personnage
            self.cam.transformation.rotation_euler = self.objs[0].transformation.rotation_euler.copy() 
            self.cam.transformation.rotation_euler[pyrr.euler.index().yaw] += np.pi
            self.cam.transformation.rotation_center = self.objs[0].transformation.translation + self.objs[0].transformation.rotation_center
            self.cam.transformation.translation = self.objs[0].transformation.translation + pyrr.Vector3([0, 1, 5])
            
            #On fait avancer notre personnage en continue
            self.objs[0].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, 0.02]))

            
            #Pour les déplacements (il faut mettre le code ici sinon ça ne boucle pas)
            
            #Le saut (méthode sans gravité)
            #if t_espace > 50 :
            #    self.objs[0].transformation.translation.y += 0.01
            #    t_espace = t_espace -1
            #elif 0 < t_espace <= 50:
            #    self.objs[0].transformation.translation.y -= 0.01
            #    t_espace = t_espace -1
            #else :
            #    t_espace = 0
            
            #Le saut (méthode avec gravité)
            #start = time.time()
            if self.objs[0].transformation.translation.y > 1 : #si l'object est en l'air
                g  = pyrr.Vector3([0,9.81,0]) #9.81 pour la gravité
                #dt = time.time() - start
                self.objs[0].vitesse                    -= g * 0.05
                self.objs[0].transformation.translation += self.objs[0].vitesse * 0.05
            #pour empêcher que notre personnage s'enfonce dans le sol :
            if self.objs[0].transformation.translation.y < 1 :
                self.objs[0].transformation.translation.y = 1

            #Déplacement à droite
            if t_right > 0 :
                self.objs[0].transformation.translation.x -= 0.2
                t_right = t_right -1
            else :
                t_right = 0
            #Déplacement à gauche
            if t_left > 0 :
                self.objs[0].transformation.translation.x += 0.2
                t_left = t_left -1
            else :
                t_left = 0

            t=glfw.get_time()
            print(t)

            # changement de buffer d'affichage pour éviter un effet de scintillement
            glfw.swap_buffers(self.window)
            # gestion des évènements
            glfw.poll_events()
            
        
    def key_callback(self, win, key, scancode, action, mods):
        global t_espace, t_right, t_left, t_pos
        # sortie du programme si appui sur la touche 'échappement'
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(win, glfw.TRUE)
        self.touch[key] = action
        #if t_espace == 0 : #cette condition permet de pas superposer deux sauts
        if key == glfw.KEY_SPACE and action == glfw.PRESS:
            self.objs[0].vitesse.y = 10
            self.objs[0].transformation.translation.y = 1.01

        if t_left == 0 and t_right == 0 and t_pos >-1 :
        #le t_left == 0 et t_right == 0 sont les conditions qui font que on ne peut pas faire deux déplacements simultanés
        #t_pos est une variable qui stock une valeur en fonction de la position, qui permet de définir des déplacements interdits   
            if glfw.KEY_LEFT in self.touch and self.touch[glfw.KEY_LEFT] > 0:
                t_left  = 20
                t_pos -= 1
                    #print("t_pos vaut", t_pos)     #pour vérifier que t_pos marche bien
        if t_right == 0 and t_left == 0 and t_pos <1:
                if glfw.KEY_RIGHT in self.touch and self.touch[glfw.KEY_RIGHT] > 0:
                    t_right = 20
                    t_pos += 1
                    #print("t_pos vaut", t_pos)     #pour vérifier que t_pos marche bien
    
    def add_object(self, obj):
        self.objs.append(obj)

    def set_camera(self, cam):
        self.cam = cam

    def update_camera(self, prog):
        GL.glUseProgram(prog)
        # Récupère l'identifiant de la variable pour le programme courant
        loc = GL.glGetUniformLocation(prog, "translation_view")
        # Vérifie que la variable existe
        if (loc == -1) :
            print("Pas de variable uniforme : translation_view")
        # Modifie la variable pour le programme courant
        translation = -self.cam.transformation.translation
        GL.glUniform4f(loc, translation.x, translation.y, translation.z, 0)

        # Récupère l'identifiant de la variable pour le programme courant
        loc = GL.glGetUniformLocation(prog, "rotation_center_view")
        # Vérifie que la variable existe
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_center_view")
        # Modifie la variable pour le programme courant
        rotation_center = self.cam.transformation.rotation_center
        GL.glUniform4f(loc, rotation_center.x, rotation_center.y, rotation_center.z, 0)

        rot = pyrr.matrix44.create_from_eulers(-self.cam.transformation.rotation_euler)
        loc = GL.glGetUniformLocation(prog, "rotation_view")
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_view")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, rot)
    
        loc = GL.glGetUniformLocation(prog, "projection")
        if (loc == -1) :
            print("Pas de variable uniforme : projection")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, self.cam.projection)

    def update_key(self):
        if glfw.KEY_J in self.touch and self.touch[glfw.KEY_J] > 0:
            self.cam.transformation.rotation_euler[pyrr.euler.index().yaw] -= 3.15


