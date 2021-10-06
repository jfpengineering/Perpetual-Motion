# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////

import math
import sys
import time
import threading

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.config import Config
from kivy.core.window import Window
from pidev.kivy import DPEAButton
from pidev.kivy import PauseScreen
from time import sleep
import RPi.GPIO as GPIO 
from pidev.stepper import stepper
from pidev.Cyprus_Commands import Cyprus_Commands_RPi as cyprus

s0 = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
             steps_per_unit=200, speed=3)

# ////////////////////////////////////////////////////////////////
# //                      GLOBAL VARIABLES                      //
# //                         CONSTANTS                          //
# ////////////////////////////////////////////////////////////////
ON = False
OFF = True
HOME = True
TOP = False
OPEN = False
CLOSE = True
YELLOW = .180, 0.188, 0.980, 1
BLUE = 0.917, 0.796, 0.380, 1
DEBOUNCE = 0.1
INIT_RAMP_SPEED = 150
RAMP_LENGTH = 725


# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////
class MyApp(App):
    def build(self):
        self.title = "Perpetual Motion"
        return sm

Builder.load_file('main.kv')
Window.clearcolor = (.1, .1,.1, 1) # (WHITE)

cyprus.open_spi()

# ////////////////////////////////////////////////////////////////
# //                    SLUSH/HARDWARE SETUP                    //
# ////////////////////////////////////////////////////////////////
sm = ScreenManager()

# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# //             SHOULD INTERACT DIRECTLY WITH HARDWARE         //
# ////////////////////////////////////////////////////////////////
	
# ////////////////////////////////////////////////////////////////
# //        DEFINE MAINSCREEN CLASS THAT KIVY RECOGNIZES        //
# //                                                            //
# //   KIVY UI CAN INTERACT DIRECTLY W/ THE FUNCTIONS DEFINED   //
# //     CORRESPONDS TO BUTTON/SLIDER/WIDGET "on_release"       //
# //                                                            //
# //   SHOULD REFERENCE MAIN FUNCTIONS WITHIN THESE FUNCTIONS   //
# //      SHOULD NOT INTERACT DIRECTLY WITH THE HARDWARE        //
# ////////////////////////////////////////////////////////////////
class MainScreen(Screen):
    version = cyprus.read_firmware_version()
    staircaseSpeedText = '0'
    rampSpeed = INIT_RAMP_SPEED
    staircaseSpeed = 40
    servo_gate = True

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.initialize()

    def toggleGate(self):
        cyprus.set_servo_position(2, .5)
        sleep(.6)
        cyprus.set_servo_position(2, .1)
        print("Open and Close gate here")

    def toggleStaircase(self):
        cyprus.set_pwm_values(1, period_value=100000, compare_value=25000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        sleep(11)
        cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        print("Turn on and off staircase here")
        
    def toggleRamp(self):
        # s0.start_relative_move(29)
        # while s0.is_busy():
        #     sleep(.1)
        # s0.go_until_press(0,40000)
        s0.start_relative_move(1.5)
        sleep(.5)
        while s0.get_position_in_units() < 29:
            s0.go_until_press(1, 10000)
            sleep(.1)
        s0.stop()
        #s0.go_to_position_threaded(57.669375)
        #sleep(10)
        #s0.go_to_position_threaded(0.0)
        #s0.run(1, 500)
        #sleep(11)
        #s0.stop()
        #s0.get_position_in_units()
        #sleep(.25)
        #s0.run(0, 700)
        #sleep(8)
        #s0.stop()
        #print("Move ramp up and down here")
        
    def auto(self):
        for i in range(5):
            s0.run(1, 500)
            sleep(11)
            s0.stop()
            sleep(.25)
            s0.run(0, 700)
            sleep(1)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=25000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            sleep(7)
            s0.stop()
            sleep(3.5)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            cyprus.set_servo_position(2, .5)
            sleep(1)
            cyprus.set_servo_position(2, .1)
            sleep(2)
            print("Run through one cycle of the perpetual motion machine")
        
    def setRampSpeed(self, speed):
        print("Set the ramp speed and update slider text")
        
    def setStaircaseSpeed(self, speed):
        print("Set the staircase speed and update slider text")
        
    def initialize(self):
        cyprus.initialize()
        cyprus.setup_servo(1)
        sleep(.1)
        cyprus.set_servo_position(2, .1)
        s0.go_until_press(0, 50000)
        if not s0.is_busy():
            s0.set_as_home()
        print(s0.get_position_in_units())

    def resetColors(self):
        self.ids.gate.color = YELLOW
        self.ids.staircase.color = YELLOW
        self.ids.ramp.color = YELLOW
        self.ids.auto.color = BLUE
    
    def quit(self):
        print("Exit")
        MyApp().stop()

sm.add_widget(MainScreen(name = 'main'))

# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

MyApp().run()
cyprus.close_spi()
