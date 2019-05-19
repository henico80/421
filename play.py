'''
    421 : Dices game
'''
import sys, time, threading
sys.path.append('classes/')

# On importe la classe du jeu
import game

# Instancie le joueur : moteur du jeu
if (__name__ == '__main__'):
    main = game.Game()
    main.newPlayer("me", False)