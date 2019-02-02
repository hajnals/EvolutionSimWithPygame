from random import uniform
from numpy.random import normal
from numpy.random import random_integers
from math import cos
from math import sin
from math import radians
from math import sqrt
from math import atan2
from math import pi
import numpy as np

#Keras
import keras
from keras import backend as K
from keras.models import Sequential
from keras.layers import Activation
from keras.layers.core import Dense
from keras.optimizers import Adam #Might not need this
from keras.metrics import categorical_crossentropy
from keras.initializers import RandomUniform
from keras.initializers import RandomNormal

def dist(x1, y1, x2, y2):
    return sqrt( (x2-x1)**2 + (y2-y1)**2 )

# An organism, shoould be able to see in from of it for different distance in different angle.
# The distance and the angle should be a parameter that they are get at their creation, 
# but they cannot change during lifespawn.
#
# They are required food to survive, if they dont eat for a certain cycle, they will die.
# That time is calculated from their properties like:
# Mass, age, speed (degradation during their lifespaw, the faster they go the sooner they die).
#
# Abel to change its size during their lifespaw. This depends on the food, 
# and something like a Growth-rate parameter.
#
# They should be able to choose diet, but they cannot change it during their lifespawn.
# 
# They should have a sets of parameters, like genomes, that are defines their appearance
# Some of there parameters are changable during lifespawn, and some are not.
class Organism():
    def __init__(self, settings, name=None, parameters=None):
        self.x = round(uniform(settings['x_min'], settings['x_max']), 0)
        self.y = round(uniform(settings['y_min'], settings['y_max']), 0)

        self.r = uniform(0,360)                                     # the direction of the organism
        self.v = (settings['v_max']/2)                              # speed of the organism
        # self.v = uniform(1, settings['v_max'])                    # speed of the organism
        self.a = uniform(-settings['a_max'], settings['a_max'])     # acceleration of the organism

        #self.size = uniform(settings['org_rad_min'], settings['org_rad_max'])
        self.size = settings['org_r_min']
        self.color = (40,40,220)
        self.fitness = settings['fission']
        self.score = 0

        self.vision_r = settings['org_vis_r']
        self.vision_fi = settings['org_vis_fi']

        # The neural network model
        self.mymodel = None
        self.createNeturalNetwork(settings, parameters)
    
    # Create and initialize the neural network of the organism
    def createNeturalNetwork(self, settings, parameters):        
        # Set the random uniform values
        RandomNormal(mean=0.0, stddev=0.5)

        l1 = Dense(2, input_shape=(1,), activation='relu', 
            kernel_initializer='RandomNormal', bias_initializer='RandomNormal')
        l2 = Dense(4, activation='relu', kernel_initializer='Ones', 
            bias_initializer='Zeros')
        o1 = Dense(1, activation='linear', 
            kernel_initializer='RandomNormal', bias_initializer='RandomNormal')
        self.mymodel = Sequential([l1, l2, o1])

        # Parameter is none when it is not a descendant organism
        if(parameters==None):
            pass
        else:
            # Modify something
            layer = random_integers(0, (len(parameters)-1) )
            w_or_b = random_integers(0, (len(parameters[layer])-1) )
            # Bias
            if(w_or_b == 1):
                node = random_integers(0, (len(parameters[layer][w_or_b])-1) )
                # Mutate
                parameters[layer][w_or_b][node] = normal(parameters[layer][w_or_b][node], 0.2)
            # Weight
            else:
                prevNode = random_integers(0, (len(parameters[layer][w_or_b])-1) )
                node = random_integers(0, (len(parameters[layer][w_or_b][prevNode])-1) )
                # Mutate
                parameters[layer][w_or_b][prevNode][node] = normal(parameters[layer][w_or_b][prevNode][node], 0.2)

            self.mymodel.layers[0].set_weights(parameters[0])
            self.mymodel.layers[1].set_weights(parameters[1])

        # Info about the network
        # self.mymodel.summary()

    # Changes the direction and the speed of an orgasim 
    # according to the decision it took from food positions
    def update_pos(self, settings):
        dx = self.v * cos(radians(self.r))
        dy = self.v * sin(radians(self.r))
        self.x += dx
        self.y += dy
    
    # Checks if food is inside the vision of an organism
    # Returns True if yes, False if not
    def isInVision(self, food):
        xbase = int( cos(radians(self.r)) * self.vision_r + self.x)
        ybase = int( sin(radians(self.r)) * self.vision_r + self.y)

        vbase = [(xbase - self.x), (ybase - self.y)]
        vfood = [(food.x - self.x), (food.y - self.y)]

        retval = True
        distance = dist(food.x, food.y, self.x, self.y)
        if(distance <= self.vision_r):
            retval = True

            angle = atan2(vfood[1], vfood[0]) - atan2(vbase[1], vbase[0])
            if(angle < 0):
                angle += 2*pi
            angle = angle * (180/pi)

            if((angle <= self.vision_fi) or (angle >= (360-self.vision_fi))):
                retval = True
            else:
                retval = False

        else:
            retval = False
        return retval

    # Get the target(s) parameters, and chosses an action 
    def think(self, settings, target):
        if(target == None):
            angle = 0
            distance = 1
        else:
            # Calculate distance
            distance = dist(target.x, target.y, self.x, self.y)

            # Calculate the degree
            xbase = int( cos(radians(self.r)) * self.vision_r + self.x)
            ybase = int( sin(radians(self.r)) * self.vision_r + self.y)
            vbase = [(xbase - self.x), (ybase - self.y)]
            vfood = [(target.x - self.x), (target.y - self.y)]
            angle = atan2(vfood[1], vfood[0]) - atan2(vbase[1], vbase[0])
            if(angle < 0):
                angle += 2*pi
            angle = angle * (180/pi)
            if(angle >= 315):
                angle -= 360
            
            # Normalize the distance and the angle:
                # distance / max distance, angle / max angle
            distance = distance / settings['org_vis_r']
            angle = angle / settings['org_vis_fi']

        # Calculate danger
        # danger = dist( ((settings['x_min']+settings['x_max'])/2), ((settings['y_min']+settings['y_max'])/2), self.x, self.y)
        # danger = danger / dist(settings['x_min'], settings['y_min'], self.x, self.y)

        # Calculate the neural network output for this input
        self.get_neuralNetworkOutput(distance, angle)
        
        # Requirements for this function: 
            # Need a neural network
            # inputs should be the angle to the food
            # and the distance to the food
            # we can calculate these form the coordinates of the food and the organism
    
    # Get the output of the neural network for a certain input
    # Sets the self.v and self.r values
    def get_neuralNetworkOutput(self, distance, angle):
        my_input = np.array([[angle]])
        predictions = self.mymodel.predict(my_input)
        
        #print("\nInput:", my_input)
        #print("Output:", predictions)
        self.r = predictions[0][0]*360

    # Returns the weights and biases
    def get_parameters(self):
        #wL1 = self.mymodel.layers[0].get_weights()[0]
        #bL1 = self.mymodel.layers[0].get_weights()[1]
        #wL2 = self.mymodel.layers[1].get_weights()[0]
        #bL2 = self.mymodel.layers[1].get_weights()[1]
        pL1 = self.mymodel.layers[0].get_weights()
        pL2 = self.mymodel.layers[1].get_weights()

        return ([pL1,pL2])

    def think_random(self, settings, target):
        if(target == None):
            return
        
        self.r = normal(self.r, 1)
        self.v = normal(self.v, 0.2)
        self.a = normal(self.a, 0.1)

        if( self.v > settings['v_max']):
            self.v = settings['v_max']
        if( self.v < -settings['v_max']):
            self.v = -settings['v_max']

class Food():
    def __init__(self, settings):
        self.x = round(uniform(settings['x_min'], settings['x_max']), 0)
        self.y = round(uniform(settings['y_min'], settings['y_max']), 0)
        
        # Different types of food should yield different energy level.
        self.energy = 1
        
        # Could be different kind of foods.
        self.type = None
        self.color = (40,220,40)
        self.spawnCounter = 0
        self.dead = False
        self.seen = False

    def respawn(self, settings):
        self.x = round(uniform(settings['x_min'], settings['x_max']), 0)
        self.y = round(uniform(settings['y_min'], settings['y_max']), 0)
        
        self.spawnCounter = 0
        self.dead = False
        self.color = (40,220,40)

    def eaten(self):
        self.spawnCounter = 1000
        self.dead = True
        self.color = (0,0,0)
    
    def inVision(self):
        self.seen = True
        self.color = (220,80,80)
    
    def notInVision(self):
        self.seen = False
        self.color = (40,220,40)