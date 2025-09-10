from settings import *

class Cutscenes:
    def __init__(self,ui):
        self.window = pygame.display.get_surface()

        #fonts
        self.ui = ui

        #text
        self.texts = []
        self.text_index = 0
        self.talk_count = 0
        self.credits = ["Animalese.mav : Josh Simmons(Acedio)[GitHub]",
                   "Background Music : Jonathan So",
                   "Sound effects : JDWasabi & Pixel Frog [itch.io]",
                   "Graphics : Pixel Frog [itch.io]"]
        self.hints = ["Hint: You don't need to get all the fruit",
                      "Hint: Ants don't have lungs",
                      "Hint: Bats are the only flying mammals",
                      "Hint: Pineapples reverse control"]

        #audio
        self.talk = pygame.mixer.Sound("../audio/talk.wav")
        self.talk_death = pygame.mixer.Sound("../audio/talk_death.wav")

    #print credits to screen
    def print_credits(self):
        for i,credit in enumerate(self.credits):
            self.ui.print(credit,WINDOW_WIDTH // 2,(WINDOW_HEIGHT // 2) + 150 + (i * 30),False)

    #play intro and move forward with space
    def play_intro(self):
        self.texts = [ "Adventure Log 114...", 
                      "We are about to crash land on a strange planet",
                      "First priority is finding my crewmates", 
                      "I'll have limited oxygen...",
                      "I can use the arrows key to move around",
                      "But what's with the fruit? ..."]

        #iterate through intro text
        if self.text_index < len(self.texts):
            self.window.fill((0,0,0))
            self.ui.print(self.texts[self.text_index],WINDOW_WIDTH// 2,WINDOW_HEIGHT//2)
            if self.text_index == 0:
                self.ui.print("Hit space to continue...",WINDOW_WIDTH//2,WINDOW_HEIGHT//2 + 100,False)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.talk.stop()
                self.text_index += 1
                #only play after "adventure log"
                if  not (self.text_index >= len(self.texts)):
                    self.talk.play()
                pygame.time.delay(200)

        return self.text_index >= len(self.texts)
            
    #play win cutscene
    def play_win_screen(self,game_duration):
        self.window.fill((0,0,0))
        #only play talk clip once
        if self.talk_count == 0:
            self.talk.play()
            self.talk_count += 1
        self.ui.print("Time to Go Home :)",WINDOW_WIDTH// 2,WINDOW_HEIGHT//2)
        self.ui.print(f"OxygenLevel : {game_duration // 1000}",(WINDOW_WIDTH// 2) + 30,(WINDOW_HEIGHT//2) + 50)
        self.print_credits()

    #play game over cutscene
    def play_game_over(self):
        self.window.fill((0,0,0))
        #only play talk clip once
        if self.talk_count == 0:
            self.talk_death.play()
            self.talk_count += 1
        self.ui.print("I'm sorry Mom...",WINDOW_WIDTH// 2, WINDOW_HEIGHT//2)
        self.print_credits() 

    def play_replay_screen(self):
        self.window.fill((0,0,0))
        self.ui.print("suit heal activating..",WINDOW_WIDTH// 2, WINDOW_HEIGHT//2)
        self.ui.print("(press R to restart)",WINDOW_WIDTH// 2, (WINDOW_HEIGHT//2) + 50,False)
       

