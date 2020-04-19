from time import sleep
from random import randint

while True:
    sleep(0.05)
    print((randint(0, 100), randint(-100, 0), randint(-50, 50)))