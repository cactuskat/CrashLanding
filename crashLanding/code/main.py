from settings import * 
from level import Level
from cutscenes import *
from timer import Timer
from ui import *

class Game:
	def __init__(self):
		pygame.init()
		self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		pygame.display.set_caption('Crash Landing')
		self.clock = pygame.time.Clock()

		#ui
		self.ui = UI()

		#oxygen levels / how quickly the game was completed
		self.game_timer = Timer(GAMETIME)
		self.game_duration = 0

		#level setup
		self.level_count = 0
		self.game_over = False  
		self.won_game = False
		self.can_replay = True
		self.chara_dead = False
		self.bg_music = None
		self.setup_bg_music()
		self.next_level = False

		#cutscene
		self.cutscenes = Cutscenes(self.ui)
		self.intro_played = False


		self.current_level = Level(self.level_count,self.ui)
		
	def check_game_over(self):
		if self.game_timer.time_left() < (GAMETIME // 5):
			self.can_replay = False
		if (self.current_level.player.health <= 0):
			self.chara_dead = True
		if (self.chara_dead and not self.can_replay) or (self.game_timer.time_left() <= 0):
			self.game_over = True
			self.game_timer.deactivate()
			self.cutscenes.play_game_over()

	def check_won(self):
		if self.current_level.won_level:
			self.current_level.won_level = False
			#Check if final level is reached
			if self.level_count == MAX_LEVEL_COUNT:
				self.won_game = True
				self.game_duration = self.game_timer.time_left()
				self.cutscenes.play_win_screen(self.game_duration)
				#self.game_timer.deactivate()
			else: #otherwise, play next level
				self.level_count += 1
				self.bg_music.stop()
				self.setup_bg_music()
				self.current_level = Level(self.level_count,self.ui)

	def setup_bg_music(self):
		bg_music_list = ["Crimson_Drive.wav","Zero_Respect.wav","Fallen_in_Battle.wav"]  
		self.bg_music = pygame.mixer.Sound(join("..","audio",bg_music_list[self.level_count]))
		self.bg_music.set_volume(0.5)
		self.bg_music.play(-1)

	def run(self):
		while True:
			dt = self.clock.tick() / 1000
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()

			keys = pygame.key.get_pressed()
			if keys[pygame.K_r] and self.chara_dead and self.can_replay:
				self.chara_dead = False
				self.current_level = Level(self.level_count,self.ui) 

			if self.level_count == 0 and not self.intro_played:
				self.intro_played = self.cutscenes.play_intro()
				if self.intro_played:
					self.game_timer.activate()
			else:	
				if self.game_over:
					self.cutscenes.play_game_over()
				elif self.won_game:
					self.cutscenes.play_win_screen(self.game_duration)
				elif self.chara_dead and self.can_replay:
					self.cutscenes.play_replay_screen()
				else: 
					self.game_timer.update()
					self.current_level.run(dt,self.game_timer.time_left())
					self.check_game_over()
					self.check_won()
			
			pygame.display.update()

if __name__ == '__main__':
	game = Game()
	game.run()