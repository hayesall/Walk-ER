'''
A gui for Entity-Relational Diagrams, based on the parsed outputs from ERDPlus's diagram creation tool.

Written by Alexander L. Hayes, Indiana University STARAI Lab
Last updated January 13, 2017

TODO:
 like literally everything
'''

import pygame
from pygame.locals import *

#initialize
pygame.init()
pygame.font.init()

#make a couple fonts
myfont = pygame.font.SysFont("monospace", 12)
PYGBUTTON_FONT = pygame.font.Font('freesansbold.ttf', 14)

#colors:
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARKGRAY = (64, 64, 64)
GRAY = (128, 128, 128)
LIGHTGRAY = (212, 208, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

#constructor function from http://inventwithpython.com/blog/2012/10/30/creating-a-button-ui-module-for-pygame/
class PygButton(object):
    def __init__(self, rect=None, caption='', bgcolor=LIGHTGRAY, fgcolor=BLACK, font=None, normal=None, down=None, highlight=None):
        if rect is None:
            self._rect = pygame.Rect(0, 0, 30, 60)
        else:
            self._rect = pygame.Rect(rect)
            
        self._caption = caption
        self._bgcolor = bgcolor
        self._fgcolor = fgcolor
        
        if font is None:
            self._font = PYGBUTTON_FONT
        else:
            self._font = font
            
        #track state of the button
        self.buttonDown = False #is the button currently pressed down?
        self.mouseOverButton = False #is the mouse currently hovering over the button 
        self.lastMouseDownOverButton = False #was the last mouse down event over the mouse button (used to track clicks)?
        
        self._visible = True # is the button visible?
        self.customSurfaces = False #button starts as a text button instead of having custom images for each surface

        if normal is None:
            #create the surfaces for a text button
            self.surfaceNormal = pygame.Surface(self._rect.size)
            self.surfaceDown = pygame.Surface(self._rect.size)
            self.surfaceHightlight = pygame.Surface(self._rect.size)
            self._update() #draw the initial button images
        else:
            #create the surfaces for a custom image button
            self.setSurfaces(normal, down, highlight)

    def setSurfaces(self, normalSurface, downSurface=None, highlightSurface=None):
        # Switch the button to a  custom image type of button (rather than a text button).
        # You can specify either a pygame.Surface object or a string of a filename to load for each of the button appearance states
        if downSurface is None:
            downSurface = normalSurface
        if highlightSurface is None:
            highlightSurface = normalSurface

        if type(normalSurface) == str:
            self.origSurfaceNormal = pygame.image.load(normalSurface)
        if type(downSurface) == str:
            self.origSurfaceDown = pygame.image.load(downSurface)
        if type(highlightSurface) == str:
            self.origSurfaceHighlight = pygame.image.load(highlightSurface)

        if self.origSurfaceNormal.get_size() != self.origSurfaceDown.get_size() != self.origSurfaceHighlight.getSize():
            raise Exception('Errors, sorry for not being more specific')

        self.surfaceNormal = self.origSurfaceNormal
        self.surfaceDown = self.origSurfaceDown
        self.surfaceHighlight = self.origSurfaceHighlight
        self.customSurfaces = True
        self._rect = pygame.Rect((self._rect.left, self._rect.top, self.surfaceNormal.get_width(), self.surfaceNormal.get_height()))
        
    def draw(self, surfaceObj):
        #Blit the current button's appearance tot he surface object.
        if self._visible:
            if self.buttonDown:
                surfaceObj.blit(self.surfaceDown, self._rect)
            elif self.mouseOverButton:
                surfaceObj.blit(self.surfaceHighlight, self._rect)
            else:
                surfaceObj.blit(self.surfaceNormal, self._rect)

    def _update(self):
        #Redraw the button's Surface object. Call this method when the button has changed appearance.
        if self.customSurfaces:
            self.surfaceNormal = pygame.transform.smoothscale(self.origSurfaceNormal, self._rect.size)
            self.surfaceDown = pygame.transform.smoothscale(self.origSurfaceDown, self._rect.size)
            self.surfaceHighlight = pygame.transform.smoothscale(self.origSurfaceHighlight, self._rect.size)
            return
        
        w = self._rect.width
        h = self._rect.height
    
        # fill background color for all buttons
        self.surfaceNormal.fill(self.bgcolor)
        self.surfaceDown.fill(self.bgcolor)
        self.surfaceHighlight.fill(self.bgcolor)

        #draw caption text for all buttons
        captionSurf = self._font.render(self._caption, True, self.fgcolor, self.bgcolor)
        captionRect = captionSurface.get_rect()
        captionRect.center = int(w/2), int(h/2)
        self.surfaceNormal.blit(captionSurf, captionRect)
        self.surfaceDown.blit(captionSurf, captionRect)

        #draw border for normal button
        pygame.draw.rect(self.surfaceNormal, BLACK, pygame.Rect((0, 0, w, h)), 1) #black border for everything
        pygame.draw.line(self.surfaceNormal, WHITE, (1,1), (w - 2, 1))
        pygame.draw.line(self.surfaceNormal, WHITE, (1,1), (1, h - 2))
        pygame.draw.line(self.surfaceNormal, DARKGRAY, (1, h - 1), (w - 1, h - 1))
        pygame.draw.line(self.surfaceNormal, DARKGRAY, (w - 1, 1), (w - 1, h - 1))
        pygame.draw.line(self.surfaceNormal, GRAY, (2, h - 2), (w - 2, h - 2))
        pygame.draw.line(self.surfaceNormal, GRAY, (w - 2, 2), (w - 2, h - 2))

        #draw border for down button
        pygame.draw.rect(self.surfaceDown, BLACK, pygame.Rect((0, 0, w, h)), 1) #black border for everything
        pygame.draw.line(self.surfaceDown, WHITE, (1, 1), (w - 2, 1))
        pygame.draw.line(self.surfaceDown, WHITE, (1, 1), (1, h - 2))
        pygame.draw.line(self.surfaceDown, DARKGRAY, (1, h - 2), (1, 1))
        pygame.draw.line(self.surfaceDown, DARKGRAY, (1, 1), (w - 2, 1))
        pygame.draw.line(self.surfaceDown, GRAY, (2, h - 3), (2, 2))
        pygame.draw.line(self.surfaceDown, GRAY, (2, 2), (w - 3, 2))

        #draw border for highlight button
        self.surfaceHighlight = self.surfaceNormal

    def mouseClick(self, event):
        pass
    def mouseEnter(self, event):
        pass
    def mouseMove(self, event):
        pass
    def mouseExit(self, event):
        pass
    def mouseDown(self, event):
        pass
    def mouseUp(self, event):
        pass

    def handleEvent(self, eventObj):
        if eventObj.type not in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN) or not self._visible:
            # The button only cares about mouse-related events (or no events if it is invisible).
            return []
        retVal = []

        hasExited = False
        if not self.mouseOverButton and self._rect.collidepoint(eventObj.pos):
            # if the mouse has entered the button
            self.mouseOverButton = True
            self.mouseEnter(eventObj)
            retVal.append('enter')
        elif self.mouseOverButton and not self._rect.collidepoint(eventObj.pos):
            # if the mouse has exited the button
            self.mouseOverButton = False
            hasExited = True #call mouseExit() later, since we want mouseMove() to be handled before mouseExit()
            
        if self._rect.collidepoint(eventObj.pos):
            # if mouse event happened over the button:
            if eventObj.type == MOUSEMOTION:
                self.mouseMove(eventObj)
                retVal.append('move')
            elif eventObj.type == MOUSEBUTTONDOWN:
                self.buttonDown = True
                self.lastMouseDownOverButton = True
                self.mouseDown(eventObj)
                retVal.append('down')
        else:
            if eventObj.type in (MOUSEBUTTONUP, MOUSEBUTTONDOWN):
                # if an up/down happens off the button, then the next up won't cause mouseClick()
                self.lastMouseDownOverButton = False
                    
        # mouse up is handled whether or not it was over the button
        doMouseClick = False
        if eventObj.type == MOUSEBUTTONUP:
            if self.lastMouseDownOverButton:
                doMouseClick = True
            self.lastMouseDownOverButton = False
                
            if self.buttonDown:
                self.buttonDown = False
                self.mouseUp =(eventObj)
                retVal.append('up')

            if doMouseClick:
                self.buttonDown = False
                self.mouseClick(eventObj)
                retVal.append('click')

        if hasExited:
            self.mouseExit(eventObj)
            retVal.append('exit')
                
        return retVal
            
        
        

