# =============================================================================
# Hola Smart HS1000 House Code - Combined File
# Target board : BBC micro:bit V2
# Language     : MakeCode Python (the Python view inside makecode.microbit.org)
# Version      : 1.2.0
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
#   1.2.0 - Converted from MicroPython to MakeCode Python so the file works
#           in MakeCode. The servo code is now the original MakeCode command.
#
# HOW TO USE
#   1. Open makecode.microbit.org and make sure the project is set to
#      micro:bit V2 (the gear menu > Change Board, if needed).
#   2. Switch the editor to the Python view and paste this file in.
#   3. Every section below starts with a True/False switch.
#      True  = that section runs.
#      False = that section is skipped.
#
# NOTE: MakeCode already knows about pins, the display, buttons and so on,
# so unlike regular MicroPython there is no "import" line at the top.
# Comments (lines starting with #) are ignored by the micro:bit.
# =============================================================================


# =============================================================================
# SECTION 1 - INITIALIZE THE SERVO
# Source file : microbit-Initialize_the_servo.hex
# Original code:
#     pins.servo_write_pin(AnalogPin.P1, 180)
#
# What it does: sends a servo signal on pin 1 that tells the servo to move to
# 180 degrees. MakeCode has this command built in, so the original line is
# used as-is.
# =============================================================================

# ON/OFF SWITCH for this section. Set to False to skip it.
ENABLE_SERVO_INIT = True

# --- Settings for this section ---
# The pin the servo signal wire is plugged into (P1).
SERVO_PIN = AnalogPin.P1
# Target angle in degrees, 0 to 180.
SERVO_ANGLE = 180


def section_servo_init():
    # Runs once at start-up. If the switch above is False, do nothing.
    if not ENABLE_SERVO_INIT:
        return
    # Built-in MakeCode command: turn the servo on this pin to this angle.
    pins.servo_write_pin(SERVO_PIN, SERVO_ANGLE)


# =============================================================================
# MAIN PROGRAM
# Runs each section in order. Each section checks its own switch above.
# =============================================================================

# Run once at start-up.
section_servo_init()
