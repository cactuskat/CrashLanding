from settings import * 
from timer import Timer
from os import listdir
from math import sin
from utils import load_audio,load_image,load_sprite,load_asset

class Player(pygame.sprite.Sprite):
	def __init__(self, pos, groups,col_group):
		super().__init__(groups)

		#image
		self.frames = self.get_images()
		self.frame_index = 0
		self.facing_right = True
		self.state = "idle"
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
		self.can_jump = True
		self.jump_height = 550
		self.jump_count = 0

		#audio
		self.jump_sound = load_audio("jump.wav")
		self.fruit_sound = load_audio("fruit.wav")
		

	def get_images(self):
		width, height = 32, 32
		folder = ("player",)  # path components relative to "images"
		all_sprites = {}

		# listdir expects a filesystem path, so we use load_asset to get the absolute path
		path = load_asset("images", *folder)

		for image_name in listdir(path):
			# Use load_image to load the sprite sheet
			sprite_sheet = load_image("player", image_name).convert_alpha()

			# Split the sheet into frames
			sprites = [
				pygame.transform.scale2x(
					sprite_sheet.subsurface(i * width, 0, width, height)
				)
				for i in range(sprite_sheet.get_width() // width)
			]

			base_name = image_name.replace(".png", "")
			all_sprites[base_name] = sprites
		return all_sprites
	
	#load in all images of the player
	def load_player_sprites(self):
		width,height = 32,32
		path = join("..","..","images","player")
		all_sprites = {}
		for image in listdir(path):
			full_img_path = join(path,image)
			sprite_sheet = pygame.image.load(full_img_path).convert_alpha()
			sprites = [pygame.transform.scale2x(sprite_sheet.subsurface(i * width, 0,width, height)) 
			  for i in range(sprite_sheet.get_width() // width)]
			base_name = image.replace(".png","")
			all_sprites[base_name] = sprites
		return all_sprites
	
	#change the sprite frame according to the directional movement & action
	def animate(self,dt):
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

		self.frame_index += ANIMATION_SPEED * dt
		self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
		self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)										  
		self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))

	#change player movement depending on keyboard input
	def input(self):
		keys = pygame.key.get_pressed()
		input_vector = vector(0,0)
		if keys[pygame.K_RIGHT]:
			if not self.reverse_controls:
				input_vector.x += 1
				self.facing_right = True
			else:
				input_vector.x -= 1
				self.facing_right = False
		if keys[pygame.K_LEFT]:
			if not self.reverse_controls:
				input_vector.x -= 1
				self.facing_right = False
			else:
				input_vector.x += 1
				self.facing_right = True

		self.direction.x = input_vector.normalize().x if input_vector else input_vector.x
		
		if not self.reverse_controls:
			if keys[pygame.K_UP] and not self.can_jump and self.jump_count < 2:
				self.jump()
			if not keys[pygame.K_UP]:
				self.can_jump = False
		else:
			if keys[pygame.K_DOWN] and not self.can_jump and self.jump_count < 2:
					self.jump()
			if not keys[pygame.K_DOWN]:
				self.can_jump = False
	
	#jump player upwards
	def jump(self):
		self.can_jump = True
		self.jump_count += 1
		self.direction.y = - self.jump_height
		self.jump_sound.play()

	#move player
	def move(self, dt):
		#horizontal
		self.rect.x += self.direction.x * self.speed * dt
		self.rect.x = max(0,min(self.rect.x, GAME_WIDTH - self.rect.width))
		self.collision("horizontal")

		#vertical
		self.direction.y += self.gravity / 2 * dt
		self.rect.y += self.direction.y * dt
		self.direction.y += self.gravity / 2 * dt
		self.collision("vertical")

	#if on platform: move the player with the platform
	def platform_move(self,dt):
		floor_rect = pygame.Rect(self.rect.bottomleft,(self.rect.width,1))
		collide_rects = [sprite.rect for sprite in self.col_group]

		#check collisions
		self.on_surface["floor"] = True if floor_rect.collidelist(collide_rects) >= 0 else False

		#platform
		for sprite in [sprite for sprite in self.col_group.sprites() if hasattr(sprite,"is_platform")]:
			if sprite.rect.colliderect(floor_rect):
				self.rect.topleft += sprite.direction * sprite.speed * dt

	#collision handling
	def collision(self,axis):
		for sprite in self.col_group:
			if sprite.rect.colliderect(self.rect):
				if axis == "horizontal":
					#left
					if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
						self.rect.left = sprite.rect.right
						self.on_surface["left"] = True
					#right
					if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
						self.rect.right = sprite.rect.left
						self.on_surface["right"] = True
				else: #vertical
					#top
					if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
						self.rect.top = sprite.rect.bottom
						if hasattr(sprite,"is_platform"):
							self.rect.top += 6
					#bottom
					if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
						self.rect.bottom = sprite.rect.top
					self.direction.y = 0
					self.jump_count = 0
	
	#update timers every frame
	def update_timers(self):
		for timer in self.timers.values():
			timer.update()
		for timer in self.fruit_timers.values():
			timer.update()

	#if player gets hurt: start timer & reduce health
	def get_damage(self):
		if not self.timers["hit"].active and not self.shield:
			#print("it was not active in get_damage()")
			self.health -= 1
			if not self.direction.y < 0:
				og_jump_height = self.jump_height
				self.jump_height = 400
				self.jump()
				self.jump_height = og_jump_height
			self.timers["hit"].activate()

	#flicker player image with white mask
	def flicker(self):
		if self.timers["hit"].active or self.shield:
			if sin(pygame.time.get_ticks() / 50) >= 0:
				white_mask = pygame.mask.from_surface(self.image)
				white_surface = white_mask.to_surface()
				white_surface.set_colorkey((0,0,0))
				self.image = white_surface

	#if fruit ate: start fruit timer
	def powerup(self,fruit):
		self.fruit_sound.play()
		if fruit in self.fruit_timers.keys():
			if not self.fruit_timers[fruit].active:
				self.fruit_timers[fruit].activate()
		self.fruit_effect(fruit)

	#apply effects of the fruit to the player statuses
	def fruit_effect(self,fruit=None):
		if fruit == "cherry":
			print(f"max:{self.max_health} health: {self.health}") if DEBUG else None
			if self.health < self.max_health:
				self.health += 1
			print(f"max:{self.max_health} health: {self.health}") if DEBUG else None
			return
		elif fruit == "kiwi":
			if self.max_health > 1:
					self.max_health -= 1
					self.health -= 1 
			return
		elif fruit == "orange":
			for timer in self.fruit_timers.values():
					timer.deactivate()
			return
		
		#apple -> jump_height
		self.jump_height = 700 if self.fruit_timers["apple"].active else 550
		#banana -> speed
		self.speed = 500 if self.fruit_timers["banana"].active else 200
		#pineapple -> reverse controls
		self.reverse_controls = True if self.fruit_timers["pineapple"].active else False
		#melon -> shield
		self.shield = True if self.fruit_timers["melon"].active else False

	#draw player image on screen
	def draw(self,window,offset_x):
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
