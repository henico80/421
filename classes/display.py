import sys, pygame, threading
sys.path.append('assets/')

# notes :
# -> for draw method, next time please remind to use classes, it's better to see

import settings as cfg
import sounds
import colors

class Display(threading.Thread):
    # variables
    def __init__(self, player):
        threading.Thread.__init__(self)
        self.player = player
        self.leaving = False
        self.music = False

        self.notification = False

    # gère l'affichage : fonction de lancement du thread
    def run(self):
        pygame.init()
        
        self.display = pygame.display.set_mode((cfg.settings['intro_w'],cfg.settings['intro_h']))
        pygame.display.set_caption('421 : Le jeu de dés')
        
        self.clock = pygame.time.Clock()
        self.doloop = False
        self.loadScene(0)

    # pré-charge une scène (pour éviter de boucler le chargement des images par exemple)
    def loadScene(self,n):
        if (self.doloop):
            self.doloop = False
            
        self.buttons = []
        self.click_action = ""
        self.img = {}
        
        # scène d'accueil : sélection du mode
        if (n == 0):
            self.scene = 0
            self.fps = 30
            
            self.display = pygame.display.set_mode((cfg.settings['intro_w'],cfg.settings['intro_h']))
            self.img['background'] = pygame.image.load("assets\\img\\intro_background.jpg").convert()

            if not(self.music):
                self.music = True
                pygame.mixer.init()
                sound = pygame.mixer.Sound(sounds.sounds['music'])
                sound.set_volume(0.1)
                sound.play()

        # écran de chargement
        elif(n == 1):
            self.scene = 1
            self.fps = 30
            self.timeout = 0
            
            pygame.mixer.stop()
            self.music = False
            self.display = pygame.display.set_mode((cfg.settings['game_w'],cfg.settings['game_h']))

        # scène d'accueil : section multijoueurs
        elif(n == 2):
            self.scene = 2
            self.fps = 30
            
            self.img['background'] = pygame.image.load("assets\\img\\intro_background.jpg").convert()

        # table de jeu    
        elif(n == 3):
            self.scene = 3
            self.fps = 60
            
            self.player.ready = True
            self.img['background'] = pygame.image.load("assets\\img\\game_background.jpg").convert()

            for i in range(1,7):
                self.img['dice_{}'.format(i)] = pygame.transform.scale(pygame.image.load("assets\\img\\dice_{}.png".format(i)).convert_alpha(), (100,100))

        # menu principal lors du jeu en cours    
        elif (n == 4):
            self.scene = 4
            self.fps = 30

        else:
            print('? scene')
            
        if not(self.scene == -1):
            self.loop()
            
    def draw(self, method, *args):
        '''
            text()
            
            # Draw a text where you want
            # if you provide w and h arguments, so it will center text in the box provided
            
            Parameters:
                0) text, font, size, color
                1) x, y, (w, h)*
        '''
        def text(args):
            screen = args[0]
            
            if (len(args[2]) > 2):
                center = True
                x, y, w, h = args[2]
            else:
                center = False
                x, y = args[2]
            
            # init it
            font = pygame.font.SysFont(args[1][1], args[1][2])
            text = font.render(args[1][0], True, args[1][3])
            
            if (center):
                tw, th = text.get_rect()[2:]
                x += ((w - tw)/2)
                y += ((h - th)/2)
            
            # draw it
            screen.blit(text, (x,y))
            
        '''
            background()
            
            # Draw a background where you want
            
            Parameters:
                0) x, y, w, h
                1) colors.colors : normal, focused
                2) image
        '''
        def background(args):
            screen = args[0]

            if not(len(args) == 4):
                back = pygame.Surface((args[1][2],args[1][3]), pygame.SRCALPHA)
                back = back.convert()

                if (len(args[2]) > 1):
                    if (mouse_on_it((screen, args[1]))):
                        back.fill(args[2][1])
                    else:
                        back.fill(args[2][0])
                else:
                    back.fill(args[2][0])

                screen.blit(back, (args[1][0], args[1][1]))
            else:
                back = args[3].get_rect()
                back = back.move((args[1][0], args[1][1]))
                
                screen.blit(args[3], back)

        '''
            button()
            
            # Draw a button where you want
            # Notice that it centers the text in the box
            
            Parameters:
                0) id !
                1) text, font, size, color
                2) x, y, w, h
                3) colors.colors : normal, focused
                4) action
        '''
        def button(args):
            screen = args[0]
            
            # init it
            test = [x for x in self.buttons if x[0] == args[1]]
            if not(len(test) > 0):
                self.buttons.append([args[1], args[3], args[5]])
                
            # draw it
            background((screen, args[3], args[4]))
            text((screen, args[2], args[3]))

        def removeButton(args):
            screen = args[0]
            idd = args[1]

            test = [x for x in self.buttons if x[0] == idd]
            self.buttons.pop(self.buttons.index(test[0]))
            
        '''
            table()
            
            # Draw a table with content... idk
            
            Parameters:
                0) font, size
                1) x, y, w, h
                2) colors.colors: head_color, row
                3) content[]
                    -> text, color
        '''   
        def table(args):
            screen = args[0]
            
            # init it
            x, y0, w, h = args[2]
            n = len(args[4])
            y0 -= 2 * n
            
            # draw it
            for i, elem in enumerate(args[4]):
                y = int(y0 + (h / n) * (i+1) + (2*i))
                
                background((screen, (x,y,w,(h/n)), args[3][(i > 0)]))
                text((screen, (elem[0], *args[1], elem[1]), (x,y,w,(h/n))))
            
        def mouse_on_it(args):            
            screen = args[0]
            x, y, w, h = args[1]
            mx, my = pygame.mouse.get_pos()
            
            if (((mx >= x) and (mx <= (x+w))) and ((my >= y) and (my <= (y+h)))):
                return True
            else:
                return False
            
        args = list(args)
        args.insert(0, self.display)
        
        temp = locals()[method](args)
        return temp
        
    def handleScene(self):
        # scène d'accueil : sélection du mode
        if (self.scene == 0):
            # background
            self.display.blit(self.img['background'],[0,0])
            
            # buttons
            self.draw("button", 0, ("Solo","Roboto",64,colors.colors['white']), (50, 60, (cfg.settings['intro_w']/2 - 65), 90), (colors.colors['l_black'], colors.colors['l_green']), "self.player.game.newPlayer('computer', True)\nself.loadScene(1)")
            self.draw("button", 1, ("Duo (WIP)","Roboto",64,colors.colors['white']), ((cfg.settings['intro_w']/2 + 15), 60, (cfg.settings['intro_w']/2 - 65), 90), (colors.colors['l_black'], colors.colors['l_green']), "self.loadScene(2)")
            
            # credits
            self.draw("text", ("Créé par Nicolas HENOCQUE, Emile BOULANGER & Maxime KMIEC (TS1)","Roboto",18,colors.colors['white']), (5,cfg.settings['intro_h'] - 30))

        # écran de chargement
        elif (self.scene == 1):
            # background
            #self.display.blit(self.img['background'],[0,0])
            self.display.fill(colors.colors['white'])
            
            self.draw("text", ("Chargement en cours","Roboto",32,colors.colors['black']), (0,0,cfg.settings['game_w'],cfg.settings['game_h']))
            
            self.timeout += 1
            if (self.timeout >= (1*self.fps)):
                self.loadScene(3)
                self.timeout = None

        # scène d'accueil : section multijoueurs
        elif (self.scene == 2):
            # background
            self.display.blit(self.img['background'],[0,0])
            
            # buttons
            self.draw("text", ("Recherche de parties sur le réseau...","Roboto",32,colors.colors['white']), (0,0,cfg.settings['intro_w'],cfg.settings['intro_h']))
        
        # table de jeu
        elif (self.scene == 3):
            # background
            self.display.blit(self.img['background'],[0,0])
            self.draw("background", (20, 28, 180, 80), (colors.colors["transpagray"]))
            
            # text
            self.draw("text", ("Manche {}".format(self.player.game.round), "Roboto", 28, colors.colors['white']), (10,25,200,50))
            self.draw("text", ("{}".format((self.player.game.round_name).upper()), "Roboto Black", 32, colors.colors['white']), (10,70,200,30))
            
            if (not(self.notification)):
                # dynamic
                if (self.player.game.lock):
                    if (self.player.turn):
                        text = "C'est à votre tour !"
                    else:
                        text = "C'est au tour de {}.".format(self.player.game.turn[1])

                    self.draw("text", (text.format(self.player.game.round), "Roboto Black", 28, colors.colors['white']), (20,cfg.settings['game_h']-50))

                    if (self.player.game.round == 1):
                        text = "» Pot: "+str(self.player.game.pot)
                        self.draw("text", (text, "Roboto", 18, colors.colors['white']), (20, 110, 180, 30))

                    if (self.player.turn):
                        self.draw("button", 2, ("Fin de tour","Roboto",28,colors.colors['white']), (cfg.settings['game_w']-180, cfg.settings['game_h']-55, 160, 40), (colors.colors['l_black'], colors.colors['l_green']), "self.player.game.roundNextTurn()\nself.player.dices.shaking = []")

                        if (self.player.dices.combinations == [0,0,0]):
                            self.draw("button", 3, ("Lancer les dés","Roboto",24,colors.colors['white']), (cfg.settings['game_w']/2-100, cfg.settings['game_h']/2-25, 200, 50), (colors.colors['red'], colors.colors['red']), "self.player.dices.shake(False)\nself.draw('removeButton',3)")
                        else:
                            x = (cfg.settings['game_w'] - 100 * 3 - 20 * 2) / 2 - 80

                            for i in range(3):
                                if (i > 0): x += 120
                                self.draw("background", (x,(cfg.settings['game_h'] / 2)-50,100,100), (), self.img["dice_{}".format((self.player.dices.get())[i])])
                                
                                if (i in self.player.dices.shaking):
                                    color = colors.colors['l_green']
                                else:
                                    color = colors.colors['white']
                                
                                self.draw("button", (4+i), ("Sélectionner", "Roboto", 12, colors.colors['black']), (x,(cfg.settings['game_h'] / 2)+60, 100, 30), (color, color), "self.player.dices.handleShaking({0})".format(i))

                            if not(self.player.dices.maxShaking == -1):
                                text = "» Relances (max) : "+str(self.player.dices.maxShaking)
                                self.draw("text", (text, "Roboto", 12, colors.colors['white']), (cfg.settings['game_w']-180, (cfg.settings['game_h'] / 2)+10))

                            text = "» Vous avez relancé {} fois".format(self.player.dices.shakedTimes)
                            self.draw("text", (text, "Roboto", 12, colors.colors['white']), (cfg.settings['game_w']-180, (cfg.settings['game_h'] / 2)+30))

                            temp = self.player.dices.maxShaking
                            if ((self.player.dices.shakedTimes < temp) or (temp == -1)):
                                if (len(self.player.dices.shaking) == 0):
                                    color = colors.colors["white"]
                                else:
                                    color = colors.colors["l_green"]
                            else:
                                color = colors.colors["red"]

                            self.draw("button", 11, ("Relancer","Roboto",18,color), (cfg.settings['game_w']-180, (cfg.settings['game_h'] / 2)+60, 160, 30), (colors.colors['l_gray'], colors.colors['l_gray']), "self.player.dices.shake(True)")

                # list
                players_table = []
                for x in self.player.game.players:
                    name = x.name + " ("+str(x.tokens)+")"
                    color = colors.colors["white"]
                    if (x.turn):
                        color = colors.colors["red"]
                    players_table.append((name, color))

                self.draw("table", ("Roboto",18), (cfg.settings['game_w']-160, -8, 150, 80), (colors.colors['black'], colors.colors['black']), players_table)
            else:
                self.draw("text", (self.player.game.msg, "Roboto Black", 28, colors.colors['white']), (0,cfg.settings['game_h']/2-30,cfg.settings['game_w'],30))
        
        # menu principal lors du jeu en cours
        elif (self.scene == 4):
            # background
            self.display.fill(colors.colors['l_gray'])
            
            # text
            self.draw("text", ("JEU EN PAUSE","Roboto",32,colors.colors['white']), (cfg.settings['game_w']/2-30,40,60,40))
            
            # buttons
            self.draw("button", 7, ("Reprendre","Roboto",24,colors.colors['white']), (cfg.settings['game_w']/2-150, 120, 300, 50), (colors.colors['l_black'], colors.colors['l_green']), "self.loadScene(3)")
            self.draw("button", 8, ("Règles du jeu","Roboto",24,colors.colors['white']), (cfg.settings['game_w']/2-150, 180, 300, 50), (colors.colors['l_black'], colors.colors['l_green']), "self.loadScene(3)")
            self.draw("button", 9, ("Paramètres","Roboto",24,colors.colors['white']), (cfg.settings['game_w']/2-150, 240, 300, 50), (colors.colors['l_black'], colors.colors['l_green']), "self.loadScene(3)")
            self.draw("button", 10, ("Quitter","Roboto",24,colors.colors['white']), (cfg.settings['game_w']/2-150, 300, 300, 50), (colors.colors['l_black'], colors.colors['l_green']), "self.leaving = True\nself.player.leave()")
        else:
            print('erreur')

    # Gère les événements du clavier, souris        
    def keyHandler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break
            elif event.type == pygame.MOUSEBUTTONUP:
                if (self.scene in [0,3,4]):
                    if (not(self.notification) or self.scene == 4):
                        for x in self.buttons:
                            if (self.draw("mouse_on_it",x[1])):
                                exec(x[2])
                                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if (self.scene == 2):
                        self.loadScene(0)
                        break
                        
                    if (self.scene == 3):
                        self.loadScene(4)
                        break
                        
                    if (self.scene == 4):
                        self.loadScene(3)
                        break

    # Handler: Boucle Pygame
    def loop(self):
        self.doloop = True

        while self.doloop:
            self.keyHandler()
            self.handleScene()

            pygame.display.update()
            self.clock.tick(self.fps)

            pygame.display.flip()
            sys.stdout.flush()