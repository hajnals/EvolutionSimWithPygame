import pygame
from scene import SceneBase, TitleScene, GameScene
from organism import Organism
from organism import Food
from random import seed

settings = {}

settings['Window width'] = 1600
settings['Window height'] = 900
settings['FPS'] = 20
settings['x_min'] = 100
settings['x_max'] = 1200
settings['y_min'] = 100
settings['y_max'] = 800
settings['v_max'] = 3
settings['a_max'] = 1
settings['food_num'] = 80
settings['pop_size'] = 2
settings['food_r'] = 5
settings['org_r_min'] = 10
settings['org_r_max'] = 20
settings['org_vis_r'] = 150
settings['org_vis_fi'] = 45
settings['fission'] = 2
# settings[''] = 

def run_game(width, height, fps, starting_scene):
    #--- Start the game Scene ---------------+
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    active_scene = starting_scene

    while active_scene != None:
        pressed_keys = pygame.key.get_pressed()
        
        # Event filtering 
        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False
            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                alt_pressed = pressed_keys[pygame.K_LALT] or \
                              pressed_keys[pygame.K_RALT]
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                elif event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True
            
            if quit_attempt:
                active_scene.Terminate()
            else:
                filtered_events.append(event)
        
        active_scene.ProcessInput(filtered_events, pressed_keys, settings)
        active_scene.Update(settings)
        active_scene.Render(screen, settings)
        
        active_scene = active_scene.next
        
        pygame.display.flip()
        clock.tick(fps)

#seed(20)
run_game(settings['Window width'], settings['Window height'], settings['FPS'], TitleScene())