import pygame
import sys
import math
import os
from GUIObjects import Arrows, Value, Direction, Bar
import mysql.connector
import databaseMySQL
import threading
import time
from datetime import datetime

# defines
TEXT_COLOR = (44, 180, 232)

NORMAL = 0
RICH = 1
FULL = 2
verbosity = RICH


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

            pygame.mouse.set_visible(False)
        else:
            self.width = width
            self.height = height

            self.screen = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME | pygame.DOUBLEBUF)
            self.surface = pygame.Surface(self.screen.get_size()).convert()

        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.font = pygame.font.SysFont('mono', 20, bold=True)
        self.fontSmall = pygame.font.SysFont('mono', 2, bold=False)


        self.objects = {}

        Value.default_color = TEXT_COLOR  # sets default for all values

        offset_y = 25
        x = 38
        y = 37
        # inside
        self.objects['temperature1'] = Value(screen = self.screen, position=(x, y), units='°C', decimals=1)
        self.objects['humidity'] = Value(screen=self.screen, position=(x, y + offset_y*1), units='%',valueLimit=65)

        y = 118

        # outside
        self.objects['temperature2'] = Value(screen=self.screen, position=(x, y + offset_y*1), units='°C', decimals = 1)
        self.objects['pressure'] = Value(screen=self.screen, position=(x, y + offset_y*2), units='hPa')
        self.objects['stationVoltage'] = Value(screen=self.screen, position=(x, y + offset_y*3), units='V', decimals=2)
        self.objects['temperature3'] = Value(screen=self.screen, position=(x, y + offset_y*4), units='°C', decimals = 1)

        # arrows
        self.objects['arrowGridHouse'] = Arrows(surface=self.surface, direction=Direction.DOWN, count=10,
                                        position=(446, 131), colorA=(0, 200, 0), colorB=(0, 255, 0))
        self.objects['arrowPowerwallHouse'] = Arrows(surface=self.surface, direction=Direction.LEFT, count=10,
                                        position=(580, 236), colorA=(0, 200, 0), colorB=(0, 255, 0))
        self.objects['arrowSolarPowerwall'] = Arrows(surface=self.surface, direction=Direction.DOWN, count=10,
                                        position=(635, 120), colorA=(0, 200, 0), colorB=(0, 255, 0))
        self.objects['arrowWater'] = Arrows(surface=self.surface, direction=Direction.RIGHT, count=3,
                                        position=(355, 220), colorA=(0, 0, 200), colorB=(0, 0, 255))

        #bars
        self.objects['barWater'] = Bar(screen=self.screen, color=(0, 0, 255), rect = (299, 276, 62, 67), direction = Direction.UP)
        self.objects['barPowerwall'] = Bar(screen=self.screen, color=(0, 255, 0), rect = (630, 208, 40, 68), direction = Direction.UP)

        #values inside bars
        self.objects['valueWater1'] = Value(screen=self.screen, position=(316, 285), units='%', size = 0.8)
        self.objects['valueWater2'] = Value(screen=self.screen, position=(320, 295), units='m3', size = 0.5)

        self.objects['valuePowerwall'] = Value(screen=self.screen, position=(636, 234), units='%', size = 0.8)

        #prices
        x = 370
        y = 363
        offset_y = 20
        self.objects['valuePriceLastDay'] = Value(screen=self.screen, position=(x, y + offset_y * 1), units='Kč', title="Cena za včera:", size=0.7)
        self.objects['valuePriceYearPerc'] = Value(screen=self.screen, position=(x, y + offset_y * 2), units='%',
                                                  title="Roční plnění:", size=0.7)
        self.objects['valueDailyIncrease'] = Value(screen=self.screen, position=(x, y + offset_y * 3), units='%',
                                                   title="Denní nárůst:", decimals=2, size=0.7)

        self.terminate = False

    def run(self):
        """The mainloop
        """

        pygame.time.set_timer(pygame.USEREVENT+1, 100)# animate event
        pygame.time.set_timer(pygame.USEREVENT + 2, 200)  # update values event
        pygame.time.set_timer(pygame.USEREVENT+3, 5000)#check for sw update

        try:
            self.UpdateValuesFromServer() # for first time, then it is self-called
            self.UpdateOnlineList()

            while not self.terminate:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.terminate = True
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.terminate = True
                    elif event.type == pygame.USEREVENT+1:
                        for name, obj in self.objects.items():
                            if hasattr(obj, 'Animate'):
                                obj.Animate()
                    elif event.type == pygame.USEREVENT + 2:
                        self.objects['barWater'].value = 100.0 * abs(math.sin(self.playtime/4.0))
                        self.objects['barPowerwall'].value = 100.0 * abs(math.sin(self.playtime / 4.0))
                    elif event.type == pygame.USEREVENT + 3:
                        if self.CheckForSWUpdate():
                            self.terminate = True


                milliseconds = self.clock.tick(self.fps)
                self.playtime += milliseconds / 1000.0

                self.drawBackground()
                #frame
                pygame.draw.rect(self.screen, (44, 180, 232), (0, 0, self.width-2, self.height-2), 2)

                self.drawText("Stav systému", (200, 38))

                for name, obj in self.objects.items():
                    obj.Draw()

                #online devices
                x=28
                y=358
                i=0
                for deviceName, online in self.onlineDevices.items():
                    txt=deviceName[:9] + '.' if len(deviceName)>9 else deviceName # cut long names
                    self.drawText(txt, (x, y+12*i), color=TEXT_COLOR if online==1 else (255,0,0), font = self.fontSmall)
                    i+=1

                pygame.display.flip()
                self.screen.blit(self.surface, (0, 0))

        except Exception as e:
            Log("Exception for main run()")
            LogException(e)

        self.terminate = True
        print("pygame quit")
        pygame.quit()

    def UpdateValuesFromServer(self):
        currValues = databaseMySQL.getCurrentValues()

        self.objects['temperature1'].value = currValues['temperature_PIR sensor']
        self.objects['humidity'].value = currValues['humidity_PIR sensor']
        self.objects['temperature2'].value = currValues['temperature_meteostation 1']
        self.objects['pressure'].value = currValues['pressure_meteostation 1'] / 10  # kPa to hPa
        self.objects['stationVoltage'].value = currValues['voltage_meteostation 1']
        prices = databaseMySQL.getPriceData()
        self.objects['valuePriceLastDay'].value = prices['priceLastDay']
        self.objects['valuePriceYearPerc'].value = prices['yearPerc']
        self.objects['valueDailyIncrease'].value = prices['dailyIncrease']

        if not self.terminate:
            threading.Timer(5, self.UpdateValuesFromServer).start() # calling itself periodically

    def UpdateOnlineList(self):
        self.onlineDevices = databaseMySQL.getOnlineDevices()

        if not self.terminate:
            threading.Timer(30, self.UpdateValuesFromServer).start()  # calling itself periodically

    def drawBackground(self):
        currentFolder = os.path.dirname(__file__)
        img = pygame.image.load(currentFolder+"/background.png").convert()
        # transform venus and blit on background in one go
        pygame.transform.scale(img, (self.width, self.height), self.surface)



    def drawText(self, text, pos, color = TEXT_COLOR, font=None):
        """Center text in window
        """
        if font is None:
            font = self.font
        fw, fh = self.font.size(text)  # fw: font width,  fh: font height
        surface = self.font.render(text, True, color)
        # // makes integer division in python3

        self.screen.blit(surface, pos)


    def CheckForSWUpdate(self):
        currentFolder = os.path.dirname(__file__)
        updateFolder = currentFolder+'/update/'
        files = os.listdir(updateFolder)
        if len(files)>0:
            for f in files:
                os.replace(updateFolder+f, currentFolder+"/"+os.path.basename(f)) # move to parent folder
                print("updated:"+str(f))


            os.popen('nohup /home/pi/Desktop/runVisualization.sh')
            return True
        return False
####

def Log(s, _verbosity=NORMAL):
    if _verbosity > verbosity:
        return
    print(str(s))

    dateStr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("main.log", "a") as file:
        file.write(dateStr + " >> " + str(s) + "\n")

def LogException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    Log(str(e))
    Log(str(exc_type) +" : "+ str(fname) + " : " +str(exc_tb.tb_lineno))

if __name__ == '__main__':
    # call with width of window and fps
    PygView(fullscreen=True).run()