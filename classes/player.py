import threading, dices, display, time, collections, random

# Méthode pour lancer une fonction en prog parallèle (voir dossier écrit Nicolas)
def threaded(fn):
    def wrapper(*args, **kwargs):
        handle = threading.Thread(target=fn, args=args, kwargs=kwargs)
        handle.setDaemon(True)
        handle.start()
    return wrapper

class Player(threading.Thread):
    ### Init ###
    def __init__(self,name,remote,game):
        threading.Thread.__init__(self)

        self.game = game
        self.name = name
        self.remote = remote
        self.ready = False
        
        self.reset()
        
        # Gère le mode solo
        if (name == 'computer'):
            self.ready = True
            game.solo = True
            self.remote = True

    # Remise à zéro de variables essentielles
    def reset(self):
        self.notification = False
        self.tokens = 0
        self.turn = False
        self.dices = dices.Dices()

    # gère le joueur : fonction de lancement du thread
    def run(self):
        if not(self.remote):
            self.screen = display.Display(self)
            self.screen.start()

        if (self.name == "computer"):
            self.AI()

    ### AI integration ###
    # Gère le bot qui joue en mode solo
    @threaded
    def AI(self):
        while not(self.game.stop):
            # j'attends mon tour comme un grand garçon
            while (self.turn != True):
                if (self.game.stop): break
                time.sleep(1)
            
            print("c'est mon tour")

            # je lance mes dés pour la première fois si ce n'est pas fait
            if (self.dices.get() == [] or self.dices.get() == [0,0,0]):
                self.dices.shake(False)
                self.dices.shakedTimes = 0

            print("des ia: "+str(self.dices.get())+" , prix: "+str(self.dices.prize()))
            print(self.dices.shakedTimes, self.dices.maxShaking)

            # je relance au maximum tant de fois que la partie l'autorise
            for x in range(self.dices.shakedTimes, self.dices.maxShaking):
                print("je relance : "+str(x))
                self.dices.shaking = []

                temp = sorted(self.dices.combinations, reverse=True)
                if (temp == [4,2,1] or temp == [1,1,1]): break
                # je détermine les dés à relancer

                # NOTE: on détermine l'avantage en fonction de la moyenne des jetons (de tout le monde) et si on est en dessous, on n'a pas l'avantage
                # SCHEMA :
                #   - On trouve 2 éléments pareils
                #       -> On trouve des 1 : on joue les as (on relance tant qu'on n"obtient pas 1 ou 6)
                #       -> Si >= 4 et avantage : on laisse
                #       -> Sinon on va à la case sinon finale et on fait intervenir les probas
                #   
                #   - Recherche d'un élément :
                #       -> 4,2 ou 1 (As) : On essaye de faire un 421
                #       -> si as : on mélange tout sauf celui-ci
                #       -> Sinon on va à la case sinon finale et on fait intervenir les probas
                #
                #   - Sinon (final) :
                #       -> Probabilités (> 50% : je relance la composante)
                final = False
                data = collections.Counter(self.dices.combinations)

                # method
                def popping(data, n, arg):
                    for o in range(n):
                        cond = "if (data[0] "+str(arg)+"): data.pop(o, None)"
                        exec(cond)

                # avantage
                result = []
                for x in self.game.players:
                    result.append(x.tokens)

                avantage = True if (self.tokens <= (sum(result) / len(result))) else False

                print(self.dices.combinations)
                print("-----------------")
                test = self.dices.prize("kohlantry", data, 2)
                print("test 1: "+str(test))
                if (test > 0):
                    if (test == 1):
                        print("popping")
                        popping(data, 2, "== 1")
                        print("fin popping")
                        self.dices.shaking.append(self.dices.combinations.index(list(data)[0]))
                    else:
                        if (test >= 4 and avantage):
                            test2 = self.dices.prize("kohlantry", data, 3)
                            if (test2 == test): break
                            print("popping")
                            popping(data, 2, "== "+str(test))
                            print("fin popping")
                            self.dices.shaking.append(self.dices.combinations.index(list(data)[0]))
                        else:
                            final = True
                else:
                    test = [x if x in [4,2,1] else 0 for x in self.dices.combinations]
                    print("test 2: "+str(test))
                    if (sum(test) > 0):
                        for e, y in enumerate(test):
                            if (y == 0): self.dices.shaking.append(e)
                    else:
                        for i, x in enumerate(self.dices.combinations):
                            if (x == 1):
                                if (i in self.dices.shaking):
                                    self.dices.shaking.remove(i)
                            else:
                                if not(i in self.dices.shaking):
                                    self.dices.shaking.append(i)

                print("-----------------")
                            
                # doit-on passer par l'aléatoire final, ou non
                if (final):
                    self.dices.shaking = []
                    for i in range(3):
                        prob = random.randint(0,100)
                        if (prob >= 50):
                            self.dices.shaking.append(i)

                # si pas de probabilités à mon avantage, je passe mon tour
                print(str(self.dices.shaking))
                if (self.dices.shaking == []): break
                self.dices.shake(True)
                print("combinaison: "+str(self.dices.combinations))
                time.sleep(1)

            # je passe mon tour
            print("je passe mon tour")
            time.sleep(1)
            print("----------------")
            print("prix final: "+str(self.dices.get())+" "+str(self.dices.prize()))
            self.game.roundNextTurn()

    ### Gaming ###
    # méthodes get(), set()
    def removeTokens(self, tokens):
        if ((self.tokens - tokens) < 0): 
            tokens = 0
            self.tokens = 0

        self.tokens -= tokens

    def addTokens(self, tokens):
        self.tokens += tokens

    ### Others ###
    # gère le fait que le joueur veuille partir du jeu
    def leave(self):
        if (self.screen.leaving):
            print('i want to leave')
            if (self.game.solo):
                self.game.playerLeave('me')

        if not(self.remote):
            self.screen.loadScene(0)