import pygame
import sys
import math
import os
from GUIObjects import Arrows, Value, Direction, Bar
import mysql.connector
import databaseMySQL

# defines
TEXT_COLOR = (44, 180, 232)


class PygView(object):

    def __init__(self, fullscreen, width=800, height=600, fps=30):
        """Initialize pygame, window, background, font,...
        """
        #window position
       # x = 10
        #y = 0
        #os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)

        pygame.init()
        pygame.display.set_caption("Home system visualization")
        if fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.surface = pygame.Surface(self.screen.get_size()).convert()
            self.width, self.height = pygame.display.get_surface().get_size()
        else:
            self.width = width
            self.height = height

            self.screen = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME | pygame.DOUBLEBUF)
            self.surface = pygame.Surface(self.screen.get_size()).convert()

        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.font = pygame.font.SysFont('mono', 20, bold=True)


        self.objects = {}

        Value.default_color = TEXT_COLOR  # sets default for all values

        offset_y = 25
        x = 30
        y = 37
        # inside
        self.objects['temperature1'] = Value(screen = self.screen, position=(x, y), units='°C', decimals=1)
        self.objects['humidity'] = Value(screen=self.screen, position=(x, y + offset_y*1), units='%')

        y = 118

        # outside
        self.objects['temperature2'] = Value(screen=self.screen, position=(x, y + offset_y*1), units='°C', decimals = 1)
        self.objects['pressure'] = Value(screen=self.screen, position=(x, y + offset_y*2), units='hPa')
        self.objects['stationVoltage'] = Value(screen=self.screen, position=(x, y + offset_y*3), units='V', decimals=2)
        self.objects['temperature3'] = Value(screen=self.screen, position=(x, y + offset_y*4), units='°C', decimals = 1)

        # arrows
        self.objects['arrowGridHouse'] = Arrows(surface=self.surface, direction=Direction.DOWN, count=10,
                                        position=(438, 175), colorA=(0, 200, 0), colorB=(0, 255, 0))
        self.objects['arrowPowerwallHouse'] = Arrows(surface=self.surface, direction=Direction.LEFT, count=10,
                                        position=(574, 290), colorA=(0, 200, 0), colorB=(0, 255, 0))
        self.objects['arrowSolarPowerwall'] = Arrows(surface=self.surface, direction=Direction.DOWN, count=10,
                                        position=(630, 150), colorA=(0, 200, 0), colorB=(0, 255, 0))
        self.objects['arrowWater'] = Arrows(surface=self.surface, direction=Direction.RIGHT, count=3,
                                        position=(320, 275), colorA=(0, 0, 200), colorB=(0, 0, 255))

        #bars
        self.objects['barWater'] = Bar(screen=self.screen, color=(0, 0, 255), rect = (306, 338, 55, 64), direction = Direction.UP)
        self.objects['barPowerwall'] = Bar(screen=self.screen, color=(50, 200, 0), rect = (615, 242, 51, 98), direction = Direction.UP)

        #values inside bars
        self.objects['valueWater1'] = Value(screen=self.screen, position=(310, 342), units='%', size = 0.8)
        self.objects['valueWater2'] = Value(screen=self.screen, position=(310, 348), units='m3', size = 0.5)

        self.objects['valuePowerwall'] = Value(screen=self.screen, position=(625, 242), units='%', size = 0.8)

        #prices
        x = 400
        y = 300
        offset_y = 25
        self.objects['valuePriceLastDay'] = Value(screen=self.screen, position=(x, y + offset_y * 1), units='Kč', title="Cena za včera:")
        self.objects['valuePriceYearPerc'] = Value(screen=self.screen, position=(x, y + offset_y * 2), units='%',
                                                  title="Roční plnění:")
        self.objects['valueDailyIncrease'] = Value(screen=self.screen, position=(x, y + offset_y * 3), units='%',
                                                   title="Denní nárůst:")

    def run(self):
        """The mainloop
        """
        running = True

        pygame.time.set_timer(pygame.USEREVENT+1, 100)# animate event
        pygame.time.set_timer(pygame.USEREVENT + 2, 200)  # update values event
        pygame.time.set_timer(pygame.USEREVENT+3, 5000)#check for sw update

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.USEREVENT+1:
                    for name, obj in self.objects.items():
                        if hasattr(obj, 'Animate'):
                            obj.Animate()
                elif event.type == pygame.USEREVENT + 2:
                    self.objects['barWater'].value = 100.0 * abs(math.sin(self.playtime/4.0))
                    self.objects['barPowerwall'].value = 100.0 * abs(math.sin(self.playtime / 4.0))
                elif event.type == pygame.USEREVENT + 3:
                    if self.CheckForSWUpdate():
                        running = False
                    currValues = databaseMySQL.getCurrentValues()

                    self.objects['temperature1'].value = currValues['temperature_keyboard']
                    self.objects['humidity'].value = currValues['humidity_keyboard']
                    self.objects['temperature2'].value = currValues['temperature_meteostation 1']
                    self.objects['pressure'].value = currValues['pressure_meteostation 1']/10 # kPa to hPa
                    self.objects['stationVoltage'].value = currValues['voltage_meteostation 1']


            milliseconds = self.clock.tick(self.fps)
            self.playtime += milliseconds / 1000.0

            self.drawBackground()
            #frame
            pygame.draw.rect(self.screen, (44, 180, 232), (0, 0, self.width-2, self.height-2), 2)

            self.drawText("Stav systému", (192, 40))


            for name, obj in self.objects.items():
                obj.Draw()

            pygame.display.flip()
            self.screen.blit(self.surface, (0, 0))

        pygame.quit()

    def drawBackground(self):
        currentFolder = os.path.dirname(__file__)
        img = pygame.image.load(currentFolder+"/background.png").convert()
        # transform venus and blit on background in one go
        pygame.transform.scale(img, (self.width, self.height), self.surface)



    def drawText(self, text, pos):
        """Center text in window
        """
        fw, fh = self.font.size(text)  # fw: font width,  fh: font height
        surface = self.font.render(text, True, TEXT_COLOR)
        # // makes integer division in python3

        self.screen.blit(surface, pos)


    def CheckForSWUpdate(self):
        currentFolder = os.path.dirname(__file__)
        updateFolder = currentFolder+'/update/'
        files = os.listdir(updateFolder)
        print(files)
        if len(files)>0:
            for f in files:
                os.replace(updateFolder+f, currentFolder+"/"+os.path.basename(f)) # move to parent folder
                print("updated:"+str(f))

                os.popen('nohup /home/pi/Desktop/runVisualization.sh')
            return True
        return False
####

if __name__ == '__main__':
    # call with width of window and fps
    PygView(fullscreen=True).run()