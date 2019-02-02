import pygame
from organism import Food, Organism
from math import cos
from math import sin
from math import radians
from math import sqrt

def draw_wall(screen, settings):
    color = (0,0,0)
    #pygame.draw.line(screen, color, (settings['x_min'], settings['y_min']), (settings['x_max'], settings['y_max']), 1)
    # (xmin ymin) (xmin ymax); 
    # (xmin ymax) (xmax ymax); 
    # (xmax ymax) (xmax ymin); 
    # (xmax ymin) (xmin ymin)
    pygame.draw.line(screen, color, (settings['x_min'], settings['y_min']), (settings['x_min'], settings['y_max']), 10)
    pygame.draw.line(screen, color, (settings['x_min'], settings['y_max']), (settings['x_max'], settings['y_max']), 10)
    pygame.draw.line(screen, color, (settings['x_max'], settings['y_max']), (settings['x_max'], settings['y_min']), 10)
    pygame.draw.line(screen, color, (settings['x_max'], settings['y_min']), (settings['x_min'], settings['y_min']), 10)
    
    pass

def draw_organism(screen, organism):
    # Draw the body
    x1 = int(organism.x)
    y1 = int(organism.y)
    color = organism.color
    radius = int(round(organism.size))
    pygame.draw.circle(screen, color, (x1, y1), radius)

    # Draw the vision
    xf1 = int( cos(radians(organism.r - organism.vision_fi)) * organism.vision_r + x1 )
    yf1 = int( sin(radians(organism.r - organism.vision_fi)) * organism.vision_r + y1 )
    xf2 = int( cos(radians(organism.r + organism.vision_fi)) * organism.vision_r + x1 )
    yf2 = int( sin(radians(organism.r + organism.vision_fi)) * organism.vision_r + y1 )
    # xfa = int( cos(radians(organism.r)) * organism.vision_r + x1)
    # yfa = int( sin(radians(organism.r)) * organism.vision_r + y1)

    # The border of the arc
    pygame.draw.line(screen, color, (xf1, yf1), (x1, y1), 1)
    pygame.draw.line(screen, color, (xf2, yf2), (x1, y1), 1)

    # The arc itself
    start_r = radians(-organism.r - organism.vision_fi)
    end_r = radians(-organism.r + organism.vision_fi)
    arc_x1 = x1-organism.vision_r
    arc_y1 = y1-organism.vision_r
    arc_r = organism.vision_r*2
    pygame.draw.arc(screen, color, (arc_x1, arc_y1, arc_r, arc_r), start_r, end_r, 1)

def draw_food(settings, screen, food):
    color = food.color
    radius = settings['food_r']
    pygame.draw.circle(screen, color, (int(food.x), int(food.y)), radius)

def dist(x1, y1, x2, y2):
    return sqrt( (x2-x1)**2 + (y2-y1)**2 )

class SceneBase:
    def __init__(self):
        self.next = self
    
    def ProcessInput(self, events, pressed_keys, settings):
        print("uh-oh, you didn't override this in the child class")

    def Update(self):
        print("uh-oh, you didn't override this in the child class")

    def Render(self, screen):
        print("uh-oh, you didn't override this in the child class")

    def SwitchToScene(self, next_scene):
        self.next = next_scene
    
    def Terminate(self):
        self.SwitchToScene(None)

class TitleScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
    
    def ProcessInput(self, events, pressed_keys, settings):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Move to the next scene when the user pressed Enter
                self.SwitchToScene(GameScene(settings))
    
    def Update(self, *argv):
        pass
    
    def Render(self, screen, settings, *argv):
        # For the sake of brevity, the title scene is a blank red screen
        screen.fill((0, 0, 0))
        # Add a Text
        font = pygame.font.SysFont("Impact", 72)
        text = font.render("Welcome to the game!", True, (255,255,255))
        screen.blit(text, ((settings['Window width'] // 2)-text.get_width() // 2, (settings['Window height'] // 2)-text.get_height() // 2))

# The rest is code where you implement your game using the Scenes model
class GameScene(SceneBase):
    def __init__(self, settings):
        SceneBase.__init__(self)

        self.highestSc = 0

        #--- Add food to the map ---------------+
        self.foods = []
        for i in range(0, settings['food_num']):
            self.foods.append(Food(settings))
        #--- Add organisms to the map ---------------+
        self.organisms = []
        for i in range(0, settings['pop_size']):
            self.organisms.append(Organism(settings, name= f'gen[x]-org[{str(i)}]' ))

    # Input buttons processing
    def ProcessInput(self, events, pressed_keys, settings):
        pass
    
    # When an organism reaches the border, 
    # act like it started over at the other edge
    def borderControl(self, settings, organism):
        if(organism.x > settings['x_max']):
            organism.x = settings['x_min']
            pass
        elif(organism.x < settings['x_min']):
            organism.x = settings['x_max']
            pass
        elif(organism.y > settings['y_max']):
            organism.y = settings['y_min']
            pass
        elif(organism.y < settings['y_min']):
            organism.y = settings['y_max']
            pass

    # Checks if one of the organism reached a food,
    # And what food is in vision range, 
    # Returns: The targets it sees sorted by increasing distance
    def interractWithFood(self, settings, organism):
        # foods that the organism sees
        targets = []

        for food in self.foods:
            # If the food dead count donw the respawn timer, 
            # when the respawn timer is 0 we can respawn the food, 
            # but if it is not 0 just skipp this food.
            if(food.dead == True):
                food.spawnCounter -= 1

                if(food.spawnCounter <= 0):
                    food.respawn(settings)
                else:
                    continue

            food_org_dist = dist(organism.x, organism.y, food.x, food.y)

            # Check what food is in vision of the org
            inVision = organism.isInVision(food)
            if(inVision == True):
                targets.append([food, food_org_dist])
                food.inVision()
            
            # Check if the org is close enough to eat the food.
            if(food_org_dist < (settings['food_r']+organism.size)):
                organism.fitness += food.energy
                organism.score += 1
                food.eaten()
        
        # This is not seeing any food, 
        if not targets:
            return None
        # If there are targets, Order the targets by distance
        else:
            targets.sort(key=lambda x: x[1])
            return targets[0][0]    #TODO we can give more than the first object to the network

    # Creates a child for the organism if it has enough food
    def createDescendant(self, settings, organism):
        # If higher than a treshold multipied with 2, it could have a descendant
        if(organism.fitness >= (settings['fission']*2)):
            organism.fitness -= settings['fission']
            # Copy parameters
            parameters = organism.get_parameters()
            # Create descendant with mutation
            self.organisms.append(Organism(settings, parameters=parameters))

    def starve(self, settings, organism, newOrganisms):
        organism.fitness -= 0.005
        if(organism.fitness <= 0):
            # Kill the organism
            pass
        else:
            # Dont kill it yet
            newOrganisms.append(organism)

    def Update(self, settings):

        # Set the default food color.
        for food in self.foods:
            if(food.dead == False):
                food.notInVision()

        # Array for the organism that we will keep
        newOrganisms = []
        highestScore = 0
        # Update location, find foods
        for organism in self.organisms:
            # Record highest score
            if(organism.score > highestScore):
                highestScore = organism.score
                organism.color = (220,80,220)
            else:
                organism.color = (40,40,220)
            
            # Update the location of the organisms
            organism.update_pos(settings)

            # Check starvation
            self.starve(settings, organism, newOrganisms)

            # Throws the organism to the other side of the map.
            self.borderControl(settings, organism)

            # Handles feeding, and in vision coloring
            target = self.interractWithFood(settings, organism)

            # Creates a child for the organism if it has enough food
            self.createDescendant(settings, organism)
            
            # TODO
            # I might want to pass everything or at least 
            # the closes 5 thing to the brain to think about it
            organism.think(settings, target)
        
        self.organisms = newOrganisms

        # If there are less organism than defined create new ones
        if(len(self.organisms) < settings['pop_size']):
            self.organisms.append(Organism(settings))
        
        if(self.highestSc != highestScore):
            self.highestSc = highestScore
            print("Highest Score:", self.highestSc)
    
    def Render(self, screen, settings):
        # The game scene is just a blank blue screen 
        screen.fill((255, 255, 255))

        #draw foods
        for food in self.foods:
            draw_food(settings, screen, food)

        #draw organisms
        for organism in self.organisms:
            draw_organism(screen, organism)
        
        #draw wall around the map, to make the game great again!
        #draw_wall(screen, settings)
