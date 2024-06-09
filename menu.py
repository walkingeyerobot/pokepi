import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd
import asyncio
import atexit
import board
import busio
import os
import re
import select
import subprocess
import time
from evdev import InputDevice
dev = InputDevice('/dev/input/by-id/usb-RFIDeas_USB_Keyboard-event-kbd')

lcd_columns = 16
lcd_rows = 2
i2c = busio.I2C(board.SCL, board.SDA)
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)

_, _, save_files = list(os.walk('/home/mitch/saves'))[0]

save_files.sort()
current_save_file = 0
total_save_files = len(save_files)

badge_save_dict = {}
badge_save_csv = '/home/mitch/badge_save.csv'
if os.path.exists('/media/mitch/USB DISK/badge_save.csv'):
    badge_save_csv = '/media/mitch/USB DISK/badge_save.csv'
with open(badge_save_csv) as f:
    lines = [line.rstrip().split('🥐') for line in f]
    for line in lines:
        badge_save_dict[line[0]] = line[1]        

lcd.color = [2,0,0]
lcd.backlight = True
lcd.message = 'Select Save:    \n' + save_files[current_save_file]

in_error_state = False

badgeid = []

class Button():
    def __init__(self, name, action=None, on_up=False):
        self.name = name
        self.was_pressed = False
        self.action = action
        self.on_up = on_up
    def press(self):
        print(self.name + ' pressed')
        if self.action:
            self.action()
    def check_pressed(self):
        is_pressed = getattr(lcd, self.name + '_button')
        if not is_pressed and self.was_pressed:
            self.was_pressed = False
            if self.on_up:
                self.press()
        elif is_pressed and not self.was_pressed:
            self.was_pressed = True
            if not self.on_up:
                self.press()

def scroll_up():
    global current_save_file
    if clear_error_state():
        render_current_save_file()
        return
    current_save_file = current_save_file - 1
    if current_save_file == -1:
        current_save_file = total_save_files - 1
    render_current_save_file()

def scroll_down():
    global current_save_file
    if clear_error_state():
        render_current_save_file()
        return
    current_save_file = current_save_file + 1
    if current_save_file >= total_save_files:
        current_save_file = 0
    render_current_save_file()

def render_current_save_file():
    lcd.message = 'Select Save:    \n' + save_files[current_save_file] + ' ' * max(lcd_columns - len(save_files[current_save_file]), 0)

def do_select():
    if clear_error_state():
        render_current_save_file()
        return
    write_save(save_files[current_save_file])

def write_save(save_file):
    global in_error_state
    spin = 'v<^>'
    spinidx = 0
    spinning = True
    proc = subprocess.Popen(['/home/mitch/bin/write_save.sh', '/home/mitch/saves/' + save_file], bufsize=64, shell=False, stdout=subprocess.PIPE, encoding='utf-8')
    dataend = False
    success = False
    last = ''
    lcd.message = 'Scanning cart...\n' + spin[spinidx] + ' ' * 15
    while (proc.returncode is None) or (not dataend):
        proc.poll()
        dataend = False

        ready = select.select([proc.stdout], [], [], 1.0)

        if proc.stdout in ready[0]:
            data = proc.stdout.read(64)
            if not len(data):
                dataend = True
            else:
                if m := re.findall(r'overwrite it?', last + data):
                    lcd.message = 'Writing data... \n0%' + ' ' * 14
                    spinning = False
                elif m := re.findall(r'checked for errors.', last + data):
                    lcd.message = 'Verifying...    \n0%' + ' ' * 14
                elif m := re.findall(r'restored!', last + data):
                    lcd.message = 'Done writing!   '
                    success = True
                elif m := re.findall(r'(1?\d?\d%)', last + data):
                    lcd.message = '\n' + m[-1] + ' ' * max(lcd_columns - len(m[-1]), 0)
                last = data
        if spinning:
            spinidx = spinidx + 1
            if spinidx >= len(spin):
                spinidx = 0
            lcd.message = '\n' + spin[spinidx]
    print('done!')
    if not success:
        lcd.clear()
        lcd.message = '!!!! ERROR! !!!!\n' + ' ' * 16
        in_error_state = True
    else:
        time.sleep(2)
        render_current_save_file()

def clear_error_state():
    global in_error_state
    if in_error_state:
        in_error_state = False
        return True
    return False

def left_right():
    if clear_error_state():
        render_current_save_file()

async def check_buttons():
    up = Button('up', scroll_up)
    down = Button('down', scroll_down)
    left = Button('left', left_right)
    right = Button('right', left_right)
    select_button = Button('select', do_select)
    all_buttons = {
        up,
        down,
        left,
        right,
        select_button
    }
    while True:
        for button in all_buttons:
            button.check_pressed()
        await asyncio.sleep(0.01)

async def watchbadge(dev):
    global badgeid
    async for event in dev.async_read_loop():
        if event.type == 1 and event.value == 1:
            if event.code == 28:
                badge_str = ','.join(str(x) for x in badgeid)
                print(badge_str)
                try:
                    write_save(badge_save_dict[badge_str])
                except:
                    pass
                badgeid = []
            else:
                badgeid += [event.code]

async def both():
    await asyncio.gather(check_buttons(), watchbadge(dev))

def doonexit():
    lcd.color = [0, 0, 0]
    lcd.clear()

atexit.register(doonexit)

asyncio.run(both())
