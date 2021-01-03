import pygame
from enum import Enum
import math

class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

# ------------------------------------------ ARROWS --------------------------------------------------------------------
class Arrows(object):

    def __init__(self, surface, direction, count, position, colorA, colorB):
        self.colBuffer = [colorA] * count
        self.count = count
        self.colorA = colorA
        self.colorB = colorB
        self.surface = surface
        self.direction = direction
        self.position = position
        self.animTmp = 0.0
        self.active = False

        self.NOT_ACTIVE_COL = (80,80,80)
        self.speed = 0.3

    def Draw(self):
        if self.direction == Direction.UP:
            x = 0
            y = -1
        elif self.direction == Direction.DOWN:
            x = 0
            y = 1
        elif self.direction == Direction.LEFT:
            x = -1
            y = 0
        elif self.direction == Direction.RIGHT:
            x = 1
            y = 0

        for i in range(self.count):
            offset = i * 5
            self._DrawArrow((x * offset + self.position[0], y * offset + self.position[1]), self.colBuffer[i])

    def _DrawArrow(self, pos, color):  # draws one arrow
        if self.direction == Direction.UP:
            pygame.draw.line(self.surface, color, (pos[0] + 0, pos[1] + 10), (pos[0] + 10, pos[1] + 0))
            pygame.draw.line(self.surface, color, (pos[0] + 10, pos[1] + 0), (pos[0] + 20, pos[1] + 10))
        elif self.direction == Direction.DOWN:
            pygame.draw.line(self.surface, color, (pos[0] + 0, pos[1] + 0), (pos[0] + 10, pos[1] + 10))
            pygame.draw.line(self.surface, color, (pos[0] + 10, pos[1] + 10), (pos[0] + 20, pos[1] + 0))
        elif self.direction == Direction.LEFT:
            pygame.draw.line(self.surface, color, (pos[0] + 10, pos[1] + 0), (pos[0] + 0, pos[1] + 10))
            pygame.draw.line(self.surface, color, (pos[0] + 10, pos[1] + 20), (pos[0] + 0, pos[1] + 10))
        elif self.direction == Direction.RIGHT:
            pygame.draw.line(self.surface, color, (pos[0] + 0, pos[1] + 0), (pos[0] + 10, pos[1] + 10))
            pygame.draw.line(self.surface, color, (pos[0] + 10, pos[1] + 10), (pos[0] + 0, pos[1] + 20))

    def Animate(self):
        # reverse(self.colBuffer)

        prev = (0, 0, 0)
        for i in range(len(self.colBuffer)):
            (self.colBuffer[i], prev) = (prev, self.colBuffer[i])  # swap them

        if not self.active:
            self.colBuffer[0] = self.NOT_ACTIVE_COL
            return
        diff = self.colorB[0] - self.colorA[0]
        blend1 = diff * abs(math.sin(self.animTmp)) + self.colorA[0]
        diff = self.colorB[1] - self.colorA[1]
        blend2 = diff * abs(math.sin(self.animTmp)) + self.colorA[1]
        diff = self.colorB[2] - self.colorA[2]
        blend3 = diff * abs(math.sin(self.animTmp)) + self.colorA[2]

        self.colBuffer[0] = (blend1, blend2, blend3)

        self.animTmp += self.speed
        if self.animTmp > math.pi:
            self.animTmp -= math.pi

# ------------------------------------------- BAR ----------------------------------------------------------------------
class Bar(object):
    def __init__(self, screen, color, rect, direction=Direction.UP):
        self.color = color
        self.screen = screen
        self.rect = rect
        self.direction = direction
        self.value = None

    def Draw(self):
        if self.value is None:  # if not initialized, draw empty rectange crossed
            # cross
            pygame.draw.line(self.screen, (255, 0, 0), (self.rect[0]+2, self.rect[1]+1),
                             (self.rect[0] + self.rect[2]-1, self.rect[1] + self.rect[3]-1), 1)
            pygame.draw.line(self.screen, (255, 0, 0), (self.rect[0]+2, self.rect[1] + self.rect[3]-1),
                             (self.rect[0] + self.rect[2]-1, self.rect[1]+1), 1)
            # rect
            pygame.draw.rect(self.screen, self.color, self.rect, 2)
        else:
            #pygame.draw.rect(self.screen, self.color, self.rect, 2)

            barWidth = self.value * self.rect[2] / 100.0
            barHeight = self.value * self.rect[3] / 100.0

            if self.direction == Direction.UP:
                bar = (self.rect[0], self.rect[1] + (self.rect[3] - barHeight), self.rect[2], barHeight)
            elif self.direction == Direction.DOWN:
                bar = (self.rect[0], self.rect[1], self.rect[2], barHeight)
            elif self.direction == Direction.LEFT:
                bar = (self.rect[0] + (self.rect[2] - barWidth), self.rect[1], barWidth, self.rect[3])
            elif self.direction == Direction.RIGHT:
                bar = (self.rect[0], self.rect[1], barWidth, self.rect[3])
            else:
                raise ValueError()
            pygame.draw.rect(self.screen, self.color, bar, 0)

# ------------------------------------------ VALUES --------------------------------------------------------------------
class Value(object):
    default_color = (255, 255, 255)

    def __init__(self, screen, position, units, decimals=0, valueLimit=999999, colorLimit=(255, 0, 0),
                 color=None,size=1.0, title="", units2=""):
        self.value = None
        self.valueLimit = valueLimit
        if color is None:
            self.color = Value.default_color
        else:
            self.color = color
        self.colorLimit = colorLimit
        self.colorLimit_anim = colorLimit
        self.position = position

        self.valFont = pygame.font.SysFont('mono', int(28*size), bold=True)
        self.unitsFont = pygame.font.SysFont('mono', int(15*size), bold=True)

        self.screen = screen
        self.units = units
        self.units2 = units2
        self.animTmp = 0.0
        self.speed = 0.2
        self.decimals = decimals
        self.title=title

    def Draw(self):

        value = self.value
        decimals = self.decimals
        units = self.units
        valueLimit = self.valueLimit


        if self.value is not None:

            # if > 1000, switch to higher order if units2 is not empty
            if value > 1000 and self.units2 != '':
                value /= 1000
                valueLimit /= 1000
                decimals = 2
                units = self.units2

            formatStr = "{:."+str(decimals)+"f}"
            valueText = formatStr.format(value)
        else:
            if self.decimals>1:
                valueText = "-."+'-'*self.decimals
            elif self.decimals>0:
                valueText = "--."+'-'*self.decimals
            else:
                valueText = "--"


        titleOffset = 0
        if self.title!="":
            surfaceTitle = self.valFont.render(self.title, True, self.color)
            self.screen.blit(surfaceTitle, self.position)
            titleOffset = surfaceTitle.get_width()

        surfaceVal = self.valFont.render(valueText, True, self.color if value is None or value < valueLimit else self.colorLimit_anim)
        self.screen.blit(surfaceVal, (self.position[0] + titleOffset,self.position[1]))

        unitsVal = self.unitsFont.render(units, True,
                                      self.color if value is None or value < valueLimit else self.colorLimit_anim)
        self.screen.blit(unitsVal, (self.position[0] + surfaceVal.get_width() + titleOffset,self.position[1]+surfaceVal.get_height()*0.38))


    def Animate(self):

        self.colorLimit_anim = (
        self.colorLimit[0] * (1 - abs(math.sin(self.animTmp) / 3)), self.colorLimit[1], self.colorLimit[2])

        self.animTmp += self.speed
        if self.animTmp > math.pi:
            self.animTmp -= math.pi
