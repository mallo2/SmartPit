import sys
import pygame
from dotenv import get_key


def is_good_device(joystick):
    return joystick.get_name() == get_key('.env', 'DEVICE_NAME') and joystick.get_numbuttons() == get_key('.env',
                                                                                                          'COUNT_BUTTONS')


def get_devices_name():
    names = []
    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        print("Aucun périphérique de jeu connecté.")
        sys.exit()
    for i in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        names.append(joystick.get_name())
    return names


def init_device():
    joystick = pygame.joystick.Joystick(pygame.joystick.get_count() - 1)
    joystick.init()
    return joystick
