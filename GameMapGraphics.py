import GameSettings as settings
import GameEnum
import pygame
from Enemies import Vampire,Wyrm,Giant_Rat,Goblin,Gray_Slime,Ettin,Orc_Grunt,Orc_Warlord,Skeleton
from Games_items import HelthPotion,ManaPotion,Werdna_Ring,Staff,Sword
from Tile import Tile
class GameMapGraphics():
    '''The GameMapGraphics class creates the image of game map. 
    Also it creates images of the enemies, the player and the items placed on the map.'''
    def __init__(self,screen):
        self.tilesize=4*settings.screenFactor
        self.tilefilsize= 11/3*settings.screenFactor
        self.rectEnemyPading = 1/3*settings.screenFactor
        self.rectEnemyFill = 3*settings.screenFactor
        self.cycleEnemyPading = 5/3*settings.screenFactor
        self.cycleEnemyFill = 4/3*settings.screenFactor
        self.skeletonfill = 7/3*settings.screenFactor
        self.itemFill = settings.screenFactor
        self.itemPading = 8/3*settings.screenFactor
        self.screen = screen
        self.red = (255,0,0)
        self.darkred = (120,0,0)
        self.yellow = (255,255,0)
        self.blue = (0,0,255)
        self.gray = (127,127,127)
        self.orange = (255,100,10)
        self.lightGray = (211, 211, 211)
        self.green = (0,255,0)
        self.dark_green=(0, 100, 0)
        self.dark_gray = (169, 169, 169)
        self.white = (255,255,255)
        self.magenta = (255,0,230)
        self.black = (0,0,0)
        self.pink = (255,100,180)
        self.royalblue4 = (39,64,139)
        self.royalblue = (65,105,225)
        self.tiles_lists = []
        self.player_positions_list = []
        self.enemies_lists = []
        #print(settings.screenFactor)
        if settings.screenFactor < 1:
            # print('Do I work')
            self.itemFill = 1
            self.itemPading = 0
            self.cycleEnemyFill = 1

        # print(self.tilesize,self.itemFill,self.skeletonfill,self.rectEnemyFill,self.rectEnemyPading)


    def drawMap(self,tiles,frame_stack,enter_cave):
        '''Creates the image of the game map.'''
        if enter_cave:
            self.tiles_lists = []
        self.tiles_lists.append(tiles)
        if len(self.tiles_lists) > frame_stack and self.tiles_lists!= []:
            del self.tiles_lists[0]
        if len(self.tiles_lists) < 1:
            for x in range(settings.xtile):
                for y in range(settings.ytile):   
                    if settings.tiles[x][y].ground == GameEnum.GroundType.floor:
                        if  settings.tiles[x][y].visibility == GameEnum.VisibilityType.unknown:
                            pygame.draw.rect(self.screen, self.black, [x*self.tilesize,y*self.tilesize,self.tilefilsize,self.tilefilsize])
                        if  settings.tiles[x][y].visibility == GameEnum.VisibilityType.visible: 
                            pygame.draw.rect(self.screen, self.red, [x*self.tilesize,y*self.tilesize,self.tilefilsize,self.tilefilsize])
                        if  settings.tiles[x][y].visibility == GameEnum.VisibilityType.fogged:
                            pygame.draw.rect(self.screen, self.darkred, [x*self.tilesize,y*self.tilesize,self.tilefilsize,self.tilefilsize])
                    if settings.tiles[x][y].ground == GameEnum.GroundType.stairs:
                        if  settings.tiles[x][y].visibility == GameEnum.VisibilityType.unknown:
                            pygame.draw.rect(self.screen, self.black, [x*self.tilesize,y*self.tilesize,self.tilefilsize,self.tilefilsize])
                        if  settings.tiles[x][y].visibility == GameEnum.VisibilityType.visible: 
                            pygame.draw.rect(self.screen, self.pink, [x*self.tilesize,y*self.tilesize,self.tilefilsize,self.tilefilsize])
                        if  settings.tiles[x][y].visibility == GameEnum.VisibilityType.fogged:
                            pygame.draw.rect(self.screen, self.pink, [x*self.tilesize,y*self.tilesize,self.tilefilsize,self.tilefilsize])
        if len(self.tiles_lists) >= 1:
            for x in range(settings.xtile):
                    for y in range(settings.ytile):
                        if  settings.tiles[x][y].visibility == GameEnum.VisibilityType.unknown:
                            pygame.draw.rect(self.screen, self.black, [x*self.tilesize,y*self.tilesize,self.tilefilsize,self.tilefilsize])
                        if settings.tiles[x][y].ground == GameEnum.GroundType.stairs and settings.tiles[x][y].visibility == GameEnum.VisibilityType.visible:
                            pygame.draw.rect(self.screen, self.pink, [x*self.tilesize,y*self.tilesize,self.tilefilsize,self.tilefilsize])
                        if settings.tiles[x][y].ground == GameEnum.GroundType.stairs and settings.tiles[x][y].visibility == GameEnum.VisibilityType.fogged:
                            pygame.draw.rect(self.screen, self.pink, [x*self.tilesize,y*self.tilesize,self.tilefilsize,self.tilefilsize])
            for tile_list in self.tiles_lists:
                for x in range(settings.xtile):
                    for y in range(settings.ytile):
                        if  tile_list[x][y].visibility == GameEnum.VisibilityType.fogged and tile_list[x][y].ground == GameEnum.GroundType.floor:
                            pygame.draw.rect(self.screen, self.darkred, [x*self.tilesize,y*self.tilesize,self.tilefilsize,self.tilefilsize])
            for tile_list in self.tiles_lists:
                for x in range(settings.xtile):
                    for y in range(settings.ytile):
                        if  tile_list[x][y].visibility == GameEnum.VisibilityType.visible and tile_list[x][y].ground == GameEnum.GroundType.floor:
                            pygame.draw.rect(self.screen, self.red, [x*self.tilesize,y*self.tilesize,self.tilefilsize,self.tilefilsize])

    def drawPlayer(self,x,y,frame_stack,enter_cave):
        '''Creates the image of the player.'''
        if enter_cave:
            self.player_positions_list = []
        self.player_positions_list.append([x,y])
        if len(self.player_positions_list) > frame_stack and self.tiles_lists!= []:
            del self.player_positions_list[0]
        for position in self.player_positions_list:
            pygame.draw.rect(self.screen, self.blue, [position[0]*self.tilesize + self.rectEnemyPading,position[1]*self.tilesize + self.rectEnemyPading,self.rectEnemyFill,self.rectEnemyFill])
        

    def enemyDepiction(self,enemies_list,frame_stack,enter_cave):
        '''Creates the image of the enemies.'''
        if enter_cave:
            self.enemies_lists = []
        self.enemies_lists.append(enemies_list)
        if len(self.enemies_lists) > frame_stack and self.tiles_lists!= []:
            del self.enemies_lists[0]
        new_tiles_lists = self.tiles_lists.copy()
        
        #new_tiles_lists.reverse()
        for enemy_l,tile in zip(self.enemies_lists,new_tiles_lists):
            if enemy_l != []:
                for enemy in enemy_l:
                    
                    if tile[enemy[0]][enemy[1]].visibility == GameEnum.VisibilityType.visible:
                        if enemy[2] == "a Giant Rat":
                            pygame.draw.rect(self.screen, self.gray, [enemy[0]*self.tilesize + self.rectEnemyPading,enemy[1]*self.tilesize + self.rectEnemyPading,self.rectEnemyFill,self.rectEnemyFill])
                        if enemy[2] == "a Goblin":
                            # print(enemy.enemyCurrentPossitionX*self.tilesize  + self.cycleEnemyPading,self.cycleEnemyFill)
                            # self.cycleEnemyFill = 1
                            pygame.draw.circle(self.screen, self.yellow, (enemy[0]*self.tilesize  + self.cycleEnemyPading,enemy[1]*self.tilesize + self.cycleEnemyPading), self.cycleEnemyFill)
                        if enemy[2] == "a Gray Slime":
                            pygame.draw.rect(self.screen, self.lightGray, [enemy[0]*self.tilesize + self.rectEnemyPading,enemy[1]*self.tilesize + self.rectEnemyPading,self.rectEnemyFill,self.rectEnemyFill])
                        if enemy[2] == "an  Orc Grunt":
                            pygame.draw.rect(self.screen, self.green, [enemy[0]*self.tilesize + self.rectEnemyPading,enemy[1]*self.tilesize + self.rectEnemyPading,self.rectEnemyFill,self.rectEnemyFill])
                        if enemy[2] == "an Orc Warlord":
                            pygame.draw.circle(self.screen, self.dark_green, (enemy[0]*self.tilesize  + self.cycleEnemyPading,enemy[1]*self.tilesize + self.cycleEnemyPading), self.cycleEnemyFill)
                        if enemy[2] == "an Ettin":
                            pygame.draw.circle(self.screen, self.dark_gray, (enemy[0]*self.tilesize  + self.cycleEnemyPading,enemy[1]*self.tilesize + self.cycleEnemyPading), self.cycleEnemyFill)
                        if enemy[2] == "a Skeleton":
                            pygame.draw.rect(self.screen, self.white, [enemy[0]*self.tilesize + self.rectEnemyPading,enemy[1]*self.tilesize + self.rectEnemyPading,self.rectEnemyFill,self.skeletonfill])  
                        if enemy[2] == "a Wyrm":
                            pygame.draw.rect(self.screen, self.magenta, [enemy[0]*self.tilesize + self.rectEnemyPading,enemy[1]*self.tilesize + self.rectEnemyPading,self.rectEnemyFill,self.rectEnemyFill]) 
                        if enemy[2] == "a Vampire":
                            pygame.draw.circle(self.screen, self.black, (enemy[0]*self.tilesize  + self.cycleEnemyPading,enemy[1]*self.tilesize + self.cycleEnemyPading), self.cycleEnemyFill)

    def drawItem(self):
        '''Creates the image of the items.'''
        for x in range(settings.xtile):
            for y in range(settings.ytile):
                if settings.tiles[x][y].visibility != GameEnum.VisibilityType.unknown:
                    if  isinstance(settings.tiles[x][y].store,HelthPotion):
                        # print(x,self.itemPading,x*self.tilesize + self.itemPading,y*self.tilesize,self.itemFill,self.itemFill)
                        pygame.draw.rect(self.screen, self.blue, [x*self.tilesize + self.itemPading,y*self.tilesize,self.itemFill,self.itemFill])
                    if isinstance(settings.tiles[x][y].store,ManaPotion):
                        pygame.draw.rect(self.screen, self.yellow, [x*self.tilesize + self.itemPading,y*self.tilesize,self.itemFill,self.itemFill])
                    if isinstance(settings.tiles[x][y].store,Staff) or isinstance(settings.tiles[x][y].store,Sword):
                        pygame.draw.rect(self.screen, self.green, [x*self.tilesize,y*self.tilesize,self.itemFill,self.itemFill])
                    if isinstance(settings.tiles[x][y].store,Werdna_Ring):
                        pygame.draw.rect(self.screen, self.green, [x*self.tilesize,y*self.tilesize,self.tilefilsize,self.tilefilsize])

    def arrayreturn(self,screen):
        array = pygame.surfarray.array3d(screen)
        return array