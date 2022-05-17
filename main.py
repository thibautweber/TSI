#!/usr/bin/env python3

import os
import OpenGL.GL as GL
import glfw
import numpy as np

def init_window():
    # initialisation de la librairie glfw
    glfw.init()
    # paramétrage du context opengl
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    # création et parametrage de la fenêtre
    glfw.window_hint(glfw.RESIZABLE, False)
    window = glfw.create_window(800, 800, 'OpenGL', None, None)
    # parametrage de la fonction de gestion des évènements
    glfw.set_key_callback(window, key_callback)
    return window

def init_context(window):
    # activation du context OpenGL pour la fenêtre
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    # activation de la gestion de la profondeur
    GL.glEnable(GL.GL_DEPTH_TEST)
    # choix de la couleur de fond
    GL.glClearColor(0.5, 0.6, 0.9, 1.0)
    print(f"OpenGL: {GL.glGetString(GL.GL_VERSION).decode('ascii')}")

def init_program():
    pass
        
def init_data():
    pass

def run(window):
    # boucle d'affichage
    while not glfw.window_should_close(window):
        # nettoyage de la fenêtre : fond et profondeur
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        #  l'affichage se fera ici

        # changement de buffer d'affichage pour éviter un effet de scintillement
        glfw.swap_buffers(window)
        # gestion des évènements
        glfw.poll_events()

def key_callback(win, key, scancode, action, mods):
    # sortie du programme si appui sur la touche 'echap'
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(win, glfw.TRUE)

def main():
    window = init_window()
    init_context(window)
    init_program()
    init_data()
    run(window)
    glfw.terminate()

if __name__ == '__main__':
    main()