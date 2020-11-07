import pygame
import sys
import math
import os
from GUIObjects import Arrows, Value, Direction, Bar

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

        offset_y = 20
        x = 40
        y = 80
        # inside
        self.objects['temperature1'] = Value(screen = self.screen, position=(x, y), units='°C')
        self.objects['humidity'] = Value(screen=self.screen, position=(x, y - offset_y*1), units='%')

        x = 40
        y = 250

        # outside
        self.objects['temperature2'] = Value(screen=self.screen, position=(x, y - offset_y*1), units='°C')
        self.objects['pressure'] = Value(screen=self.screen, position=(x, y - offset_y*2), units='kPa')
        self.objects['stationVoltage'] = Value(screen=self.screen, position=(x, y - offset_y*3), units='V', decimals=2)
        self.objects['temperature3'] = Value(screen=self.screen, position=(x, y - offset_y*4), units='°C')

        # test
        self.objects['arrow1'] = Arrows(surface=self.surface, direction=Direction.DOWN, count=10,
                                        position=(50, 130), colorA=(0, 200, 0), colorB=(0, 255, 0))
        self.objects['bar1'] = Bar(screen=self.screen, color=(0, 200, 50), rect = (200, 50, 20, 120), direction = Direction.UP)
        self.objects['bar2'] = Bar(screen=self.screen, color=(50, 200, 0), rect = (230, 50, 20, 120), direction = Direction.DOWN)
        self.objects['bar3'] = Bar(screen=self.screen, color=(100, 200, 50), rect = (360, 100, 120, 50), direction = Direction.LEFT)
        self.objects['bar4'] = Bar(screen=self.screen, color=(150, 200, 0), rect = (390, 160, 120, 50), direction = Direction.RIGHT)

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
                    self.objects['bar1'].value = 100.0 * abs(math.sin(self.playtime/4.0))
                    self.objects['bar2'].value = 100.0 * abs(math.sin(self.playtime / 4.0))
                    self.objects['bar3'].value = 100.0 * abs(math.sin(self.playtime / 4.0))
                    self.objects['bar4'].value = 100.0 * abs(math.sin(self.playtime / 4.0))
                elif event.type == pygame.USEREVENT + 3:
                    if self.CheckForSWUpdate():
                        running = False

            milliseconds = self.clock.tick(self.fps)
            self.playtime += milliseconds / 1000.0

            self.drawBackground()
            #frame
            pygame.draw.rect(self.screen, (44, 180, 232), (0, 0, self.width-2, self.height-2), 2)

            self.drawText("Stav systému", (200, 50))


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