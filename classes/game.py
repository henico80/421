import sys, player, threading, time
sys.path.append('assets/')

sys.setrecursionlimit(10000)

import settings as cfg

# Méthode pour lancer une fonction en prog parallèle (voir dossier écrit Nicolas)
def threaded(fn):
    def wrapper(*args, **kwargs):
        handle = threading.Thread(target=fn, args=args, kwargs=kwargs)
        if (fn.__name__ == "waitForPlayers"):
            handle.setDaemon(True)
        handle.start()
    return wrapper

class Game:
    # On init la partie
    def __init__(self):
        self.reset()

    ###########################################################################################################################################################
    #  GAME
    ###########################################################################################################################################################
    
    ### Basics ###
    # On remet à zéro toutes les variables
    def reset(self):
        self.stop = False
        self.round = 0
        self.fights = 0
        self.round_name = "Préparatifs"
        self.pot = cfg.settings['pot']
        self.solo = False
        self.turn = 0
        self.msg = "?"

        if not(hasattr(self, 'players')):
            self.players = []
        else:
            for i, x in enumerate(self.players):
                if not(x.name == "me"):
                    self.players.pop(i)
                
        self.turn = None
        self.lock = False

    # On lance une partie de jeu
    def startGame(self):
        print("game start")
        self.waitForPlayers("self.nextRound()")

    # On attend que tous les joueurs aient fini le chargement du jeu pour lancer une fonction
    @threaded
    def waitForPlayers(self, fn):
        while True:
            n = 0
            for x in self.players:
                if (x.ready): n += 1
            if (n == cfg.settings['players']): break
            if (self.stop): break
        
        if not(self.stop):
            exec(fn)

    # On arrête la partie en cours    
    def stopGame(self):
        sys.stdout.flush()
        self.stop = True

        for x in self.players:
            if (x.remote or x.name == "computer"):
                x.join()
            else:
                if not(x.screen.leaving):
                    x.leave()
                    x.screen.loadScene(0)
                x.reset()
        
        self.reset()
        print("game stop")

    # On informe tous les joueurs d'une information donnée
    def tellPlayers(self, how_many_time, msg):
        self.msg = msg

        for x in self.players:
            if (x.name == "me"):
                x.screen.notification = True

        for x in range(how_many_time):      
            if (self.stop): break
            time.sleep(1)

        for x in self.players:
            if (x.name == "me"):
                x.screen.notification = False

        self.msg = ""

    ### Rounds ###
    # On passe le tour à quelqu'un d'autre
    def roundNextTurn(self):
        player = self.turn[0]

        end = False
        self.turn = [-1, "..."]
        self.players[player].turn = False

        if (player < (cfg.settings['players']-1)):
            player += 1
        else:
            end = True
            player = 0

        if (player == 1 and self.fights == 0 and self.round == 2):
            for x in self.players:
                x.dices.maxShaking = self.players[0].dices.shakedTimes
        
        self.turn = [player, self.players[player].name]
        self.players[player].turn = True

        if (end):
            self.turnResetActions()

    # Gère un tour de table
    def turnResetActions(self):
        self.roundCombinationsFight()

        for x in self.players:
            x.dices.resetShaking()

        if (self.round == 1 and self.pot == 0):
            self.nextRound()
            self.fights = 0
        else:
            self.fights += 1

    # Détermine le gagnant d'un tour
    def roundCombinationsFight(self):
        temp = []

        # On récupère la valeur des combinaisons de chaque joueur
        for x in self.players:
            temp.append(x.dices.prize())
        

        # On récupère le min, le max
        values = [min(temp), max(temp)]

        if not(values[1:] == values[:-1]):
            indexes = [temp.index(min(temp)), temp.index(max(temp))]
            tokens = (self.players[indexes[1]]).dices.prize()

            # Premiere manche : la charge
            if (self.round == 1):
                if ((self.pot - tokens) < 0):
                    tokens = self.pot
                
                self.pot -= tokens
                (self.players[indexes[0]]).addTokens(tokens)

            # Deuxieme manche : la décharge
            elif (self.round == 2):
                (self.players[indexes[1]]).removeTokens(tokens)
                (self.players[indexes[0]]).addTokens(tokens)

                # Un joueur n'a plus de jetons : c'est le vainqueur
                if (self.players[indexes[1]].tokens <= 0):
                    self.gameWinner(self.players[indexes[1]])

            if not(self.stop):
                self.tellPlayers(2, "+{} jetons pour {} !".format(tokens, (self.players[indexes[0]]).name))
        else:
            self.tellPlayers(2, "Égalité !")

    # Arrête le jeu en broadcast le gagnant à tous les joueurs
    def gameWinner(self, who):
        self.tellPlayers(10, "{} gagne cette partie !".format(who.name))
        self.stopGame()

    # Passe à la manche suivante
    def nextRound(self):
        if (self.round > 0):
            for x in self.players:
                if (x.tokens == 0):
                    self.gameWinner(x)
                    break
                else:
                    if (self.round == 2):
                        x.dices.maxShaking = -1

        self.round += 1
        self.turn = [-1]

        self.roundNextTurn()

        if(self.round == 1):
            self.round_name = "Charge"
            self.tellPlayers(2, "Joueurs, prenez place !")
        elif(self.round == 2):
            self.round_name = "Décharge"
            self.tellPlayers(5, "Changement de round !")

    ###########################################################################################################################################################
    #  PLAYERS
    ###########################################################################################################################################################
    # Gère un nouveau joueur
    @threaded
    def newPlayer(self, name, remote):
        print('new player: {} {}'.format(name,remote))
        
        if (self.lock):
            print("Serveur: Je n'accepte pas d'autres joueurs ! La table est complète.")
            return
        else:
            obj = player.Player(name,remote,self)
            self.players.append(obj)
            
            obj.start()

            if (len(self.players) == cfg.settings['players']):
                self.lock = True
                self.startGame()
                
    # Gère le départ d'un joueur            
    def playerLeave(self, name):
        print('player left: {}'.format(name))
        
        players = [x.name for x in self.players]
        player = players.index(name)
        
        if not(name == "me"):
            (players[player]).join()
            self.players.pop(player)
        else:
            self.stopGame()