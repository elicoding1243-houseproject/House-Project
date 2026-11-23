# =============================================================================
# Hola Smart HS1000 House Code - Combined File
# Target board : BBC micro:bit V2
# Language     : MakeCode Python (the Python view inside makecode.microbit.org)
# Version      : 1.4.0
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
#   1.2.1 - Added a .mkcd project file for drag and drop into MakeCode.
#           Removed out-of-date board and Python-view steps from HOW TO USE.
#   1.3.0 - Combined in the second source: "10Bluetooth Smart Home"
#           (Sections 2-7). Converted from MakeCode blocks/TypeScript to
#           MakeCode Python. The .mkcd now loads the extensions it needs.
#   1.3.1 - Bluetooth fix: the listening loop now stops when the phone
#           disconnects (it used to keep running).
#   1.4.0 - Combined in the third source: "9Bluetooth APP Control LED"
#           (Section 8, a simple Bluetooth light controller).
#
# HOW TO USE
#   1. Go to makecode.microbit.org and drag the .mkcd file onto the editor.
#      It opens on micro:bit V2 in the Python view automatically.
#   2. Every section below starts with a True/False switch.
#      True  = that section runs.
#      False = that section is skipped.
#   3. Some sections need others (see "NEEDS" notes). Turning off a section
#      that another one needs can make the program stop with an error.
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
# used as-is. (In the smart home build this is the "window servo", so the
# window starts closed. The second source file had the same line at start-up;
# it is not repeated in Section 2 because this section already does it.)
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
# SECTIONS 2-7 - SMART HOME (BLUETOOTH, PASSWORD DOOR, SENSORS)
# Source file : microbit-10Bluetooth_Smart_Home.hex
# Extensions this needs (the .mkcd loads them for you): bluetooth, microphone,
# the keyestudio IoT kit (NeoPixel lights), and the SSD1306 OLED screen.
#
# What it does: a phone app sends single letters over Bluetooth. The micro:bit
# reacts by showing faces, running lights and music, moving servos, and
# switching sensors on. A password typed with buttons A and B opens the door.
#
# Phone commands (each letter ends with # when sent):
#   a = countdown + "Merry Christmas" + lights + Jingle Bells
#   b = stop music and lights, back to "Enter password"
#   c = window servo to 90      d = window servo to 180
#   g = fan on                  h = fan off
#   i = rainbow lights          j = warm white on small strip   k = lights off
#   1-6 = faces, 0 = clear      o = sound meter on
#   q = gas alarm on            r = motion alarm on     x = all sensors off
# =============================================================================


# --- Variables shared by Sections 2-7 (the program's "memory") ---
# The two light strips. They are created in Section 2.
strip: neopixel.Strip = None
strip2: neopixel.Strip = None
# Door password, and what has been typed so far with buttons A and B.
PASSWORD = "1001"
passwd_enter = ""
# 1 while a phone is connected (set back to 0 when it disconnects).
connect = 0
# The last Bluetooth message received.
ble_val = ""
# Set to 1 when the "a" command starts the countdown (not used elsewhere).
count_down = 0
# Sensor mode flags: 1 = that sensor is being watched.
db_flag = 0
prevent_flag = 0
alarm_flag = 0


# =============================================================================
# SECTION 2 - SMART HOME SETUP
# What it does: runs once at start-up. Sets up the USB serial link, the OLED
# screen, and the two light strips (all turned off).
# =============================================================================

# ON/OFF SWITCH for this section. Set to False to skip it.
ENABLE_SETUP = True

# --- Settings for this section ---
OLED_WIDTH = 128
OLED_HEIGHT = 64
STRIP_PIN = DigitalPin.P8    # Big strip: 12 lights
STRIP_LIGHTS = 12
STRIP2_PIN = DigitalPin.P9   # Small strip: 4 lights
STRIP2_LIGHTS = 4


