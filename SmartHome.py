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
import RPi.GPIO as GPIO
import subprocess
import pathlib


# defines
TEXT_COLOR = (44, 180, 232)
RED_COLOR = (232,56,44)
ORANGE_COLOR = (232,150,44)

NORMAL = 0
RICH = 1
FULL = 2
verbosity = RICH


PIN_IR_SENSOR = 4 # GPIO

thisScriptPath = str(pathlib.Path(__file__).parent.absolute())

class PygView(object):

    def __init__(self, fullscreen, width=800, height=600, fps=30):
        """Initialize pygame, window, background, font,...
        """
        #window position
       # x = 10
        #y = 0
        #os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN_IR_SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.tmrIRsensorFilter = 0
        self.tmrIRsensorOFF = 0
        self.displayEnabled = True
        subprocess.run(['vcgencmd', 'display_power', '1']) # for sure, if previous was forced

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

        self.fontBig = pygame.font.SysFont('mono', 30, bold=True)
        self.font = pygame.font.SysFont('mono', 20, bold=True)
        self.fontSmall = pygame.font.SysFont('mono', 15, bold=False)


        self.objects = {}

        Value.default_color = TEXT_COLOR  # sets default for all values

        offset_y = 25
        x = 38
        y = 37
        # inside
        self.objects['valTemperature1'] = Value(screen = self.screen, position=(x, y), units='°C', decimals=1)
        self.objects['valHumidity'] = Value(screen=self.screen, position=(x, y + offset_y*1), units='%',valueLimit=65)

        y = 118

        # outside
        self.objects['valTemperature2'] = Value(screen=self.screen, position=(x, y + offset_y*1), units='°C', decimals = 1)
        self.objects['valPressure'] = Value(screen=self.screen, position=(x, y + offset_y*2), units='hPa')
        self.objects['valStationVoltage'] = Value(screen=self.screen, position=(x, y + offset_y*3), units='V', decimals=2)
        self.objects['valTemperature3'] = Value(screen=self.screen, position=(x, y + offset_y*4), units='°C', decimals = 1)

        # arrows
        self.objects['arrowGridHouse'] = Arrows(surface=self.surface, direction=Direction.DOWN, count=10,
                                        position=(446, 131), colorA=(0, 200, 0), colorB=(0, 255, 0))
        self.objects['arrowPowerwallHouse'] = Arrows(surface=self.surface, direction=Direction.LEFT, count=10,
                                        position=(580, 236), colorA=(0, 200, 0), colorB=(0, 255, 0))
        self.objects['arrowSolarPowerwall'] = Arrows(surface=self.surface, direction=Direction.DOWN, count=10,
                                        position=(635, 120), colorA=(0, 200, 0), colorB=(0, 255, 0))
        self.objects['arrowWater'] = Arrows(surface=self.surface, direction=Direction.RIGHT, count=3,
                                        position=(355, 220), colorA=(0, 0, 200), colorB=(0, 0, 255))

        # values besides arrows
        self.objects['valGridPower'] = Value(screen=self.screen, position=(470, 146), units='W', size=0.8, units2='kW')
        self.objects['valPowerwallPower'] = Value(screen=self.screen, position=(552, 260), units='W', size=0.8, units2='kW')
        self.objects['valSolarPower'] = Value(screen=self.screen, position=(659, 140), units='W', size=0.8, units2='kW')

        #bars
        self.objects['barWaterLevel'] = Bar(screen=self.screen, color=(0, 0, 220), rect = (299, 276, 62, 67), direction = Direction.UP)
        self.objects['barPowerwallLevel'] = Bar(screen=self.screen, color=(0, 170, 0), rect = (630, 208, 40, 68), direction = Direction.UP)

        #values inside bars
        self.objects['valWaterLevel'] = Value(screen=self.screen, position=(316, 285), units='%', size = 0.9)
        self.objects['valWaterVolume'] = Value(screen=self.screen, position=(320, 295), units='m3', size = 0.7)

        self.objects['valPowerwallLevel'] = Value(screen=self.screen, position=(636, 234), units='%', size = 0.8)

        #prices
        x = 370
        y = 363
        offset_y = 20
        self.objects['valPriceLastDay'] = Value(screen=self.screen, position=(x, y + offset_y * 1), units='Kč', title="Cena za včera:", size=0.7)
        self.objects['valPriceYearPerc'] = Value(screen=self.screen, position=(x, y + offset_y * 2), units='%',
                                                  title="Roční plnění:", size=0.7, decimals = 1)
        self.objects['valDailyIncrease'] = Value(screen=self.screen, position=(x, y + offset_y * 3), units='%',
                                                   title="Denní nárůst:", decimals=2, size=0.7)

        self.phoneCommState = 0
        self.phoneSignalInfo = "Unknown"

        self.onlineDevices = {}

        self.powerwallError = 0
        self.blinkTmr = 0
        self.blink = 0
        self.terminate = False
        self.blinkComm = False

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
                        # check sensor if we need to enable display
                        sensor = GPIO.input(PIN_IR_SENSOR)
                        if sensor:
                            self.tmrIRsensorFilter += 1
                        else:
                            self.tmrIRsensorFilter = 0

                        if not self.displayEnabled and self.tmrIRsensorFilter > 2:

                                subprocess.run(['vcgencmd','display_power','1'])
                                self.displayEnabled = True
                                self.tmrIRsensorFilter = 0

                        if self.displayEnabled:
                            if self.tmrIRsensorFilter > 2:
                                self.tmrIRsensorOFF = 0
                            else:
                                self.tmrIRsensorOFF += 1
                                # check for display going to sleep
                                if (self.tmrIRsensorOFF > 6000): # 10 min
                                    subprocess.run(['vcgencmd', 'display_power', '0'])
                                    self.displayEnabled = False
                                    self.tmrIRsensorOFF = 0

                    #elif event.type == pygame.USEREVENT + 2:
                        #self.objects['barWaterLevel'].value = 100.0 * abs(math.sin(self.playtime/4.0))


                        self.blinkTmr += 1
                        if self.blinkTmr >= 5:
                            self.blink = not self.blink
                            self.blinkTmr = 0

                    elif event.type == pygame.USEREVENT + 3:
                        if self.CheckForSWUpdate():
                            self.terminate = True




                milliseconds = self.clock.tick(self.fps)
                self.playtime += milliseconds / 1000.0

                self.drawBackground()
                #frame
                pygame.draw.rect(self.screen, (44, 180, 232), (0, 0, self.width-2, self.height-2), 2)

                self.drawText("Stav systému", (200, 38))

                if self.powerwallError or self.phoneCommState!=1:
                    self.drawText(""if self.blink else "Error!!!", (200, 57), color=RED_COLOR)
                elif self.phoneSignalInfo != 'Excellent':
                    self.drawText("Varování!", (200, 57), color=ORANGE_COLOR)
                else:
                    self.drawText("V pořádku", (200, 57), color=TEXT_COLOR)

                #powerwall exclamation mark
                if self.powerwallError:
                    self.drawText(""if self.blink else "!", (675, 233), color=RED_COLOR, font=self.fontBig)

                #phone exclamation mark
                if self.phoneCommState != 1:
                    self.drawText(""if self.blink else "phone", (200, 130), color=RED_COLOR, font=self.font)

                if self.phoneCommState==1 and self.phoneSignalInfo != 'Excellent':
                    self.drawText("phone signal", (200, 130), color=ORANGE_COLOR, font=self.font)

                for name, obj in self.objects.items():
                    obj.Draw()

                #online devices
                x=28
                y=358
                i=0
                if self.onlineDevices is not None:
                    for deviceName, online in self.onlineDevices.items():
                        txt=deviceName[:10] + '.' if len(deviceName)>10 else deviceName # cut long names
                        self.drawText(txt, (x, y+12*i), color=TEXT_COLOR if online==1 else (255,0,0), font = self.fontSmall)
                        i+=1


                # blink comm
                if self.blinkComm:
                    pygame.draw.rect(self.screen, TEXT_COLOR, (0, 0, 5, 5), 0)
                pygame.display.flip()
                self.screen.blit(self.surface, (0, 0))

        except Exception as e:
            Log("Exception for main run()")
            LogException(e)

        self.terminate = True
        print("pygame quit")
        pygame.quit()

    def UpdateValuesFromServer(self):
        try:
            currValues = databaseMySQL.getCurrentValues()

            if currValues is not None:
                self.objects['valTemperature1'].value = currValues['temperature_PIR sensor']
                self.objects['valHumidity'].value = currValues['humidity_PIR sensor']
                self.objects['valTemperature2'].value = currValues['temperature_meteostation 1']
                self.objects['valPressure'].value = currValues['pressure_meteostation 1'] / 10  # kPa to hPa
                self.objects['valStationVoltage'].value = currValues['voltage_meteostation 1']

                self.objects['valPowerwallPower'].value = 0
                self.objects['valGridPower'].value = currValues['power_grid']
                self.objects['valSolarPower'].value = currValues['power_solar']

                # animate arrows according to these values
                self.objects['arrowGridHouse'].active = currValues['power_grid'] > 0
                self.objects['arrowSolarPowerwall'].active = currValues['power_solar'] > 0
                self.objects['arrowPowerwallHouse'].active = False

                self.powerwallError = currValues['status_powerwall_stateMachineStatus'] == 99
                self.objects['barPowerwallLevel'].value = currValues['status_powerwallSoc']
                self.objects['valPowerwallLevel'].value = currValues['status_powerwallSoc']
                self.objects['arrowPowerwallHouse'].active = currValues['status_powerwall_stateMachineStatus'] == 10 and \
                                                             currValues['status_rackUno_stateMachineStatus'] == 3

            prices = databaseMySQL.getPriceData()
            if prices is not None:
                self.objects['valPriceLastDay'].value = prices['priceLastDay']
                self.objects['valPriceYearPerc'].value = prices['yearPerc']
                self.objects['valDailyIncrease'].value = prices['dailyIncrease']



            stateValues = databaseMySQL.getStateValues()
            if stateValues is not None:
                self.phoneCommState = stateValues['phoneCommState']
                self.phoneSignalInfo = stateValues['phoneSignalInfo']

        except Exception as e:
            Log("Exception for main UpdateValuesFromServer()")
            LogException(e)

        self.blinkComm = not self.blinkComm
        if not self.terminate:
            threading.Timer(5, self.UpdateValuesFromServer).start() # calling itself periodically

    def UpdateOnlineList(self):
        self.onlineDevices = databaseMySQL.getOnlineDevices()

        if not self.terminate:
            threading.Timer(30, self.UpdateOnlineList).start()  # calling itself periodically

    def drawBackground(self):
        img = pygame.image.load(thisScriptPath+"/background.png").convert()
        pygame.transform.scale(img, (self.width, self.height), self.surface)



    def drawText(self, text, pos, color = TEXT_COLOR, font=None):
        """Center text in window
        """
        if font is None:
            font = self.font
        #fw, fh = self.font.size(text)  # fw: font width,  fh: font height
        surface = font.render(text, True, color)

        self.screen.blit(surface, pos)


    def CheckForSWUpdate(self):
        updateFolder = thisScriptPath+'/update/'
        files = os.listdir(updateFolder)
        if len(files)>0:
            for f in files:
                os.replace(updateFolder+f, thisScriptPath+"/"+os.path.basename(f)) # move to parent folder
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
    with open(thisScriptPath+"/logs/main.log", "a") as file:
        file.write(dateStr + " >> " + str(s) + "\n")

def LogException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    Log(str(e))
    Log(str(exc_type) +" : "+ str(fname) + " : " +str(exc_tb.tb_lineno))

if __name__ == '__main__':
    # call with width of window and fps
    PygView(fullscreen=True).run()