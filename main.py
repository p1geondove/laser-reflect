import sys
import pygame

from math import pi

from scripts.prim import Line, Circle, Ellipse, Prim
from scripts.laser import Laser
from scripts.const import WIDTH, HEIGHT, MAX_BOUNCES, MAX_DISTANCE

def main():
    window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
    clock = pygame.Clock()

    mouse_pos = 0,0
    pretty_drawing = False
    max_bounces = 512
    max_distance = 10000

    laser = Laser(450,420,0)
    prims:list[Prim] = [
        Circle(400, 0, 450),
        Circle(400, 0, 340),
        Circle(400, 800, 340),
        Circle(400, 800, 300),
        Circle(400, 580, 50),
        Circle(400, 800, 450),
        Line(300,400,500,400),
        Line(400,340,400,320),
    ]
    """
    prims:list[Prim] = [
        Ellipse(200,100,200,100,0),
        Line(0,0,100,100)
        #Ellipse(600,200,200,100,pi/2),
        #Ellipse(200,600,200,100,pi),
        #Ellipse(200,600,200,100,pi/2*3),
        #Ellipse(400,400,200,100,pi/4),
    ]
    """

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            laser.handle_event(event)

            for p in prims:
                p.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # exit when pressing Esc
                    pygame.quit()
                    sys.exit(0)
                elif event.key == pygame.K_p: # toggle pretty drawing when pressing p
                    pretty_drawing = not pretty_drawing
                elif event.key == pygame.K_c: # add new Circle when pressing c
                    prims.append(Circle(mouse_pos[0], mouse_pos[1], 50))
                elif event.key == pygame.K_l: # add new line when pressing l
                    prims.append(Line(mouse_pos[0]-50, mouse_pos[1], mouse_pos[0]+50, mouse_pos[1]))
                elif event.key == pygame.K_e: # add new Ellipse
                    prims.append(Ellipse(mouse_pos[0],mouse_pos[1],100,50,0))

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # remove prim if middle mouse pressed
                if event.button == 2:
                    for p,t in zip(prims, (p.touch(mouse_pos) for p in prims)):
                        if t: prims.remove(p)

            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos

            elif event.type == pygame.MOUSEWHEEL:
                max_bounces = max(1, min(MAX_BOUNCES, int(max_bounces*2**event.y)))
                max_distance = max(100, min(MAX_DISTANCE, max_distance*2**event.y))

        window.fill("grey10")
        laser.trace(prims, max_bounces, max_distance)
        laser.draw(window, pretty_drawing)

        for p in prims:
            p.draw(window)

        pygame.display.flip()
        clock.tick()
        pygame.display.set_caption(f"{clock.get_fps():.0f} fps")

if __name__ == "__main__":
    main()