def section_setup():
    global strip, strip2, passwd_enter
    if not ENABLE_SETUP:
        return
    # Send serial messages over the USB cable at 9600 speed.
    serial.redirect(SerialPin.USB_TX, SerialPin.USB_RX, BaudRate.BAUD_RATE9600)
    basic.show_icon(IconNames.HOUSE)
    # Start the OLED screen and ask for the password.
    OLED.init(OLED_WIDTH, OLED_HEIGHT)
    OLED.clear()
    basic.pause(100)
    OLED.write_string_new_line("Enter password:")
    # RGB LED strips: create them, then turn them off.
    strip = neopixel.create(STRIP_PIN, STRIP_LIGHTS, NeoPixelMode.RGB)
    strip2 = neopixel.create(STRIP2_PIN, STRIP2_LIGHTS, NeoPixelMode.RGB)
    strip2.set_brightness(255)
    strip.show_color(neopixel.colors(NeoPixelColors.BLACK))
    strip2.show_color(neopixel.colors(NeoPixelColors.BLACK))
    passwd_enter = ""


# =============================================================================
# SECTION 3 - MODE HELPERS (faces, lights, sensors)
# NEEDS: Section 2 (the light strips and OLED must be set up first).
# What it does: three small helpers that look at the last Bluetooth message
# (ble_val) and act on it. Section 5 calls them after every message.
# =============================================================================

# ON/OFF SWITCH for this section. Set to False to skip it.
ENABLE_MODE_HELPERS = True


def face_mode():
    # Letters "0" to "6" show a face or icon on the micro:bit screen.
    if not ENABLE_MODE_HELPERS:
        return
    if ble_val == "1":
        basic.show_icon(IconNames.HAPPY)
    elif ble_val == "2":
        basic.show_icon(IconNames.SAD)
    elif ble_val == "3":
        basic.show_icon(IconNames.ASLEEP)
    elif ble_val == "4":
        basic.show_icon(IconNames.HEART)
    elif ble_val == "5":
        basic.show_icon(IconNames.DUCK)
    elif ble_val == "6":
        basic.show_icon(IconNames.HOUSE)
    elif ble_val == "0":
        basic.clear_screen()


def neopixel_mode():
    # i = rainbow, j = warm white on the small strip, k = both strips off.
    if not ENABLE_MODE_HELPERS:
        return
    if ble_val == "i":
        strip.show_rainbow(1, 360)
    elif ble_val == "j":
        strip2.show_color(neopixel.rgb(255, 198, 187))
    elif ble_val == "k":
        strip.show_color(neopixel.colors(NeoPixelColors.BLACK))
        strip2.show_color(neopixel.colors(NeoPixelColors.BLACK))


def sensor_mode():
    # o = sound meter, q = gas alarm, r = motion alarm, x = all sensors off.
    # This only sets the flags. Section 7 does the actual watching.
    global db_flag, prevent_flag, alarm_flag
    if not ENABLE_MODE_HELPERS:
        return
    if ble_val == "o":
        OLED.clear()
        db_flag = 1
    elif ble_val == "q":
        prevent_flag = 1
    elif ble_val == "r":
        alarm_flag = 1
    elif ble_val == "x":
        db_flag = 0
        alarm_flag = 0
        prevent_flag = 0
        OLED.clear()
        OLED.write_string_new_line("Enter password")


# =============================================================================
# SECTION 4 - JINGLE BELLS
# What it does: plays the tune Jingle Bells (command "a" starts it).
# Each line plays one note: the number is the pitch, and the beat is how long.
# =============================================================================

# ON/OFF SWITCH for this section. Set to False to skip it.
ENABLE_JINGLE_BELLS = True


