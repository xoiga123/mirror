from PIL import Image
from PIL import ImageGrab
import keyboard

while True:
    keyboard.wait("ctrl+q")
    im = ImageGrab.grab(include_layered_windows=True)
    im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im.show()
    