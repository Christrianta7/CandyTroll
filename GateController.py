"""
A basic template file for using the Model class in PicoLibrary
This will allow you to implement simple Statemodels with some basic
event-based transitions.
"""

# Import whatever Library classes you need - StateModel is obviously needed
# Counters imported for Timer functionality, Button imported for button events
import time
import random
from Log import *
from StateModel import *
from Counters import *
from Button import *
from Displays import *
from Buzzer import *
from Gate import *


"""
This is the template for a Controller - you should rename this class to something
that is supported by your class diagram. This should associate with your other
classes, and any PicoLibrary classes. If you are using Buttons, you will implement
buttonPressed and buttonReleased.

To implement the state model, you will need to implement __init__ and 4 other methods
to support model start, stop, entry actions, exit actions, and state actions.

The following methods must be implemented:
__init__: create instances of your View and Business model classes, create an instance
of the StateModel with the necessary number of states and add the transitions, buttons
and timers that the StateModel needs

stateEntered(self, state, event) - Entry actions
stateLeft(self, state, event) - Exit actions
stateDo(self, state) - do Activities

# A couple other methods are available - but they can be left alone for most purposes

run(self) - runs the State Model - this will start at State 0 and drive the state model
stop(self) - stops the State Model - will stop processing events and stop the timers

This template currently implements a very simple state model that uses a button to
transition from state 0 to state 1 then a 5 second timer to go back to state 0.
"""

class GateController:

    def __init__(self):
        
        # Instantiate whatever classes from your own model that you need to control
        # Handlers can now be set to None - we will add them to the model and it will
        # do the handling

        self.gate = Gate()
        self.display = LCDDisplay(sda=0, scl=1)
        self.buzzer = PassiveBuzzer(16)

        # Instantiate a Model. Needs to have the number of states, self as the handler
        # You can also say debug=True to see some of the transitions on the screen
        # Here is a sample for a model with 4 states
        self.model = StateModel(5, self, debug=True)
        
        # Instantiate any Buttons that you want to process events from and add
        # them to the model
        self._button = Button(9, "b", handler=None)        
        self.model.addButton(self._button)
        
        # add other buttons if needed. Note that button names must be distinct
        # for all buttons. Events will come back with [buttonname]_press and
        # [buttonname]_release
        self.model.addCustomEvent('motion')
        self.model.addCustomEvent('presence')
        self.model.addCustomEvent('nonpresence')        
        # Add any timer you have. Multiple timers may be added but they must all
        # have distinct names. Events come back as [timername}_timeout
        self._timer = SoftwareTimer(name="t", handler=None)
        self.model.addTimer(self._timer)

        # Add any custom events as appropriate for your state model. e.g.
        # self.model.addCustomEvent("collision_detected")
        
        # Now add all the transitions from your state model. Any custom events
        # must be defined above first. You can have a state transition to another
        # state based on multiple events - which is why the eventlist is an array
        # Syntax: self.model.addTransition( SOURCESTATE, [eventlist], DESTSTATE)
        
        # some examples:
        self.model.addTransition(0, ["b_press"], 1)
        self.model.addTransition(1, ["b_press"], 0)

        self.model.addTransition(0, ["motion"], 2)
        self.model.addTransition(2, ["t_timeout"], 0)
        
        self.model.addTransition(2, ["presence"], 3)
        self.model.addTransition(3, ["nonpresence"], 4)
        self.model.addTransition(4, ["t_timeout"], 0)
    
    def stateEntered(self, state, event):
        """
        stateEntered - is the handler for performing entry actions
        You get the state number of the state that just entered
        Make sure actions here are quick
        """
        
        # If statements to do whatever entry/actions you need for
        # for states that have entry actions
        Log.d(f'State {state} entered on event {event}')
        if state == 0:
            # entry actions for state 0
            self.display.showText('Welcome Home')
            self.gate.close()
        elif state == 1:
            # entry actions for state 1
            self.display.showText('Door is opening')
            self.gate.open()
        elif state ==2:
            self.display.showText('Door is opening')
            self._timer.start(5)

        elif state ==3:
            self.display.ShowText('Caution Go Quick')
            self.gate.open()

        elif state == 4:
            self.display.showText('Door Closing')
            self._timer.start(5)

    def stateLeft(self, state, event):
        """
        stateLeft - is the handler for performing exit/actions
        You get the state number of the state that just entered
        Make sure actions here are quick
        
        This is just like stateEntered, perform only exit/actions here
        """

        Log.d(f'State {state} exited on event {event}')
        if state == 2:
            # exit actions for state 0
            self._timer.cancel()
        elif state==4:
            self._timer.cancel()
        # etc.
    
    def stateDo(self, state):
        """
        stateDo - the method that handles the do/actions for each state
        """
        
        # Now if you want to do different things for each state that has do actions
        if state == 0:
            # State 0 do/actions
            if self.gate.checkMotion():
                self.model.processEvent('motion')


        elif state == 2:
            
            if self.gate.checkPresence():
                self.model.processEvent('presence')
        
        elif state == 3:
            if not self.gate.CheckPresence():
                self.model.processEvent('nonpresence')

    def run(self):
        """
        Create a run() method - you can call it anything you want really, but
        this is what you will need to call from main.py or someplace to start
        the state model.
        """
        
        # The run method should simply do any initializations (if needed)
        # and then call the model's run method.
        # You can send a delay as a parameter if you want something other
        # than the default 0.1s. e.g.,  self.model.run(0.25)
        self.model.run()

    def stop(self):
        # The stop method should simply do any cleanup as needed
        # and then call the model's stop method.
        # This removes the button's handlers but will need to see
        # if the IRQ handlers should also be removed
        self.model.stop()
        

# Test your model. Note that this only runs the template class above
# If you are using a separate main.py or other control script,
# you will run your model from there.
if __name__ == '__main__':
    p = GateController()
    try:
        p.run()
    except KeyboardInterrupt:
        p.stop()    
