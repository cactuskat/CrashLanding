import pygame
pygame.mixer.init()
try:
    sound = pygame.mixer.Sound("Crimson_Drive.mp3")
    sound.play()
    print("Sound played successfully!")
except pygame.error as e:
    print("Pygame error:", e)
except FileNotFoundError:
    print("File not found!")
