import cv2
import numpy as np
import os
import time
from subprocess import Popen

print('starting hdmi_rec.py')

record_video_cmd1 = 'ffmpeg -f pulse -ac 2 -i default -f v4l2 -framerate 30 -video_size 640x480 -i /dev/video0 -vcodec libx264 -preset ultrafast'.split(' ')
record_video_cmd2 = '-r 60 -update true /mnt/tmpfs/lastframe.png -y'.split(' ')
watch_video_cmd = 'ffmpeg -i /dev/video0 -r 60 -s 640x480 -update true /mnt/tmpfs/lastframe.png -y'.split(' ')

nosignal1 = cv2.cvtColor(cv2.imread('/home/mitch/nosignal1.png'), cv2.COLOR_BGR2GRAY)
nosignal2 = cv2.cvtColor(cv2.imread('/home/mitch/nosignal2.png'), cv2.COLOR_BGR2GRAY)
nosignal_threshold = 10

recording = False
ffmpeg_process = Popen(watch_video_cmd)
inactive_count = 0

def isActive():
    try:
        lastframe = cv2.cvtColor(cv2.imread('/mnt/tmpfs/lastframe.png'), cv2.COLOR_BGR2GRAY)
    except:
        return False
    height, width = lastframe.shape
    area = float(height*width)
    diff1 = cv2.subtract(nosignal1, lastframe)
    diff2 = cv2.subtract(nosignal2, lastframe)
    err1 = np.sum(diff1**2)
    err2 = np.sum(diff2**2)
    mse1 = err1/area
    mse2 = err2/area
    print('*****************')
    print(mse1)
    print(mse2)
    print('*****************')
    return mse1 > nosignal_threshold and mse2 > nosignal_threshold

def mainLoop():
    global ffmpeg_process
    global recording
    global inactive_count
    if not ffmpeg_process: # I think this is wrong. I think I need to call .poll() and then check .returncode
        print('no ffmpeg_process')
        exit(5)
    isa = isActive()
    if not isa:
        inactive_count = inactive_count + 1
    else:
        inactive_count = 0
    if recording and inactive_count > 10:
        print('stopping recording')
        if ffmpeg_process:
            ffmpeg_process.terminate()
            ffmpeg_process.wait()
        ffmpeg_process = Popen(watch_video_cmd)
        recording = False
    elif not recording and inactive_count == 0:
        print('starting recording')
        if ffmpeg_process:
            ffmpeg_process.terminate()
            ffmpeg_process.wait()
        ffmpeg_process = Popen(record_video_cmd1 + ['/home/mitch/Videos/' + time.strftime("%Y%m%d-%H%M%S") + '.mp4'] + record_video_cmd2)
        recording = True
    elif recording and inactive_count == 0:
        print('recording and active')
    elif not recording and inactive_count > 10:
        print('not recording and inactive')
    else:
        print('inactive_count: ' + str(inactive_count))

while True:
    mainLoop()
    time.sleep(5)
