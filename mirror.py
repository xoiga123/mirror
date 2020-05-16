import numpy as np
import pyautogui
import cv2
import keyboard

events = [i for i in dir(cv2) if 'EVENT' in i]
print( events )

print("Please enter the keys you wanna use to capture screen.")
print("Type 'done' when completed.")
print("Shift and Ctrl can't be recorded, so just type in 'shift' or 'ctrl' if you want to use them in combination with other keys.")
print("Example: to use ctrl + q, type ctrl, then next line type q, then next line type done.")
print("Im not doing any input checking so if the program breaks, thats on you, and just restart the program.")

keys = ""
while True:
    inp = input("Type a key ('done' to confirm): ")
    if inp == "done": break
    keys += inp + "+"
keys = keys[:-1]
print("Keys recorded, to capture screen use " + keys)

scale = int(input("Enter scale percent to resize the image (100 is the original): "))
print("To close the image, press any key, or escape key to exit the program.")
print("To exit the program, either close the cmd, or press escape key when an image is showing.")

while True:
    keyboard.wait(keys)
    image = pyautogui.screenshot()
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    flipHorizontal = cv2.flip(image, 1)
    width = int(flipHorizontal.shape[1] * scale / 100)
    height = int(flipHorizontal.shape[0] * scale / 100)
    dim = (width, height)
    resized = cv2.resize(flipHorizontal, dim)
    cv2.imshow("Mirrored", resized)
    k = cv2.waitKey(0)
    #print(k)
    cv2.destroyAllWindows()
    if k == 27:
        break