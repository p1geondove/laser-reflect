import sys
import math
import pygame

from scripts import const
from scripts.prim import Arc, Bezier, Circle, Ellipse, Line, Prim 
from scripts.laser import Laser
from scripts.svg_parser import parse

"""
TODO
Fix Arc.reflect
Improve .touch performance, fps plummits when just moving the cursor, maybe remove .hover and only check when mousepressed
More gui:
    buttons:
        locking elements
        toggle DRAW_MANIP

    maybe angle sweep:
        text/numberfield for start/end angle and amtount steps (steps/(second or fram) maybe??)  
"""

def main():
    window = pygame.display.set_mode((const.WIDTH, const.HEIGHT), pygame.SRCALPHA)
    pygame.font.init()
    font = pygame.font.SysFont(None, 20)
    clock = pygame.Clock()

    mouse_pos = pygame.Vector2()
    fancy_drawing = False
    max_bounces = 512
    max_distance = 10000

    laser = Laser((100,400),(1,0))
    prims:list[Prim] = [
        Ellipse((600,400),(200,100),0),
        Circle((100,100),100),
        Line((309,420),(331,380)),
        Bezier(((300,300),(400,300),(400,400),(300,450))),
        Arc((200,200),(150,100),0,math.pi/2,0)
    ]

    trace_flag = False
    laser.trace(prims)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            if laser.handle_event(event):
                trace_flag = True
                
            for p in prims:
                if p.handle_event(event):
                    trace_flag = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # exit when pressing Esc
                    pygame.quit()
                    sys.exit(0)
                elif event.key == pygame.K_a: # add new Arc when pressing a
                    prims.append(Arc(mouse_pos,(100,50),0,math.pi/2,math.pi/4))
                    trace_flag = True
                elif event.key == pygame.K_b: # add new Bezier when pressing b
                    points = [mouse_pos+p for p in ((-50,-50),(50,-50),(50,50),(-50,50))]
                    prims.append(Bezier(points))
                    trace_flag = True
                elif event.key == pygame.K_c: # add new Circle when pressing c
                    prims.append(Circle((mouse_pos.x, mouse_pos.y), 50))
                    trace_flag = True
                elif event.key == pygame.K_e: # add new Ellipse when pressing e
                    prims.append(Ellipse((mouse_pos.x, mouse_pos.y), (100,50), 0))
                    trace_flag = True
                elif event.key == pygame.K_l: # add new Line when pressing l
                    prims.append(Line((mouse_pos.x-50, mouse_pos.y), (mouse_pos.x+50, mouse_pos.y)))
                    trace_flag = True
                elif event.key == pygame.K_p: # toggle pretty drawing when pressing p
                    fancy_drawing = not fancy_drawing
                    trace_flag = True
                
                elif event.key == pygame.K_m:
                    const.DRAW_MANIP = not const.DRAW_MANIP
                    trace_flag = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # remove prim if middle mouse pressed:
                if event.button == 2:
                    for p,t in zip(prims, (p.touch(mouse_pos) for p in prims)):
                        if t:
                            prims.remove(p)
                            trace_flag = True

            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.Vector2(event.pos)
                trace_flag = True

            elif event.type == pygame.MOUSEWHEEL:
                max_bounces = max(1, min(const.MAX_BOUNCES, int(max_bounces*2**event.y)))
                max_distance = max(100, min(const.MAX_DISTANCE, max_distance*2**event.y))
                trace_flag = True

            elif event.type == pygame.DROPFILE:
                if event.file.split(".")[-1] == "svg":
                    new_prims = parse(event.file)
                    if new_prims:
                        prims = new_prims
                        trace_flag = True

        if trace_flag:
            laser.trace(prims, max_bounces, max_distance)
            trace_flag = False
            window.fill(const.COLOR_BACKGROUND)
            laser.draw(fancy_drawing)
            window.blit(laser.surface)
            for p in prims: p.draw(window)
            info_text = f"reflections: {len(laser.points)-2}\nmax reflections: {max_bounces}\ndistance: {laser.distance}\nmax length: {max_distance}\namount elements: {len(prims)}"
            info_surf = font.render(info_text, True, "grey50")
            window.blit(info_surf)

        pygame.display.flip()
        clock.tick(60)
        pygame.display.set_caption(f"{clock.get_fps():.0f} fps")

if __name__ == "__main__":
    main()
    # from scripts import svg_parser
