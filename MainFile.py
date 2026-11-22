# =============================================================================
# Hola Smart HS1000 House Code - Combined File
# Target board : BBC micro:bit V2 (MicroPython)
# Version      : 1.1.1
#
# VERSION RULES
#   First number  : only changes when the project owner says so
#   Second number : relatively major change (e.g. combining two files)
#   Third number  : small change or bug fix
#
# VERSION LOG (short form - full log lives in the Google Doc changelog)
#   1.0.0 - Added a name to the file
#   1.1.0 - Added first source: "Initialize the servo" (servo on pin 1 -> 180)
#   1.1.1 - Removed the empty forever loop that was left in by accident
#
# HOW TO USE
#   1. Open python.microbit.org and make sure the board is set to micro:bit V2.
#   2. Paste or load this file and flash it to the micro:bit.
#   3. Every section below starts with a True/False switch.
#      True  = that section runs.
#      False = that section is skipped.
# =============================================================================

# This line brings in everything the micro:bit can do: pins, display, buttons,
# sleep(), and so on. It is the MicroPython equivalent of what MakeCode does
# automatically behind the scenes.
from microbit import *


# =============================================================================
# SECTION 1 - INITIALIZE THE SERVO
# Source file : microbit-Initialize_the_servo.hex
# Original MakeCode Python:
#     pins.servo_write_pin(AnalogPin.P1, 180)
#
# What it does: sends a servo signal on pin 1 that tells the servo to move to
# 180 degrees.
# =============================================================================

# ON/OFF SWITCH for this section. Set to False to skip it.
ENABLE_SERVO_INIT = True

# --- Settings for this section ---
SERVO_PIN = pin1          # The pin the servo signal wire is plugged into (P1)
SERVO_ANGLE = 180         # Target angle in degrees, 0 to 180
SERVO_PERIOD_MS = 20      # Servos expect a pulse every 20 ms (50 times a second)
SERVO_MIN_PULSE_US = 500  # Pulse length (microseconds) that means 0 degrees
SERVO_MAX_PULSE_US = 2500 # Pulse length (microseconds) that means 180 degrees


def servo_write(pin, angle):
    """Move a servo on `pin` to `angle` (0-180 degrees).

    MakeCode has a built-in pins.servo_write_pin(). MicroPython does not, so
    this function recreates it using PWM:
      1. Servos read the LENGTH of a pulse that repeats every 20 ms.
         About 0.5 ms = 0 degrees, about 2.5 ms = 180 degrees.
      2. MicroPython's write_analog() takes a number from 0 to 1023, which is
         how much of each 20 ms period the signal stays on.
      3. So we convert: angle -> pulse length -> a 0-1023 duty value.
    """
    # Keep the angle in the safe range so we never ask for something odd.
    if angle < 0:
        angle = 0
    if angle > 180:
        angle = 180

    # Step 1: angle -> pulse length in microseconds.
    pulse_us = SERVO_MIN_PULSE_US + (angle * (SERVO_MAX_PULSE_US - SERVO_MIN_PULSE_US)) / 180

    # Step 2: pulse length -> duty value (0-1023).
    # The full period is SERVO_PERIOD_MS * 1000 microseconds.
    duty = int(pulse_us / (SERVO_PERIOD_MS * 1000) * 1023)

    # Step 3: tell the pin to repeat the pulse every 20 ms, then set its width.
    pin.set_analog_period(SERVO_PERIOD_MS)
    pin.write_analog(duty)


def section_servo_init():
    """Runs once at start-up: moves the servo to SERVO_ANGLE."""
    if not ENABLE_SERVO_INIT:
        return  # Switch is off, so do nothing.
    servo_write(SERVO_PIN, SERVO_ANGLE)


# =============================================================================
# MAIN PROGRAM
# Runs each section in order. Each section checks its own switch above.
# =============================================================================

# Run once at start-up.
section_servo_init()
