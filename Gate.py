"""
    Gate.py
    Implementation of our gate...

"""
from Sensors import *
from Motors import *

OPENANGLE = 0
CLOSEANGLE = 90

class Gate: 
    """
    Gate Class.......
    """

    def __init__(self):
        self.openstatus = False
        self.motionsensor = DigitalSensor(pin=11, name='PIR', lowActive=False)
        self.proxsensor = DigitalSensor(pin=10, name='prox')
        self.servo = Servo(pin=21, name='Gate')

    def open(self):
        """
        """
        self.servo.setAngle(OPENANGLE)

    def close(self):
        """
        """
        self.servo.setAngle(CLOSEANGLE)

    def checkPresence(self)->bool:
        """
        """
        return self.proxsensor.tripped()

    def checkMotion(self)->bool:
        """
        """
        return self.motionsensor.tripped()
