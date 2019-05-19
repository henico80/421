import sys, pygame, numpy, random, collections
sys.path.append('assets/')

import sounds
import settings as cfg

class Dices:
    ## initialisation variables
    def __init__(self):
        self.combinations = [0,0,0]
        self.shaking = []
        self.maxShaking = 1
        self.shakedTimes = -1
        #self.shake(False)

    ## get(), set() methods   
    def get(self):
        return self.combinations

    def rand(self):
        return random.randint(1,6)

    def resetShaking(self):
        self.shakedTimes = 0

    def setMaxShaking(self, n):
        self.maxShaking = n

    ## Methods
    # gère les dès qui vont être relancés
    def handleShaking(self, n):
        if not(n in self.shaking):
            self.shaking.append(n)
        else:
            self.shaking.remove(n)

    # relance les dés
    def shake(self, handleShaking):
        if ((self.shakedTimes < self.maxShaking) or (self.maxShaking == -1)):
            # gère les dés à être relancés, par défaut on inclue les trois dés dans une liste : [1,2,3]
            if not(handleShaking):
                ids = [i for i in range(3)]
            else:
                ids = self.shaking

            if (len(ids) > 0):
                # son de relance
                pygame.mixer.music.load(sounds.sounds['dices_shake'])
                pygame.mixer.music.play()
                pygame.mixer.music.set_volume(cfg.settings["volume"])
                self.shakedTimes += 1

                # on attribue une valeur aléatoire aux dés sélectionnés
                for i in range(3):
                    if(i in ids):
                        (self.combinations)[i] = self.rand()
            
            # évite un bug d'affichage
            if ((self.shakedTimes + 1) > self.maxShaking):
                self.shaking = []

    # Détermine le prix de la combinaison du joueur     
    def prize(self, *args):
        # parcoure le dictionnaire : {valeur => clé}
        # on recherche dans les clés -- la fréquence n
        # on retourne la valeur '''le résultat est de la forme: data[i] ''' soit un entier naturel dans ce cas (dés)
        def kohlantry(data,n):
            if (len(data) > 0):
                test = 0

                try:
                    # méthode pour récupérer la valeur en fonction de la clé dans un dictionnaire
                    test = list(data.keys())[list(data.values()).index(n)]
                except ValueError:
                    test = 0

                return test
            else:
                return 0

        if (len(args) > 0):
            if (isinstance(args[0], str)):
                args = args[1::]
                return kohlantry(*args)

        # je ne sais plus si self.combinations sera changé ou pas
        temp = sorted(self.combinations, reverse=True)
        
        # combinaison la plus forte du jeu
        if (temp == [4,2,1]):
            return 10
        # nénette (à prendre en charge)
        elif (temp == [2,2,1]):
            return 2
        else:
            # on calcule la fréquence des chiffres dans une combinaison
            data = collections.Counter(self.combinations)
            
            # get 1,1,1 for instance
            test = kohlantry(data,3)
            if (test > 0):
                if(test == 1): return 7
                else: return test
            
            # get 1,1,2 for exemple
            test = kohlantry(data,2)
            if (test > 0):
                for o in range(2):
                    if (data[o] > 1):
                        data.pop(o, None)
                        return (list(data)[0])
            
            # get numbers sequence
            if numpy.all(numpy.diff(self.combinations, 2) == 0):
                return 2
            
            # envoie le défaut si aucun return n'a été déclanché
            return 1