def jingle_bells():
    if not ENABLE_JINGLE_BELLS:
        return
    music.play(music.tone_playable(330, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(330, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(330, music.beat(BeatFraction.WHOLE)), music.PlaybackMode.UNTIL_DONE)
    basic.pause(100)
    music.play(music.tone_playable(330, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(330, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(330, music.beat(BeatFraction.WHOLE)), music.PlaybackMode.UNTIL_DONE)
    basic.pause(100)
    music.play(music.tone_playable(330, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(392, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(262, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(294, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(330, music.beat(BeatFraction.WHOLE)), music.PlaybackMode.UNTIL_DONE)
    basic.pause(200)
    music.play(music.tone_playable(349, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(349, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(349, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(349, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)
    basic.pause(100)
    music.play(music.tone_playable(349, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(330, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(330, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(330, music.beat(BeatFraction.QUARTER)), music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(330, music.beat(BeatFraction.QUARTER)), music.PlaybackMode.UNTIL_DONE)
    basic.pause(100)
    music.play(music.tone_playable(392, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(392, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(349, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(294, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(262, music.beat(BeatFraction.HALF)), music.PlaybackMode.UNTIL_DONE)


# =============================================================================
# SECTION 5 - BLUETOOTH CONTROL
# NEEDS: Section 2 (setup). Uses Sections 3 and 4 when they are on.
# What it does: when a phone connects, listens for letters and acts on them
# (see the command list above). When it disconnects, shows an X and stops
# listening. If Section 8 is on, it takes over Bluetooth instead and this
# section is not plugged in.
# =============================================================================

# ON/OFF SWITCH for this section. Set to False to skip it.
ENABLE_BLUETOOTH = True


def on_bluetooth_connected():
    global connect, ble_val, count_down
    basic.show_icon(IconNames.YES)
    connect = 1
    # Keep listening. Each message ends with a # character.
    while connect == 1:
        ble_val = bluetooth.uart_read_until(serial.delimiters(Delimiters.HASH))
        # Echo the message to the USB serial link.
        serial.write_string(ble_val)
        serial.write_line("")
        if ble_val == "a":
            # Countdown 3, 2, 1, then Christmas lights and music.
            count_down = 1
            basic.show_leds("""
                . # # # .
                . . . # .
                . # # # .
                . . . # .
                . # # # .
                """)
            basic.pause(1000)
            basic.show_leds("""
                . # # # .
                . . . # .
                . # # # .
                . # . . .
                . # # # .
                """)
            basic.pause(1000)
            basic.show_leds("""
                . . # . .
                . # # . .
                . . # . .
                . . # . .
                . # # # .
                """)
            basic.pause(1000)
            basic.clear_screen()
            OLED.clear()
            basic.show_icon(IconNames.HAPPY)
            OLED.write_string("Merry Christmas!")
            strip.show_rainbow(1, 360)
            strip2.show_color(neopixel.rgb(255, 198, 187))
            jingle_bells()
        elif ble_val == "b":
            # Stop everything and go back to the password screen.
            count_down = 0
            basic.show_icon(IconNames.YES)
            OLED.clear()
            OLED.write_string_new_line("Enter password")
            music.stop_all_sounds()
            strip.show_color(neopixel.colors(NeoPixelColors.BLACK))
            strip2.show_color(neopixel.colors(NeoPixelColors.BLACK))
        elif ble_val == "c":
            # Window servo to 90 degrees.
            pins.servo_write_pin(AnalogPin.P1, 90)
        elif ble_val == "d":
            # Window servo to 180 degrees.
            pins.servo_write_pin(AnalogPin.P1, 180)
        elif ble_val == "g":
            # Fan on. P12 is IN+ and P13 is IN- on the motor driver.
            OLED.clear()
            basic.clear_screen()
            basic.pause(100)
            pins.analog_write_pin(AnalogPin.P12, 1023)
            pins.analog_write_pin(AnalogPin.P13, 300)
        elif ble_val == "h":
            # Fan off.
            pins.analog_write_pin(AnalogPin.P12, 0)
            pins.analog_write_pin(AnalogPin.P13, 0)
            basic.show_icon(IconNames.HAPPY)
        # After every message, check the faces, lights and sensor commands.
        neopixel_mode()
        face_mode()
        sensor_mode()


def on_bluetooth_disconnected():
    global connect
    # Tell the listening loop above to stop.
    connect = 0
    basic.show_icon(IconNames.NO)


# =============================================================================
# SECTION 6 - PASSWORD DOOR (BUTTONS AND TOUCH LOGO)
# NEEDS: Section 2 (the OLED screen).
# What it does: button A types a 1, button B types a 0. Pressing A and B
# together checks the password. If right, the door servo (pin 1) opens to 90.
# If wrong, it shows an error and clears what was typed. Touching the logo
# closes the door and starts over.
# =============================================================================

# ON/OFF SWITCH for this section. Set to False to skip it.
ENABLE_PASSWORD_DOOR = True


def on_button_pressed_a():
    global passwd_enter
    OLED.write_string_new_line("1")
    passwd_enter = passwd_enter + "1"


def on_button_pressed_b():
    global passwd_enter
    OLED.write_string_new_line("0")
    passwd_enter = passwd_enter + "0"


def on_button_pressed_ab():
    global passwd_enter
    OLED.clear()
    if passwd_enter == PASSWORD:
        OLED.write_string_new_line("Successful!")
        OLED.new_line()
        OLED.write_string_new_line("Open the door")
        pins.servo_write_pin(AnalogPin.P1, 90)
    else:
        OLED.write_string_new_line("Error!")
        OLED.new_line()
        OLED.write_string_new_line("Error again")
        passwd_enter = ""
        basic.pause(1000)
        OLED.clear()
        OLED.write_string_new_line("Enter password:")
        OLED.new_line()
        pins.servo_write_pin(AnalogPin.P1, 180)


def on_logo_pressed():
    global passwd_enter
    OLED.clear()
    OLED.write_string_new_line("Close the door")
    # Door servo back to 180 degrees.
    pins.servo_write_pin(AnalogPin.P1, 180)
    basic.pause(1000)
    passwd_enter = ""
    OLED.clear()
    OLED.write_string_new_line("Enter password")
    OLED.new_line()


# =============================================================================
# SECTION 7 - SENSOR WATCHING (FOREVER LOOP)
# NEEDS: Section 2 (OLED and lights). The flags are set by Section 3.
# What it does: repeats forever and checks whichever sensor was switched on:
#   sound meter (o) - shows the noise level on the OLED
#   gas alarm (q)   - gas sensor on pin 5; alarm sound + red flashing lights
#   motion alarm (r) - infrared body sensor on pin 2; warns and beeps
# =============================================================================

# ON/OFF SWITCH for this section. Set to False to skip it.
ENABLE_SENSOR_LOOP = True


def on_forever():
    if db_flag == 1:
        OLED.write_string("decibel")
        OLED.new_line()
        OLED.write_num_new_line(input.sound_level())
        basic.pause(500)
    elif prevent_flag == 1:
        # Gas sensor module.
        if pins.digital_read_pin(DigitalPin.P5) == 1:
            music.play(music.tone_playable(262, music.beat(BeatFraction.WHOLE)), music.PlaybackMode.UNTIL_DONE)
            OLED.write_string_new_line("Alarming")
            strip.show_color(neopixel.colors(NeoPixelColors.RED))
            basic.pause(100)
            strip.show_color(neopixel.colors(NeoPixelColors.BLACK))
            basic.pause(100)
        else:
            strip.show_color(neopixel.colors(NeoPixelColors.BLACK))
            music.stop_melody(MelodyStopOptions.ALL)
            OLED.write_string_new_line("Remaining normal")
            basic.pause(200)
    elif alarm_flag == 1:
        # Human body infrared sensor.
        if pins.digital_read_pin(DigitalPin.P2) == 1:
            OLED.clear()
            OLED.write_string_new_line("Look out! There's someone!")
            music.play(music.tone_playable(262, music.beat(BeatFraction.WHOLE)), music.PlaybackMode.UNTIL_DONE)
        else:
            OLED.clear()
            OLED.write_string_new_line("All goes well.")
            music.stop_melody(MelodyStopOptions.ALL)


# =============================================================================
# SECTION 8 - BLUETOOTH APP CONTROL LED (SIMPLE VERSION)
# Source file : microbit-9Bluetooth_APP_Control_LED.hex
# NEEDS: nothing if Section 2 is off (it sets up its own serial link and
#        small light strip). If Section 2 is on, it reuses Section 2's setup.
#
# What it does: a smaller, stand-alone Bluetooth controller. Same idea as
# Section 5 but it only controls the small 4-light strip:
#   j = warm white on     k = off
#
# IMPORTANT: Sections 5 and 8 both listen for Bluetooth, and only one can be
# in charge. If both switches are True, Section 8 wins and Section 5 is not
# plugged in. It starts OFF because Section 5 already does everything this
# section does (j turns the small strip on; k turns BOTH strips off).
# =============================================================================

# ON/OFF SWITCH for this section. Set to True to use it instead of Section 5.
ENABLE_BLUETOOTH_LED_ONLY = False

# --- Variables for this section ---
# 1 while a phone is connected, and the last message received.
led_connect = 0
led_ble_val = ""


def section_led_setup():
    # Runs once at start-up. Skipped if Section 2 already did this work.
    global strip2
    if not ENABLE_BLUETOOTH_LED_ONLY:
        return
    if ENABLE_SETUP:
        return
    # Send serial messages over the USB cable (the simple, default way).
    serial.redirect_to_usb()
    # The small light strip (uses the pin and size set in Section 2).
    strip2 = neopixel.create(STRIP2_PIN, STRIP2_LIGHTS, NeoPixelMode.RGB)


def on_led_bluetooth_connected():
    global led_connect, led_ble_val
    basic.show_icon(IconNames.YES)
    led_connect = 1
    # Keep listening. Each message ends with a # character.
    while led_connect == 1:
        led_ble_val = bluetooth.uart_read_until(serial.delimiters(Delimiters.HASH))
        # Echo the message to the USB serial link.
        serial.write_string(led_ble_val)
        serial.write_line("")
        if led_ble_val == "j":
            strip2.show_color(neopixel.rgb(255, 198, 187))
        elif led_ble_val == "k":
            strip2.show_color(neopixel.colors(NeoPixelColors.BLACK))


def on_led_bluetooth_disconnected():
    global led_connect
    # Tell the listening loop above to stop.
    led_connect = 0
    basic.show_icon(IconNames.NO)


# =============================================================================
# MAIN PROGRAM
# Runs each section in order. Each section checks its own switch above.
# Event sections (5, 6, 7, 8) are only "plugged in" when their switch is True.
# =============================================================================

# Run once at start-up.
section_servo_init()
section_setup()
section_led_setup()

# Bluetooth events. Only one section can be in charge of Bluetooth:
# Section 8 if its switch is on, otherwise Section 5.
if ENABLE_BLUETOOTH_LED_ONLY:
    bluetooth.on_bluetooth_connected(on_led_bluetooth_connected)
    bluetooth.on_bluetooth_disconnected(on_led_bluetooth_disconnected)
elif ENABLE_BLUETOOTH:
    bluetooth.on_bluetooth_connected(on_bluetooth_connected)
    bluetooth.on_bluetooth_disconnected(on_bluetooth_disconnected)

# Section 6: buttons and touch logo.
if ENABLE_PASSWORD_DOOR:
    input.on_button_pressed(Button.A, on_button_pressed_a)
    input.on_button_pressed(Button.B, on_button_pressed_b)
    input.on_button_pressed(Button.AB, on_button_pressed_ab)
    input.on_logo_event(TouchButtonEvent.PRESSED, on_logo_pressed)

# Section 7: the forever loop.
if ENABLE_SENSOR_LOOP:
    basic.forever(on_forever)
