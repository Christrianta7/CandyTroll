import time
import random
from StateModel import *
from Counters import SoftwareTimer
from Button import Button
from Sensors import DigitalSensor
from Buzzer import PassiveBuzzer, DO, RE, MI
from LightStrip import LightStrip, RED, GREEN, BLUE, YELLOW, ORANGE
from Motors import Servo
from Displays import *



class GameController:
    def __init__(self):
        # Hardware Setup (Adjusted for simulator)
        self.display_question = LCDDisplay(sda=0, scl=1)  # Question LCD
        self.display_answer = LCDDisplay(sda=16, scl=17)  # Answer LCD

        self.buzzer = PassiveBuzzer(16)
        self.motion_sensor = DigitalSensor(pin=11, name='PIR', lowActive=False)
        self.lights = LightStrip(pin=18, numleds=4)
        self.candy_box_motor = Servo(pin=17, name='CandyBox')
        self.buttons = [
            Button(pin=6, name="Red"),
            Button(pin=7, name="Green"),
            Button(pin=8, name="Blue"),
            Button(pin=9, name="Yellow")
        ]

        # Temporary test button to trigger 'tripped' event
        self.test_button = Button(pin=13, name="Test")  

        # Game Variables
        self.questions = [
            {"question": "What spooky creature flies on a broom?",
             "answers": ["Witch", "Ghost", "Vampire", "Zombie"],
             "correct": 0},
            {"question": "What do you carve at Halloween?",
             "answers": ["Watermelons", "Pumpkins", "Turnips", "Cantaloupes"],
             "correct": 1},
            {"question": "What colors are associated with Halloween?",
             "answers": ["Red and Green", "Orange and Black", "Purple and Gold", "Blue and Silver"],
             "correct": 1},
            # ... Add more questions ...
        ]
        self.current_question = None
        self.score = 0
        self.time_limit = 15

        # State Model Setup
        self.model = StateModel(8, self, debug=True)
        for button in self.buttons:
            self.model.addButton(button)
        self.model.addButton(self.test_button)  # Add the test button to the model
        self.timer = SoftwareTimer(name="game_timer", handler=None)
        self.model.addTimer(self.timer)
        self.model.addCustomEvent("tripped")  # Add "tripped" event for motion

        # State Transitions
        self.model.addTransition(0, ["tripped"], 1)  # Standby to Intro
        self.model.addTransition(1, ["no_event"], 2)  # Intro to Question
        self.model.addTransition(2, ["Red_press", "Green_press", "Blue_press", "Yellow_press"],
                                 3)  # Question to Answer
        self.model.addTransition(2, ["game_timer_timeout"], 5)  # Question to Timeout (Lose)
        self.model.addTransition(3, ["no_event"], 4)  # Answer to Result
        self.model.addTransition(4, ["no_event"], 2)  # Result to Next Question
        self.model.addTransition(4, ["no_event"], 6)  # Result to Win
        self.model.addTransition(5, ["no_event"], 7)  # Timeout to Lose
        self.model.addTransition(6, ["no_event"], 0)  # Win to Standby
        self.model.addTransition(7, ["no_event"], 0)  # Lose to Standby

    # --- State Model Handlers (with delays) ---
    def stateEntered(self, state, event):
        if state == 0:  # Standby
            self.display_question.showText("Candy Troll")
            time.sleep(0.05)
            self.display_answer.showText("Press Button")
            time.sleep(0.05)
            self.lights.off()
        elif state == 1:  # Intro
            self.display_answer.clear()
            time.sleep(0.05)
            self.buzzer.beep(DO, 250)
            self.lights.setColor(ORANGE)
            time.sleep(1)
            self.score = 0
            self.current_question = random.choice(self.questions)
            self.display_question.showText(self.current_question["question"])
            time.sleep(0.05)
        elif state == 2:  # Question
            self.timer.start(self.time_limit)
            self.lights.setColor((0, 0, 0))
            self.display_answer.clear()
            time.sleep(0.05)
            self.display_answer.showText("Time: " + str(self.time_limit))
            time.sleep(0.05)
            self.set_answer_lights()
        elif state == 3:  # Answer
            self.timer.cancel()
            selected_answer = int(event[0]) - 1
            if selected_answer == self.current_question["correct"]:
                self.score += 1
                self.buzzer.beep(MI, 500)
                self.lights.setPixel(selected_answer, GREEN)
                self.display_answer.showText("Correct!")
                time.sleep(0.05)
            else:
                self.buzzer.beep(DO, 100)
                self.buzzer.beep(RE, 100)
                self.lights.setPixel(selected_answer, RED)
                self.display_answer.showText("Incorrect!")
                time.sleep(0.05)
        elif state == 4:  # Result
            time.sleep(2)
            if self.score >= 2:
                self.gotoState(6, "Win")
            elif self.current_question is not None:  
                self.current_question = random.choice(self.questions)
                self.display_question.showText(self.current_question["question"])
                time.sleep(0.05)
            else:
                self.gotoState(7, "Lose")
        elif state == 5:  # Timeout
            self.display_answer.showText("Too Slow!")
            time.sleep(0.05)
        elif state == 6:  # Win
            self.display_question.showText("You Win!")
            time.sleep(0.05)
            self.display_answer.clear()
            time.sleep(0.05)
            self.lights.setColor(GREEN)
            self.candy_box_motor.setAngle(90)  # Open (adjust angle as needed)
            time.sleep(5)
            self.candy_box_motor.setAngle(0)  # Close (adjust angle as needed)
        elif state == 7:  # Lose
            self.display_question.showText("Try Again")
            time.sleep(0.05)
            self.display_answer.clear()
            time.sleep(0.05)
            self.lights.setColor(RED)

    def stateLeft(self, state, event):
        if state == 2:
            self.timer.cancel()
        pass

    def stateDo(self, state):
        if state == 0:
            # if self.motion_sensor.tripped():  # Commented out for simulator
            #     self.model.processEvent("tripped") 
            if self.test_button.isPressed():
                self.model.processEvent("tripped")
        self.timer.check()

    def set_answer_lights(self):
        self.lights.setPixel(0, RED)
        self.lights.setPixel(1, GREEN)
        self.lights.setPixel(2, BLUE)
        self.lights.setPixel(3, YELLOW)

    def run(self):  # The missing method
        self.model.run()

    def stop(self): # The missing method
        self.model.stop()

# Example Usage
game = GameController()
try:
    game.start()
except KeyboardInterrupt:
    game.stop()