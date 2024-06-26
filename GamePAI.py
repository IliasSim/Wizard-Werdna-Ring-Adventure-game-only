import sys
import GameSettings as settings
from GameMap import GameMap
import pygame
from GameMapGraphics import GameMapGraphics
from Games_items import HelthPotion,ManaPotion,Staff,Sword,Werdna_Ring
from Warrior import Warrior
from Wizard import Wizard
from Enemy import Enemy
import GameEnum
import random
from Tile import Tile
import numpy as np
import gc
import numpy as np
import os
import cv2 
from matplotlib import pyplot as plt
eps = np.finfo(np.float16).eps.item()

class GamePAI():
    '''GamePAi is a class that creates an instance of the game and initialize the basic features of the game.'''
    def __init__(self,playerType,playerName,xPixel,yPixel,screenFactor,depict,game,playHP,seeded,torch,agent_i,frame_stack,only_cnn,gray_scale):
        self.agent_i = agent_i
        if agent_i<=4:
            x= 300*agent_i + 200
            y= 100
        if agent_i>=4:
            x= 300*agent_i - 1000
            y= 400
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d"%(x,y)
        self.seed = game
        self.additemRandom = game
        self.seeded = seeded
        self.playHP = playHP
        self.xPixel = xPixel
        self.yPixel = yPixel
        self.screenFactor = screenFactor
        self.cave = 0
        self.playerType = playerType
        self.playerName = playerName
        self.total_reward = []
        self.buffer_size = 15
        self.killNo = 0
        self.torch = torch
        self.only_cnn = only_cnn
        self.grayscale = gray_scale
        settings.screenFactor = screenFactor
        settings.mapWidth = int(self.xPixel/3)*screenFactor
        settings.mapHeigth = int(self.yPixel/3)*screenFactor
        settings.xtile = int(settings.mapWidth/(4*screenFactor))
        settings.ytile = int(settings.mapHeigth/(4*screenFactor))
        settings.tiles = [[0]*settings.ytile for i in range(settings.xtile)]
        for y in range(settings.ytile):
            for x in range(settings.xtile):
                settings.tiles[x][y] = Tile(x,y)
        self.depict = depict
        self.steps = 0
        self.rest = 0
        self.reward = 0
        #random.seed(seed)
        if self.screenFactor == 3:
            width_pading = 150
            height_pading = 70
        if self.screenFactor == 1:
            width_pading = 72
            height_pading = 32
        if self.screenFactor == 0.5:
            width_pading = 36
            height_pading = 16
        
        if depict == True:
            self.screen = pygame.display.set_mode((int(settings.mapWidth+width_pading), int(settings.mapHeigth+height_pading)))
        if depict == False:
            self.screen = pygame.Surface((settings.mapWidth+width_pading, settings.mapHeigth+height_pading))
        #if self.screenFactor == 1:
            #if depict == True:
                #self.screen = pygame.display.set_mode((settings.mapWidth+32, settings.mapHeigth+24))
            #if depict == False:
                #self.screen = pygame.Surface((settings.mapWidth+32, settings.mapHeigth+24))
        self.gamegraphics = GameMapGraphics(self.screen)
        self.map = GameMap(self.seeded,self.seed)
        if frame_stack >4:
            frame_stack = 4
        self.frame_stack = frame_stack
        pygame.init()         
        if not self.playHP:
            settings.enemies = []
            settings.game_text = []
            if playerType == 1:
                self.player = Warrior()
            if playerType == 2:
                self.player = Wizard()
            self.player.name = playerName
        if self.playHP:
            font = pygame.font.Font('freesansbold.ttf', 12)
            text = font.render("Please select the type of the player (Warrior or Wizard). Press 1 for Warrior or 2 for Wizard.", True, (255,0,0), (0,0,0))
            textRect = text.get_rect()
            textRect.center = ((settings.mapWidth+150)/2,(settings.mapHeigth+70)/2)
            self.screen.blit(text, textRect)
            pygame.display.set_caption("Wizard Werdna Ring")
            pygame.display.flip()
            writeText = True
            while writeText:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
            
                        if event.key == pygame.K_1:
                            self.player = Warrior()
                            writeText = False
                        if event.key == pygame.K_2:
                            self.player = Wizard()
                            writeText = False   

            text = font.render("Please enter the name of the player and press enter: ", True, (255,0,0), (0,0,0))
            textRect = text.get_rect()
            input_rect = pygame.Rect((settings.mapWidth+150)/2-100, (settings.mapHeigth+70)/2 + 20, 200, 20)
            textRect.center = ((settings.mapWidth+150)/2,(settings.mapHeigth+70)/2)
            self.screen.fill(pygame.Color("black"))
            user_text = ''
            self.screen.blit(text, textRect)
            pygame.display.set_caption("Wizard Werdna Ring")
            pygame.display.flip()
            writeText = True
            while writeText:
                nameinput = True
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            while nameinput:
                                self.player.name = user_text
                                nameinput = False
                                writeText = False           

                        if event.key == pygame.K_BACKSPACE:
                            user_text = user_text[:-1]
  
                        if event.key != pygame.K_BACKSPACE and event.key != pygame.K_RETURN:
                            user_text += event.unicode
                pygame.draw.rect(self.screen, (255,255,0), input_rect)
                text_surface = font.render(user_text, True, (255, 0, 0))
                self.screen.blit(text_surface, (input_rect.x+5, input_rect.y+5))
                input_rect.w = max(100, text_surface.get_width()+10)
                pygame.display.flip()
        text = self.player.name + ' welcome to the Wizard Werdna Ring adventure. Try to find the ring and win the Game.'
        settings.addGameText(text)
        self.printText()
        self.makeMap(self.cave)
        self.printPlayerStatus()
        if depict == True:
            if self.screenFactor == 1:
                pygame.display.set_caption(str(game))
                pygame.display.flip()
            else:
                pygame.display.set_caption("Wizard Werdna Ring "+str(game+1))
                pygame.display.flip()
        copy_list = self.copy_tiles()
        copy_enemie_list = self.copy_enemis()
        self.afterMoveDepiction(copy_list,copy_enemie_list,True)
        if playHP:
            self.run_gameHP()

    def afterMoveDepiction(self,copy_list,copy_enemie_list,enter_cave):
        '''This function refreshes the information on the game screen'''
        self.printText()
        self.printPlayerStatus()
        self.drawscreen(copy_list,copy_enemie_list,enter_cave) 

    def gameOverHP(self):
        '''Checks if the player is dead and reinitilize the game creating a new instance of the GamePAI class.'''
        if self.player.hitPoints <= 0:
            print(self.player.name,'is dead. Game Over ' + str(settings.gameCount) + ' episode rewards ' + str(self.reward))
            pygame.quit()
            sys.exit()
            

    def gameOver(self,s):
        '''Checks if the player is dead and reinitilize the game creating a new instance of the GamePAI class.'''
        done = False
        if self.player.hitPoints <= 0:
            done = True
            settings.gameCount = settings.gameCount + 1
            pygame.quit()
            #sys.exit()
            if s % 100 == 0:
                self.__init__(self.playerType,self.playerName,self.xPixel,self.yPixel,self.screenFactor,True,s,False)
            else:
                self.__init__(self.playerType,self.playerName,self.xPixel,self.yPixel,self.screenFactor,True,s,False)
            gc.collect()
        return done

    def drawscreen(self,copy_list,copy_enemie_list,enter_cave):
        '''This function draws the map of the game'''
        # tiles = settings.tiles.copy()
        self.gamegraphics.drawMap(copy_list,self.frame_stack,enter_cave)
        self.gamegraphics.drawItem()
        self.gamegraphics.enemyDepiction(copy_enemie_list,self.frame_stack,enter_cave)
        self.gamegraphics.drawPlayer(self.player.currentPositionX, self.player.currentPositionY,self.frame_stack,enter_cave)
        # state = pygame.surfarray.array3d(self.screen)
        # # avgs = [[(r*0.298 + g*0.587 + b*0.114) for (r,g,b) in col] for col in state]
        # state = np.array([[[avg,avg,avg] for avg in col] for col in avgs])
        # pygame.surfarray.make_surface(state)
        if self.depict == True:
            pygame.display.update()

    def makeMap(self,cave):
        '''Creates the map of the game.'''
        precentage = 0
        makemap = True
        if self.seeded:
            seed = self.seed + cave*10000
            while makemap:
                random.seed(seed)
                precentage = random.random()
                # print(seed,precentage)
                if 0.35 < precentage <= 0.55:
                    makemap = False
                else:
                    seed += 1
        else:
            while makemap:
                precentage = random.random()
                if 0.35 < precentage <= 0.55:
                    makemap = False
        if cave >= 0:
            self.map.refreshTilesSettings()
        self.map.MakeMAp(precentage, self.player, cave)
        self.player.playerVisibility(self.player.currentPositionX, self.player.currentPositionY)

    def countHealthPotion(self):
        '''Counts the health potions player posses.'''
        count = 0
        if self.player.inventory != []:
            for item in self.player.inventory:
                if isinstance(item, HelthPotion):
                    count = count + 1
        return count
 
    def countManaPotion(self):
        '''Counts the health potions player posses.'''
        count = 0
        if self.player.inventory != []:
            for item in self.player.inventory:
                if isinstance(item,ManaPotion):
                    count = count + 1
        return count

    def printPlayerStatus(self):
        '''Prints the player name and status'''
        if self.screenFactor == 1:
            font_int = 7
        if self.screenFactor == 0.5:
            font_int=3
        if self.screenFactor == 3:
            font_int = 12
        font = pygame.font.Font("freesansbold.ttf", font_int)
        if isinstance(self.player, Warrior):
            text = font.render('Warrior', True, (255,0,0), (0,0,0))
        if isinstance(self.player, Wizard):
            text = font.render('Wizard', True, (255,0,0), (0,0,0))
        text1 = font.render(self.player.name, True, (255,0,0), (0,0,0))
        text2 = font.render("HP" + str(self.player.hitPoints) + " /" + str(self.player.maxHitPoints), True, (255,0,0), (0,0,0)) 
        if isinstance(self.player, Warrior):
            text25 = font.render("MP 0/0" , True, (255,0,0), (0,0,0))    
        if isinstance(self.player, Wizard):
            text25 = font.render("MP" + str(self.player.manaPoints) + "/" + str(self.player.maxManaPoints) , True, (255,0,0), (0,0,0))  
        if self.player.weapon == None:
            text3 = font.render("Weapon: None " , True, (255,0,0), (0,0,0))
        else:
            text3 = font.render("Weapon: " + self.player.weapon.name , True, (255,0,0), (0,0,0))
        if isinstance(self.player, Warrior):
            text4 = font.render('Strength: ' + str(self.player.baseStrength), True, (255,0,0), (0,0,0))
        if isinstance(self.player, Wizard):
            text4 = font.render('Intelligence: ' + str(self.player.getBaseIntelligence()), True, (255,0,0), (0,0,0))
        text5 = font.render('Damage: ' + str(self.player.getAttackDamage()), True, (255,0,0), (0,0,0))
        text6 = font.render('Potions: ' + str(self.countHealthPotion())+ "(H) /" + str(self.countManaPotion()) + "(M)", True, (255,0,0), (0,0,0))
        text7 = font.render('Level: ' + str(self.player.getLevel()), True, (255,0,0), (0,0,0))
        text8 = font.render('XP: ' + str(self.player.experiencePoints), True, (255,0,0), (0,0,0)) 
        text9 = font.render('Cave: ' + str(self.cave), True, (255,0,0), (0,0,0))
        if self.screenFactor ==3:
            self.screen.blit(text, (settings.mapWidth,8))
            self.screen.blit(text1, (settings.mapWidth,21))
            self.screen.blit(text2, (settings.mapWidth,34))
            self.screen.blit(text25, (settings.mapWidth,47))
            self.screen.blit(text3, (settings.mapWidth,60))
            self.screen.blit(text4, (settings.mapWidth,73))
            self.screen.blit(text5, (settings.mapWidth,86))
            self.screen.blit(text6, (settings.mapWidth,99))
            self.screen.blit(text7, (settings.mapWidth,112))
            self.screen.blit(text8, (settings.mapWidth,125))
            self.screen.blit(text9, (settings.mapWidth,138))
        if self.screenFactor ==1:
            self.screen.blit(text, (settings.mapWidth,8))
            self.screen.blit(text1, (settings.mapWidth,17))
            self.screen.blit(text2, (settings.mapWidth,26))
            self.screen.blit(text25, (settings.mapWidth,35))
            self.screen.blit(text3, (settings.mapWidth,44))
            self.screen.blit(text4, (settings.mapWidth,53))
            self.screen.blit(text5, (settings.mapWidth,62))
            self.screen.blit(text6, (settings.mapWidth,71))
            self.screen.blit(text7, (settings.mapWidth,80))
            self.screen.blit(text8, (settings.mapWidth,89))
            self.screen.blit(text9, (settings.mapWidth,98))
        if self.screenFactor ==0.5:
            self.screen.blit(text, (settings.mapWidth,8))
            self.screen.blit(text1, (settings.mapWidth,14))
            self.screen.blit(text2, (settings.mapWidth,20))
            self.screen.blit(text25, (settings.mapWidth,26))
            self.screen.blit(text3, (settings.mapWidth,32))
            self.screen.blit(text4, (settings.mapWidth,38))
            self.screen.blit(text5, (settings.mapWidth,44))
            self.screen.blit(text6, (settings.mapWidth,50))
            self.screen.blit(text7, (settings.mapWidth,56))
            self.screen.blit(text8, (settings.mapWidth,62))
            self.screen.blit(text9, (settings.mapWidth,68))




    def printText(self):
        '''Prints the game Log on the screen'''
        if self.screenFactor ==1:
            font_int = 5
            space_int = 6
        if self.screenFactor ==0.5:
            font_int = 3
            space_int = 3
        if self.screenFactor ==3:
            font_int = 12
            space_int = 13
        font = pygame.font.Font('freesansbold.ttf', font_int)
        self.screen.fill(pygame.Color("black"))
        for i in range(len(settings.game_text)):
            text = font.render(settings.game_text[i], True, (255,0,0), (0,0,0))
            self.screen.blit(text,(0,settings.mapHeigth+(space_int*i)))
    
    def enemyMove(self,attacked_by_an_enemy):
        '''Determines the movement of the enemy after the movement of the player.'''
        attacking_enemies = 0
        if settings.enemies != []:
            
            for enemy in settings.enemies:
                if enemy.minDistance(self.player,enemy.enemyCurrentPossitionX,enemy.enemyCurrentPossitionY) == 0:
                    attacking_enemies += 1
                    attacked_by_an_enemy = True
                enemy.enemyMovement(self.player)
        if self.playHP:
            self.gameOverHP()
        return attacked_by_an_enemy,attacking_enemies

    def copy_tiles(self):
        copy_list = [[0]*settings.ytile for i in range(settings.xtile)]
        for y in range(settings.ytile):
            for x in range(settings.xtile):
                copy_list[x][y] = Tile(x,y)
        for y in range(settings.ytile):
            for x in range(settings.xtile):
                if settings.tiles[x][y].ground == GameEnum.GroundType.wall:
                    copy_list[x][y].ground = GameEnum.GroundType.wall
                if settings.tiles[x][y].ground == GameEnum.GroundType.floor:
                    copy_list[x][y].ground = GameEnum.GroundType.floor
                if settings.tiles[x][y].ground == GameEnum.GroundType.stairs:
                    copy_list[x][y].ground = GameEnum.GroundType.stairs
                if settings.tiles[x][y].visibility == GameEnum.VisibilityType.unknown:
                    copy_list[x][y].visibility = GameEnum.VisibilityType.unknown
                if settings.tiles[x][y].visibility == GameEnum.VisibilityType.fogged:
                    copy_list[x][y].visibility = GameEnum.VisibilityType.fogged
                if settings.tiles[x][y].visibility == GameEnum.VisibilityType.visible:
                    copy_list[x][y].visibility = GameEnum.VisibilityType.visible
                if settings.tiles[x][y].occupancy == True:
                    copy_list[x][y].occupancy = True
                if settings.tiles[x][y].store != None:    
                    item = settings.tiles[x][y].store
                    copy_list[x][y].store = item
        return copy_list
    
    def copy_enemis(self):
        copy_enemie_list = []
        for enemy in settings.enemies:
            x,y = enemy.enemyCurrentPossitionX,enemy.enemyCurrentPossitionY
            name    = enemy.name
            copy_enemie_list.append([x,y,name])
        return copy_enemie_list

    def playerAction(self,action):
        '''This function determines the actions of the player/agent.'''
        #the folling code determines the movement of the payer in the map.
        move_new_area,vissible_stairs,move_already_discovered_area = False,False,False
        move_towards_wall,pick_potion,attack_an_enemy,attack_aimlessly = False,False,False,False
        Kill_an_enemy,use_rest_correctly,use_rest_aimlessly = False,False,False
        use_health_potion_correctly,use_health_potion_aimlessly,use_mana_potion_correctly = False,False,False
        use_mana_potion_aimlessly,enter_new_cave,pick_weapon,pick_weapon_aimlessly = False,False,False,False
        attacked_by_an_enemy,win_game,gain_hp,gain_mp = False,False,False,False
        attacking_enemies = 0
        self.reward = 0
        initialHitPoint = self.player.hitPoints
        if isinstance(self.player, Wizard):
            initialManaPoints = self.player.manaPoints
        if action <= 3:
            if action == 0:
                movementType = GameEnum.MovementType.up
            if action == 1:
                movementType = GameEnum.MovementType.right
            if action == 2:
                movementType = GameEnum.MovementType.down
            if action == 3:
                movementType = GameEnum.MovementType.left
            Xposition = self.player.currentPositionX
            Yposition = self.player.currentPositionY
            inventory = len(self.player.inventory)
            unknownTille = self.map.countUknownTile()
            self.player.playerMovement(movementType)
            if Xposition != self.player.currentPositionX or Yposition != self.player.currentPositionY:
                self.steps += 1
                # print(self.steps)
                if unknownTille > self.map.countUknownTile():
                    move_new_area = True
                else:
                    move_already_discovered_area = True
                if len(self.player.inventory) > inventory:
                    pick_potion = True
                self.map.createEnemies(self.player,movementType,self.steps)
                attacked_by_an_enemy,attacking_enemies = self.enemyMove(attacked_by_an_enemy)
                enter_new_cave,win_game = self.enterCave(self.cave,enter_new_cave,win_game)
                # self.afterMoveDepiction()
                if settings.tiles[settings.exitx][settings.exity].visibility == GameEnum.VisibilityType.visible:
                    vissible_stairs = True
            if Xposition == self.player.currentPositionX and Yposition == self.player.currentPositionY:
                move_towards_wall = True
                attacked_by_an_enemy,attacking_enemies = self.enemyMove(attacked_by_an_enemy)  
                # self.afterMoveDepiction()   
        if action == 4:
        #This code chunk adds 4 points to the hp of the player and if the player is wizzard type, adds and 4 point the mp of the player.'''
            oldhitpoints = self.player.hitPoints
            self.rest += 1
            # print(self.rest)
            if isinstance(self.player, Wizard):
                oldmanapoints = self.player.manaPoints
            if settings.tiles[settings.exitx][settings.exity].visibility != GameEnum.VisibilityType.visible and settings.tiles[settings.exitx][settings.exity].visibility != GameEnum.VisibilityType.fogged:
                self.player.rest()
                self.map.createEnemiesRest(self.player,self.rest)
                attacked_by_an_enemy,attacking_enemies = self.enemyMove(attacked_by_an_enemy)
                # self.afterMoveDepiction()
            if  (abs(settings.exitx - self.player.currentPositionX) + abs(settings.exity - self.player.currentPositionY)) > 35 and settings.tiles[settings.exitx][settings.exity].visibility != GameEnum.VisibilityType.unknown:
                self.player.rest()
                self.map.createEnemiesRest(self.player,self.rest)
                attacked_by_an_enemy,attacking_enemies = self.enemyMove(attacked_by_an_enemy)
                # self.afterMoveDepiction()
            if (abs(settings.exitx - self.player.currentPositionX) + abs(settings.exity - self.player.currentPositionY)) < 35 and settings.tiles[settings.exitx][settings.exity].visibility != GameEnum.VisibilityType.unknown:
                text =self.player.name + " don't try to cheat."
                settings.addGameText(text)
                # self.afterMoveDepiction()
            if (self.player.hitPoints - oldhitpoints) == 4:# and self.countHealthPotion() == 0:
                use_rest_correctly = True
            if (self.player.hitPoints - oldhitpoints) == 0: # or self.countHealthPotion() == 0:
                use_rest_aimlessly = True
            if isinstance(self.player, Wizard):
                if  (self.player.manaPoints - oldmanapoints) == 4 and self.countManaPotion() == 0:
                    use_rest_correctly = True
                if  (self.player.manaPoints - oldmanapoints) < 4 or self.countManaPotion() == 0:
                    use_rest_aimlessly = True

        if action == 5:
        #This code chunk consumes one health potion and adds 20 point to the player hp.
            if self.player.inventory != []:
                index = None
                for i in range(len(self.player.inventory)):
                    if isinstance(self.player.inventory[i], HelthPotion):
                        index = i
                if index != None:
                    item = self.player.inventory.pop(index)
                    oldhitpoints = self.player.hitPoints
                    self.player.use(item)           
                if (self.player.hitPoints - oldhitpoints) == 20:
                    use_health_potion_correctly = True
                if (self.player.hitPoints - oldhitpoints) < 20:
                    use_health_potion_aimlessly = True
            else :
                text = self.player.name + " doesn't posses health potion."
                settings.addGameText(text)
                use_health_potion_aimlessly = True
            attacked_by_an_enemy,attacking_enemies = self.enemyMove(attacked_by_an_enemy)
            # self.afterMoveDepiction()

        if action == 6:
        #This code chunk consumes one mana potion and adds 20 points to the player mp, if the payer is a wizzard.
            if isinstance(self.player, Warrior):
                    text =self.player.name + " can't uses mana potion."
                    settings.addGameText(text)
                    use_mana_potion_aimlessly = True

            if isinstance(self.player, Wizard) and self.player.inventory != []:
                index = None          
                for i in range(len(self.player.inventory)):
                    if isinstance(self.player.inventory[i],ManaPotion):
                        index = i
                if index != None:
                    item = self.player.inventory.pop(index)
                    oldmanapoints = self.player.manaPoints
                    self.player.use(item)
                if  (self.player.manaPoints - oldmanapoints) == 20:
                    use_mana_potion_correctly = True
                    
                if  (self.player.manaPoints - oldmanapoints) < 20:
                    use_mana_potion_aimlessly = True
                if index == None:
                    text =self.player.name + " doesn't posses mana potion."
                    settings.addGameText(text)
                    use_mana_potion_aimlessly = True

            attacked_by_an_enemy,attacking_enemies = self.enemyMove(attacked_by_an_enemy)
            # self.afterMoveDepiction()   
                
        if action == 7:
        #This code chunk performs the attack of the player.
            index = self.player.enemyToAttack()
            if index == None:
                attack_aimlessly = True
            if index != None:
                enemy = settings.enemies[index]
                boolean = self.player.attack(enemy)
                if boolean:
                    attack_an_enemy = True
                if boolean and enemy.hitPoints <= 0:
                    self.killNo += 1
                    self.additemRandom += 100
                    # print(self.additemRandom)
                    Kill_an_enemy = True
                    if self.seeded:
                        random.seed(self.additemRandom)
                    r = random.random()
                    # print(r)
                    if r <= 0.25:
                        self.map.addItem(self.player, enemy.enemyCurrentPossitionX, enemy.enemyCurrentPossitionY,self.cave,self.killNo)
                if boolean and enemy.hitPoints <= 0 and self.player.experiencePoints <= 13999:
                    settings.tiles[enemy.enemyCurrentPossitionX][enemy.enemyCurrentPossitionY].occupancy = False
                    settings.enemies.pop(index)
                    text = self.player.name + " kills " + enemy.name + " and earn " + str(enemy.XPreturn) + " XP points"
                    settings.addGameText(text)
                    old_level = self.player.getLevel()
                    self.player.addXP(enemy.XPreturn)
                    if old_level < self.player.getLevel() and self.player.hitPoints <= (self.player.maxHitPoints*(2/3)):
                        for i in range(self.countHealthPotion()//2): 
                            index = None
                            for i in range(len(self.player.inventory)):
                                if isinstance(self.player.inventory[i], HelthPotion):
                                    index = i
                                
                            if index != None:
                                item = self.player.inventory.pop(index)
                                self.player.use(item)
            attacked_by_an_enemy,attacking_enemies = self.enemyMove(attacked_by_an_enemy)
            # self.afterMoveDepiction()

        if action == 8:
            #This code chunk allows the player to pick weapon from the map.'''
            if settings.tiles[self.player.currentPositionX][self.player.currentPositionY].store != None:
                weaponPicked = False
                if isinstance(self.player, Warrior) and isinstance(settings.tiles[self.player.currentPositionX][self.player.currentPositionY].store, Sword):
                    sword = settings.tiles[self.player.currentPositionX][self.player.currentPositionY].store
                    settings.tiles[self.player.currentPositionX][self.player.currentPositionY].store = self.player.dropWeapon()
                    weaponPicked = True
                    self.player.setWeapon(sword)
                    pick_weapon = True
                if isinstance(self.player, Wizard) and isinstance(settings.tiles[self.player.currentPositionX][self.player.currentPositionY].store, Staff):
                    staff = settings.tiles[self.player.currentPositionX][self.player.currentPositionY].store
                    settings.tiles[self.player.currentPositionX][self.player.currentPositionY].store = self.player.dropWeapon()
                    weaponPicked = True
                    self.player.setWeapon(staff)
                    pick_weapon = True
                if not weaponPicked:
                    pick_weapon_aimlessly =True
                    
            else:
                pick_weapon_aimlessly =True
            attacked_by_an_enemy,attacking_enemies = self.enemyMove(attacked_by_an_enemy)
            # self.afterMoveDepiction()
        copy_list = self.copy_tiles()
        copy_enemie_list = self.copy_enemis()
        self.afterMoveDepiction(copy_list,copy_enemie_list,enter_new_cave)
        screen = self.screen
        state = pygame.surfarray.array3d(screen)
        # print(state.shape)
        state = state.swapaxes(0,1)
        
        if self.only_cnn:
            state = state
        else:
            state = state[:int(settings.mapHeigth),:int(settings.mapWidth)]
        # print(state.shape)
        if self.grayscale:
            state = cv2.cvtColor(state, cv2.COLOR_RGB2GRAY)
            state = np.expand_dims(state, -1)
        #print(state.shape)
        

        # state = state/255
        # state = state.astype('float32')
        #state =  np.expand_dims(state, axis=0)
        manapoints = 0
        maxmanapoints = 0
        manapotion = 0
        inteligence = 0
        if isinstance(self.player,Warrior):
            base_int_str = self.player.baseStrength
        if isinstance(self.player, Wizard):
            manapoints = self.player.manaPoints
            maxmanapoints = self.player.maxManaPoints
            manapotion = self.countManaPotion()
            base_int_str = self.player.baseIntelligence
        if self.player.weapon != None:
            weaponencode = 1
        else :
            weaponencode = 0
        playerstatus = np.array([weaponencode,self.player.hitPoints/self.player.maxHitPoints,self.player.maxHitPoints/100,self.player.getAttackDamage()/45,self.countHealthPotion()/30,self.player.getLevel()/5,self.player.experiencePoints/14000,self.cave/10],dtype=np.float32)
        # playerstatus = np.array([self.player.hitPoints,self.player.maxHitPoints,base_int_str,inteligence,manapoints,maxmanapoints,manapotion,self.countHealthPotion(),self.player.getAttackDamage(),self.player.getLevel()],dtype=np.int32)
        # playerstatus = playerstatus/(max(playerstatus))
        textList = []
        for text in settings.game_text:
            textNname = text[len(self.player.name):]
            textList.append(textNname)        
        textArray = self.gameVocab(textList)
        done = False
        if self.player.hitPoints <= 0:
            done = True
        if initialHitPoint < self.player.hitPoints:
            gain_hp = True
        if isinstance(self.player,Wizard):
            if initialManaPoints < self.player.manaPoints:
                gain_mp = True
        if self.torch:
            state = np.reshape(state,(state.shape[2],state.shape[0],state.shape[1]))
        self.rewards(move_new_area,vissible_stairs,move_already_discovered_area,move_towards_wall,
                pick_potion,attack_an_enemy,attack_aimlessly,Kill_an_enemy,use_rest_correctly,use_rest_aimlessly,
                use_health_potion_correctly,use_health_potion_aimlessly,use_mana_potion_correctly,
                use_mana_potion_aimlessly,enter_new_cave,pick_weapon,pick_weapon_aimlessly,
                attacked_by_an_enemy,win_game,gain_hp,gain_mp,attacking_enemies)
        # print(state.shape)
        if self.only_cnn:
            return state, self.reward, done
        else:
            return state, self.reward, playerstatus,  textArray, done
    
    def rewards(self,move_new_area,vissible_stairs,move_already_discovered_area,move_towards_wall,
                pick_potion,attack_an_enemy,attack_aimlessly,Kill_an_enemy,use_rest_correctly,use_rest_aimlessly,
                use_health_potion_correctly,use_health_potion_aimlessly,use_mana_potion_correctly,
                use_mana_potion_aimlessly,enter_new_cave,pick_weapon,pick_weapon_aimlessly,
                attacked_by_an_enemy,win_game,gain_hp,gain_mp,attacking_enemies):
        # movemen rewards
        if move_new_area:
            self.reward += 20
        if vissible_stairs:
            self.reward += 20
        if move_already_discovered_area:
            self.reward += 1
        if move_towards_wall:
            self.reward -= 1
        if pick_potion:
            self.reward += 100
        # fight with enemy
        if attack_an_enemy:
            self.reward += 10
        if attack_aimlessly:
            self.reward -= 0.1
        if Kill_an_enemy:
            self.reward += 100
        if attacked_by_an_enemy:
            self.reward -= 1*attacking_enemies 
        # use rest
        if use_rest_aimlessly:
            self.reward -= 0.1
        if use_rest_correctly:
            self.reward += 10
        # use potion
        if use_health_potion_correctly:
            self.reward += 100
        if use_health_potion_aimlessly:
            self.reward -= 0.1
        if use_mana_potion_correctly:
            self.reward += 100
        if use_mana_potion_aimlessly:
            self.reward -= 0.1
        # enter cave win game
        if enter_new_cave or win_game:
            self.reward += 500
        # pick weapon
        if pick_weapon:
            self.reward += 100
        if pick_weapon_aimlessly:
            self.reward -= 0.1
        # gain hp mp
        if gain_hp:
            self.reward += 10
        if gain_mp:
            self.reward += 1
        if self.player.hitPoints <= 0:
            self.reward -= 1
        self.reward = np.float32(self.reward)

        


        


        


    def gameVocab(self,textList):
        array = np.array([])
        list1 = []
        list2 = []
        #sum_text = 0
        game_vocab = {'welcome':100,'to':1,'the':2,'Wizard':3,'Werdna':4,'Ring':5,'adventure.':6,
        'Try':7,'to':8,'find':9,'Ring':10,'and':11,'win':12,'Game.':13,"don't":14,'try':15,'cheat.':16,
        "doesn't":17,'posses':18,'health':19,'potion.':20,"can't":21,'uses':22,'mana':22,'kills':23,'earn':24,
        'XP':25,'points':26,'enters':27,'cave':28,'No':29,'can':30,'hear':31,'from':32,'east':33,
        'west':34,'north':35,'south':36,'attacked':37,'by':38,'for':39,'damage.':40,'a':41,'an':42,
        'Giant':43,'Rat':44,'Goblin':45,'Slime':46,'Orc':47,'Grunt':48,'Warlord':49,'Skeleton':50,
        'Vampire':51,'Wyrm':52,'changes':53,'level.':54,'New':55,'level':56,'is':57,'HP.':58,'potion':59,
        'MP.':60,'found':61,'press':63,'use':64,'it.':65,'h':66,'m':67,'weapon':68,'type':69,'of':70,
        'p':71,'equip':72,'with':73,'add':74,'which':75,'add':76,'max':77,'HP':78,'MP':79,'player':80,'inteligence':81,
        'earn':82,'attack':83,'strength':84,'east.':85,'west.':86,'north.':87,'south.':89,'ring':90,'Mana':91,'this':92,'Gray':93,
        'Amazing':94,'Deadly':95,'Ancient':96,'Sword':97,'Staff':98,'weapon.':99,'rest':101,'Ettin':102}
        # this code chunk creates a sum input for the model.
        # text = textList[len(textList)-1]
        # text = text.split()
        # for word in text:
            # if word in game_vocab:
               # sum_text += game_vocab[word]
            # else:
                # sum_text += int(word)
        # array_text = np.array(sum_text,dtype=np.int32)
        # array_text = np.reshape(array_text,(1,1))
        #print(array_text,array_text.shape)
        # return array_text
        for text in textList:
            text = text.split()
            list1 = []
            for word in text:
                if word in game_vocab:
                    list1.append(game_vocab[word])
                else:
                    list1.append(int(word))
            if len(list1) < 25:
                for i in range((25-len(list1))):
                    list1.insert(len(list1)+1,0)
            list2.append(list1)
        if len(list2)<5:
            for i in range (5-len(list2)):
                list2.append([0]*25)
        array = np.array(list2,dtype=np.int32)
        #array = np.reshape(array,(1,125))
        #array = np.expand_dims(array, axis=0)
        #array = np.expand_dims(array, axis=0)
        #print(type(array))
        #tfarray = tf.convert_to_tensor(array)
        array = np.reshape(array,(125))
        array = array/102
        #print(sumarray.shape,sumarray)
        array = array.astype('float32')
        return array

    def enterCave(self,cave,enter_new_cave,win_game):
        '''This function Checks if the tile is stair or the tile stores the Werdna Ring. 
        If the tile is stair the player enters a new cave if the tile posses the Werdna ring the player wins and the game ends.'''                
        if settings.tiles[self.player.currentPositionX][self.player.currentPositionY].ground == GameEnum.GroundType.stairs:
            self.cave = self.cave + 1
            self.makeMap(self.cave)
            settings.enemies = []
            text =self.player.name + " enters cave No " + str(cave + 1)
            settings.addGameText(text)
            enter_new_cave = True
            
        if isinstance(settings.tiles[self.player.currentPositionX][self.player.currentPositionY].store, Werdna_Ring):
            print(self.player.name + " found Werdna's Ring!! Congratulation")
            pygame.quit()
            win_game = True
        return enter_new_cave,win_game
                    
    def settingmapWidth(self):
        '''This function returns the pixels of the map x axis.'''
        return settings.mapWidth


    def settingmapHeigth(self):
        '''This function returns the pixels of the map y axis.'''
        return settings.mapHeigth

    def standardize_reward(self,reward):
        '''This function is used for the standardization of the reward.'''
        self.total_reward.append(reward)
        #mean_reward = self.total_reward/episode
        #print(mean_reward)
        #print(episode)
        reward_std = ((reward - np.mean(self.total_reward)) / (np.std(self.total_reward) + eps))
        return reward_std

    def run_gameHP(self):
        '''Thru this function the player can play the game with the keyboard'''
        gameContinues = True
        while gameContinues:
            settings.reward = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.playerAction(3)
                    if event.key == pygame.K_s:
                        self.playerAction(2)
                    if event.key == pygame.K_d:
                        self.playerAction(1)
                    if event.key == pygame.K_w:
                        self.playerAction(0)
                    if event.key == pygame.K_r:
                        self.playerAction(4)
                    if event.key == pygame.K_h:
                        self.playerAction(5)
                    if event.key == pygame.K_m:
                        self.playerAction(6)
                    if event.key == pygame.K_SPACE:
                        self.playerAction(7)
                    if event.key == pygame.K_p:
                        self.playerAction(8)
                    

    
    def initialGameState(self):
        '''Returns the intial state of the game'''
        #print(len(self.buffer_State),len(self.buffer_text),len(self.buffer_playerStatus))
        screen = self.screen
        state = pygame.surfarray.array3d(screen)
        state = state.swapaxes(0,1)
        # print(state1.shape,state.shape)
        if self.only_cnn:
            state = state
        else:
            state = state[:int(settings.mapHeigth),:int(settings.mapWidth)]
        #state = state/255
        if self.grayscale:
            state = cv2.cvtColor(state, cv2.COLOR_RGB2GRAY)
            state = np.expand_dims(state, -1)

        # state = state.astype('float32')
        manapoints = 0
        maxmanapoints = 0
        manapotion = 0
        inteligence = 0
        if isinstance(self.player,Warrior):
            base_int_str = self.player.baseStrength
        if isinstance(self.player, Wizard):
            manapoints = self.player.manaPoints
            maxmanapoints = self.player.maxManaPoints
            manapotion = self.countManaPotion
            base_int_str = self.player.baseIntelligence
        if self.player.weapon != None:
            weaponencode = 1
        else :
            weaponencode = 0
        playerstatus = np.array([weaponencode,self.player.hitPoints/self.player.maxHitPoints,self.player.maxHitPoints/100,self.player.getAttackDamage()/45,self.countHealthPotion()/30,self.player.getLevel()/5,self.player.experiencePoints/14000,self.cave/10],dtype=np.float32)
        textList = []
        for text in settings.game_text:
            textNname = text[len(self.player.name):]
            textList.append(textNname)
        textArray = self.gameVocab(textList)
        if self.torch:
            state = np.reshape(state,(state.shape[2],state.shape[0],state.shape[1]))
        if self.only_cnn:
            return state
        else:
            return state, playerstatus,  textArray



if __name__ == '__main__':
    game = GamePAI(1,'Connan',444,444,0.5,True,1,True,True,False,0,1,True,True)
    
