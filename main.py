import sys
import pygame

from scripts.prim import Line, Circle, Ellipse, Bezier, Prim
from scripts.laser import Laser
from scripts.const import WIDTH, HEIGHT, MAX_BOUNCES, MAX_DISTANCE, COLOR_BACKGROUND

def main():
    window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.font.init()
    font = pygame.font.SysFont(None, 20)
    clock = pygame.Clock()

    mouse_pos = pygame.Vector2()
    fancy_drawing = False
    max_bounces = 512
    max_distance = 10000

    laser = Laser((100,400),(1,0))
    prims:list[Prim] = [
        #Ellipse((600,400),(200,100),0),
        #Circle((100,100),100),
        #Line((309,420),(331,380)),
        Bezier(((300,300),(400,300),(400,400),(300,450)))
    ]

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
                    fancy_drawing = not fancy_drawing
                elif event.key == pygame.K_c: # add new Circle when pressing c
                    prims.append(Circle((mouse_pos.x, mouse_pos.y), 50))
                elif event.key == pygame.K_l: # add new Line when pressing l
                    prims.append(Line((mouse_pos.x-50, mouse_pos.y), (mouse_pos.x+50, mouse_pos.y)))
                elif event.key == pygame.K_e: # add new Ellipse
                    prims.append(Ellipse((mouse_pos.x, mouse_pos.y), (100,50), 0))
                elif event.key == pygame.K_b: # add new Bezier when pressing b
                    points = [mouse_pos+p for p in ((-50,-50),(50,-50),(50,50),(-50,50))]
                    prims.append(Bezier(points))

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # remove prim if middle mouse pressed:
                if event.button == 2:
                    for p,t in zip(prims, (p.touch(mouse_pos) for p in prims)):
                        if t: prims.remove(p)

            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.Vector2(event.pos)

            elif event.type == pygame.MOUSEWHEEL:
                max_bounces = max(1, min(MAX_BOUNCES, int(max_bounces*2**event.y)))
                max_distance = max(100, min(MAX_DISTANCE, max_distance*2**event.y))

        window.fill(COLOR_BACKGROUND)
        laser.trace(prims, max_bounces, max_distance)
        laser.draw(fancy_drawing)
        window.blit(laser.surface)
        for p in prims: p.draw(window)
        pygame.display.flip()
        clock.tick()
        pygame.display.set_caption(f"{clock.get_fps():.0f} fps")

if __name__ == "__main__":
    main()