#size
size = [900,600]
screen = pygame.display.set_mode(size)

#loop until the user clicks the close button
done = False
clock = pygame.time.Clock()

# shapes to draw
#Entities are rectangles
rectangles = [(267, 126, 'Professor'), (571, 128, 'Student'), (426, 302, 'Course')]
#Attributes are ovals
ovals = [(131, 81, 'Salary'), (126, 142, 'Department'), (425, 398, 'Rating'), (675, 66, 'GPA')]
#Relationships are diamonds, there aren't built-in diamonds so we can do rectangles in the meantime
diamonds = [(414, 137, 'Advises'), (306, 226, 'Teaches'), (579, 243, 'Takes'), (487, 211, 'TAs')]

while not done:
    clock.tick(60)    #PCMR

    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                done = True
        elif event.type == pygame.QUIT:
            done = True

    # Clear the screen and set the screen background
    screen.fill(WHITE)

    # Draw all of the rectangles
    for tupl in rectangles:
        #rectangles should be 110,55
        pygame.draw.rect(screen, BLACK, (tupl[0], tupl[1], 110, 55), 1)
        label = myfont.render(tupl[2], 1, BLACK)
        screen.blit(label, (tupl[0]+5, tupl[1]+5))

    # Draw all of the ovals
    for tupl in ovals:
        # ovals should be about the same size 110,55
        pygame.draw.ellipse(screen, BLACK, (tupl[0], tupl[1], 110, 55), 1)
        label = myfont.render(tupl[2], 1, BLACK)
        screen.blit(label, (tupl[0]+40, tupl[1]+20))

    for tupl in diamonds:
        #!!! switch this to pygame.draw.polygon (specify an array of points to draw between)
        pygame.draw.rect(screen, BLACK, (tupl[0], tupl[1], 50, 25), 1)
        label = myfont.render(tupl[2], 1, BLACK)
        screen.blit(label, (tupl[0]+5, tupl[1]+5))

    pygame.display.flip()

pygame.font.quit()
pygame.quit()
