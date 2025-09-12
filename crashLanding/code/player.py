from settings import * 
from timer import Timer
from math import sin
from utils import load_audio,load_sprite


class Player(pygame.sprite.Sprite):
	def __init__(self, pos, groups,col_group):
		super().__init__(groups)

		#sprites
		self.actions = ["idle","run","jump","hit","fall","double_jump"]
		self.frames = self.load_frames()

		#animation
		self.state = "idle"
		self.frame_index = 0
		self.facing_right = True
		self.image = self.frames[self.state][self.frame_index]
		

		#status
		self.reverse_controls = False
		self.shield = False
		self.fruit_timers = {
			"apple" : Timer (10000),
			"banana" : Timer(10000),
			"pineapple" : Timer(10000),
			"melon" : Timer(10000)
		}

		#health
		self.health = 5 if DEBUG == False else DEBUGHEALTH
		self.max_health = 5

		#collision
		self.rect = self.image.get_rect(topleft = pos)
		self.old_rect = self.rect.copy()
		self.col_group = col_group
		self.on_surface = {"floor": False}
		self.timers = {"hit" :Timer (1525)}

		# movement 
		self.direction = vector()
		self.speed = 200
		self.gravity = 1400
		self.can_double_jump = True
		self.jump_height = 550
		self.jump_count = 0

		#audio
		self.jump_sound = load_audio("jump.wav")
		self.fruit_sound = load_audio("fruit.wav")
	
	def load_frames(self):
		""" 
		Load and spilt all player sprites by action 
		
		Returns:
			dict containing all frames keyed by state
		"""
		all_sprites = {}
		#load sprites for every action avaiable
		for state in self.actions:
			width,height = 32, 32 #frame size
			sprite_sheet = load_sprite("player", f"{state}.png")
			#spilt sheet into frames
			frames = [
				pygame.transform.scale2x(
					sprite_sheet.subsurface(i * width, 0, width, height)
				)
				for i in range(sprite_sheet.get_width() // width)
			]
			all_sprites[state] = frames
		return all_sprites
	
	def animate(self,dt):
		""" 
		Change sprite frame according to the directional movement and action 
		
		Parameters:
			dt (float) : delta time since last frame
		"""
		#determine state
		if self.timers["hit"].active:
			self.state = "hit"
		elif self.direction.y < 0:
			self.state = "jump" if self.jump_count == 1 else "double_jump"
		elif self.direction.y > self.gravity * 2:
			self.state = "fall"
		else:
			if self.direction.x != 0:
				self.state = "run"
			else:
				self.state = "idle"

		#irrate through frames of state
		frame_count = len(self.frames[self.state])
		self.frame_index = (self.frame_index + ANIMATION_SPEED * dt) % frame_count
		self.image = self.frames[self.state][int(self.frame_index)]

		#default is facing right, flip for facing right
		if not self.facing_right:
			self.image = pygame.transform.flip(self.image, True, False)

	def input(self):
		"""
		Update player direction depending on keyboard input
		"""
		if not self.timers["hit"].active:
			keys = pygame.key.get_pressed()
			direction_x = 0

			#---horizontal movement---
			if keys[pygame.K_RIGHT]:
				direction_x += 1
			if keys[pygame.K_LEFT]:
				direction_x -= 1

			if self.reverse_controls:
				direction_x *= -1

			#if not moving, face right by default	
			if direction_x != 0:
				self.facing_right = direction_x > 0

			self.direction.x = direction_x

			#---vertical movement---
			jump_key = pygame.K_UP if not self.reverse_controls else pygame.K_DOWN

			if keys[jump_key] and not self.can_double_jump and self.jump_count < 2:
				self.jump()
			if not keys[jump_key]:
				self.can_double_jump = False

	def jump(self):
		""" Jumps player, allows double jump if possible """
		self.can_double_jump = True
		self.jump_count = min(self.jump_count + 1,2)
		self.direction.y = - self.jump_height
		self.jump_sound.play()

	def move(self, dt):
		""" 
		Moves player and checks horizontal and vertical collision 
		
		Parameters:
			dt (float) : delta time since last frame
		"""

		#---horizontal movement ---
		self.rect.x += self.direction.x * self.speed * dt
		self.rect.x = max(0,min(self.rect.x, GAME_WIDTH - self.rect.width))
		self.collision("horizontal")

		#---vertical movement ---
		self.direction.y += self.gravity * dt
		self.rect.y += self.direction.y * dt
		self.collision("vertical")

	def platform_move(self,dt):
		"""
		Move player with platform if on platform

		Parameters:
			dt (float) : delta time since last frame
		"""
		floor_rect = pygame.Rect(self.rect.bottomleft,(self.rect.width,1))
		collide_rects = [sprite.rect for sprite in self.col_group]

		#check collisions
		self.on_surface["floor"] = (floor_rect.collidelist(collide_rects) >= 0)

		#platform
		for sprite in self.col_group.sprites():
			if (getattr(sprite,"is_platform",False) 
	   				and sprite.rect.colliderect(floor_rect)):
				self.rect.topleft += sprite.direction * sprite.speed * dt

	#collision handling
	def collision(self,axis):
		"""
		Collision handling for 4 directions:left,right,up,down

		Parameters:
		axis (str): collision check direction('horizontal' or 'vertical')
		"""
		for sprite in self.col_group:
			if sprite.rect.colliderect(self.rect):
				#---horizontal collision---
				if axis == "horizontal":
					#left
					if (self.rect.left <= sprite.rect.right 
		 					and self.old_rect.left >= sprite.old_rect.right):
						self.rect.left = sprite.rect.right
						self.on_surface["left"] = True
					#right
					if (self.rect.right >= sprite.rect.left 
		 					and self.old_rect.right <= sprite.old_rect.left):
						self.rect.right = sprite.rect.left
						self.on_surface["right"] = True

				#---vertical collision---
				else:
					#top
					if (self.rect.top <= sprite.rect.bottom 
		 					and self.old_rect.top >= sprite.old_rect.bottom):
						self.rect.top = sprite.rect.bottom
						if hasattr(sprite,"is_platform"):
							self.rect.top += 6 #platform offset
					#bottom
					if (self.rect.bottom >= sprite.rect.top 
		 					and self.old_rect.bottom <= sprite.old_rect.top):
						self.rect.bottom = sprite.rect.top

					self.direction.y = 0
					self.jump_count = 0
	
	def update_timers(self):
		""" Update all timers """
		for timer in self.timers.values():
			timer.update()
		for timer in self.fruit_timers.values():
			timer.update()

	def get_damage(self,magnitude=1):
		"""
		Take damage, start hit timer, and reduce health

		Parameters:
		magnitude (int): how much heaath to lose
		"""
		if not self.timers["hit"].active and not self.shield:
			self.health -= magnitude
			if not self.direction.y < 0:
				og_jump_height = self.jump_height
				self.jump_height = 400
				self.jump()
				self.jump_height = og_jump_height
			self.timers["hit"].activate()

	def flicker(self):
		""" Flicker player image with white pulsing mask """
		if self.timers["hit"].active or self.shield:
			if sin(pygame.time.get_ticks() / 50) >= 0:
				white_mask = pygame.mask.from_surface(self.image)
				white_surface = white_mask.to_surface()
				white_surface.set_colorkey((0,0,0))
				self.image = white_surface

	#starting fruit/powerup effect
	def powerup(self,fruit):
		""" 
		Start powerup of frutis effects, turn on timer if needed
		 
		Parameters:
		fruit (str): fruit effect chosen
		"""
		self.fruit_sound.play()
		if fruit in self.fruit_timers.keys():
			if not self.fruit_timers[fruit].active:
				self.fruit_timers[fruit].activate()
		self.fruit_effect(fruit)

	def fruit_effect(self,fruit=None):
		""" 
		Apple effects of fruit to player based on chosen fruit

		Parameters:
		fruit (str): fruit effect chosen
		"""
		#cherry -> increase health by 1
		if fruit == "cherry":
			print(f"max:{self.max_health} health: {self.health}") if DEBUG else None
			if self.health < self.max_health:
				self.health += 1
			print(f"max:{self.max_health} health: {self.health}") if DEBUG else None
			return
		#kiwi -> decrease max health by 1
		elif fruit == "kiwi":
			if self.max_health > 1:
					self.max_health -= 1
					self.health -= 1 
			return
		#orange -> turns off all fruit effects active
		elif fruit == "orange":
			for timer in self.fruit_timers.values():
					timer.deactivate()
			return
		
		#apple -> jump_height
		self.jump_height = 700 if self.fruit_timers["apple"].active else 550
		#banana -> speed
		self.speed = 500 if self.fruit_timers["banana"].active else 200
		#pineapple -> reverse controls
		self.reverse_controls = self.fruit_timers["pineapple"].active
		#melon -> shield
		self.shield = self.fruit_timers["melon"].active

	def draw(self,window,offset_x):
		""" Draw player image on screen """
		window.blit(self.image, (self.rect.x - offset_x, self.rect.y))

	#update all player functions
	def update(self, dt):
		self.old_rect = self.rect.copy()
		self.fruit_effect()
		self.update_timers()
		self.input()
		self.move(dt)
		self.platform_move(dt)
		self.animate(dt)
		self.flicker()
