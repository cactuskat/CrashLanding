from settings import *
from player import Player
import math
from os import listdir
from math import sin
from utils import load_image,load_sprite,load_asset

BLOCK_SIZE = 96
CHARA_WIDTH,CHARA_HEIGHT = 64,64

class Object(pygame.sprite.Sprite):
	def __init__(self, pos, groups):
		super().__init__(groups)
		self.window = pygame.display.get_surface()
		self.image = pygame.Surface((BLOCK_SIZE,BLOCK_SIZE))
		self.image.fill((255,255,255))
		self.rect = self.image.get_rect(topleft = pos)
		self.old_rect = self.rect.copy()

	def draw(self,offset_x):
		self.window.blit(self.image, (self.rect.x - offset_x, self.rect.y))

	#still image
	def get_image(self,width,height,*path,scale=2):
		sprite_sheet = load_sprite(*path)
		#sprite_sheet = pygame.image.load(path).convert_alpha()
		#sprite = pygame.transform.scale_by(sprite_sheet.subsurface(0,0,width, height),scale)
		sprite = pygame.transform.scale(sprite_sheet.subsurface(0,0,width,height),(width*scale,height*scale))
		return sprite
	
	#animated
	def get_frames(self,width,height,*path,scale=2):
		sprite_sheet = load_sprite(*path)
		#sprite_sheet = pygame.image.load(path).convert_alpha()
		#frames = [pygame.transform.scale_by(sprite_sheet.subsurface(i * width, 0,width, height),2) 
		#	  for i in range(sprite_sheet.get_width() // width)]
		frames = [
			pygame.transform.scale(sprite_sheet.subsurface(i * width,0,width,height),(width*scale,height*scale)) for i in range(sprite_sheet.get_width() // width)
		]
		return frames

class Block(Object):
	def __init__(self,pos,groups,current_lvl):
		super().__init__(pos,groups)
		self.current_lvl = current_lvl
		self.image = pygame.Surface((BLOCK_SIZE,BLOCK_SIZE))
		block = self.get_block()
		self.image.blit(block,(0,0))
		self.rect = self.image.get_rect(topleft = pos)
		self.old_rect = self.rect.copy()

	def get_block(self):
		block_sprite_sheet = load_sprite("terrain","terrain.png")
		#block_sprite_sheet = pygame.image.load("../images/terrain/terrain.png").convert_alpha()
		surface = pygame.Surface((BLOCK_SIZE,BLOCK_SIZE), pygame.SRCALPHA, 32)
		#grass block starts 96 pixels from the left
		rect = pygame.Rect(96, self.current_lvl * 64, BLOCK_SIZE,BLOCK_SIZE)
		surface.blit(block_sprite_sheet,(0,0), rect)
		return pygame.transform.scale2x(surface)

class Pipe(Object):
	def __init__(self,pos,groups,current_lvl):
		super().__init__(pos,groups)
		self.image = self.get_img(current_lvl)
		self.rect = self.image.get_rect(topleft = pos)
		self.old_rect = self.rect.copy()

	def get_img(self,current_lvl):
		width,height = 96,10
		sprite_sheet = load_sprite("terrain","terrain.png")
		#sprite_sheet = pygame.image.load("../images/terrain/terrain.png").convert_alpha()
		surface = pygame.Surface((width,height), pygame.SRCALPHA, 32)
		rect = pygame.Rect(272,current_lvl * 16,width,height)
		surface.blit(sprite_sheet,(0,0),rect)
		return pygame.transform.scale2x(surface)


class Fruit(Object):
	def __init__(self,pos,groups,name):
		super().__init__(pos,groups)
		self.name = name
		self.frames = self.get_images()
		self.frame_index = 0
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(topleft=pos)
		self.rect.width *= 0.75
		self.rect.height *= 0.75
		self.eaten = False
		self.old_rect = self.rect.copy()
		self.flicker_mode = False
        
	def get_images(self):
		sprite_sheet = load_sprite("fruit",f"{self.name}.png")
		#sprite_sheet = pygame.image.load(join("..","images","fruit",f"{self.name}.png")).convert_alpha()
		sprites = []
		for i in range(sprite_sheet.get_width() // 32):
			surface = pygame.Surface((32,32), pygame.SRCALPHA, 32)
			rect = pygame.Rect(i * 32, 0, 32, 32)
			surface.blit(sprite_sheet, (-5,-5), rect)
			sprites.append(pygame.transform.scale2x(surface))
		return sprites

	def animate(self,dt):
		self.frame_index += ANIMATION_SPEED * dt
		self.image = self.frames[int(self.frame_index % len(self.frames))]
		self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
		self.rect.width *= 0.75
		self.rect.height *= 0.75

	def flicker(self):
		if sin(pygame.time.get_ticks() / 25) >= 0:
			white_mask = pygame.mask.from_surface(self.image)
			white_surface = white_mask.to_surface()
			white_surface.set_colorkey((0,0,0))
			self.image = white_surface

	def draw_ui(self,timer):
		if timer < 4000:
			self.flicker()
		self.window.blit(self.image, (self.rect.x, self.rect.y))

	def update(self,dt):
		self.old_rect = self.rect.copy()
		self.animate(dt)   

class Saw(Object):
	def __init__(self,groups,top_left,bottom_right,fast=False):
		super().__init__(top_left,groups)

		#animation
		#self.frames = self.get_images()
		self.frames= self.get_frames(38,38,"traps","saw.png")
		self.frame_index = 0
		self.image = self.frames[self.frame_index]

		#movement
		self.rect = self.image.get_rect(center = top_left)
		self.old_rect = self.rect.copy()
		self.speed = 150 if fast == False else 400
		self.point_index = 0
		top_left = vector(top_left)
		bottom_right = vector(bottom_right)
		self.path_points = [
			top_left,vector(bottom_right.x,top_left.y),
			bottom_right,vector(top_left.x,bottom_right.y)
		]
		self.target_point = self.path_points[(self.point_index + 1) % len(self.path_points)]
		self.direction = (self.target_point - self.path_points[self.point_index]).normalize()

	def animate(self,dt):
		self.frame_index += ANIMATION_SPEED * dt
		self.image = self.frames[int(self.frame_index % len(self.frames))]
		self.rect = self.image.get_rect(center = self.rect.center)

	def move(self,dt):
		# Move towards the target point
		self.rect.center += self.direction * self.speed * dt

		# Check if reached the target point
		if (self.target_point - vector(self.rect.center)).length() < 5:
			self.rect.center = self.target_point
			# Update to the next point in the path
			self.point_index = (self.point_index + 1) % len(self.path_points)
			self.target_point = self.path_points[(self.point_index + 1) % len(self.path_points)]
			self.direction = (self.target_point - self.path_points[self.point_index]).normalize()

	def update(self,dt):
		self.old_rect = self.rect.copy()
		self.move(dt)
		self.animate(dt)

class Heart(Object):
	def __init__(self,pos,group,full = True):
		super().__init__(pos,group)
		img = "heart_full.png" if full else "heart_empty.png"
		path = join("ui",img)
		self.image = self.get_image(16,14,"ui",img,scale=3)

	#def get_image(self,full):
	#	img = "heart_full.png" if full else "heart_empty.png"
	#	path = join("images","ui",img)
	#	image = pygame.image.load(path).convert_alpha()
	#	surface = pygame.Surface((16,14), pygame.SRCALPHA, 32)
	#	surface.blit(image,(0,0), pygame.Rect(0,0,16,14))
	#	return pygame.transform.scale_by(surface, 3)
	
class Friend(Object):
	def __init__(self,pos,groups,current_level,facing_right=True):
		super().__init__(pos,groups)
		self.friend_list = ["guy","tiki"]
		
		#animate
		self.frame_index = 0
		self.frames = self.get_images()
		self.facing_right =	facing_right
		self.name = self.friend_list[current_level]
		self.image = self.frames[self.name][self.frame_index]
		self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
	
	def get_images(self):
		width, height = 32, 32
		folder = ("friend",)  # path components relative to "images"
		all_sprites = {}

		# listdir expects a filesystem path, so we use load_asset to get the absolute path
		path = load_asset("images", *folder)

		for image_name in listdir(path):
			# Use load_image to load the sprite sheet
			sprite_sheet = load_image("friend", image_name).convert_alpha()

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
	'''
	def get_images(self):
		width,height = 32,32
		path = join("..","..","images","friend")
		all_sprites = {}
		for image in listdir(path):
			full_img_path = join(path,image)
			sprite_sheet = pygame.image.load(full_img_path).convert_alpha()
			sprites = [pygame.transform.scale2x(sprite_sheet.subsurface(i * width, 0,width, height)) 
			  for i in range(sprite_sheet.get_width() // width)]
			base_name = image.replace(".png","")
			all_sprites[base_name] = sprites
		return all_sprites
	'''
	def animate(self,dt):
		self.frame_index += ANIMATION_SPEED * dt
		self.image = self.frames[self.name][int(self.frame_index % len(self.frames[self.name]))]
		self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)										  
		self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))

	def update(self, dt):
		self.animate(dt)

class Spikes(Object):
	def __init__(self,pos,groups,flip=False):
		super().__init__(pos,groups)
		self.image = self.get_image(48,8,"traps","spikes.png")
		self.image = self.image if not flip else pygame.transform.flip(self.image, False, True)
		self.rect = self.image.get_rect(bottomleft = pos) if not flip else self.image.get_rect(topleft = pos)
		self.old_rect = self.rect.copy()

class Platform(Object):
	def __init__(self,pos,groups,end_pos):
		super().__init__(pos,groups)
		self.is_platform = True
		
		#animation
		self.frames = self.get_frames(32,10,"terrain","platform.png")
		self.frame_index = 0
		self.image = self.frames[self.frame_index]

		#movement
		self.rect = self.image.get_rect(topleft = pos)
		self.old_rect = self.rect.copy()
		self.speed = 150
		self.point_index = 0
		self.start_pos = vector(pos)
		self.end_pos = vector(end_pos)
		self.moving_to_end = True
		self.direction = (self.end_pos - self.start_pos).normalize()
	
	def animate(self,dt):
		self.frame_index += ANIMATION_SPEED * dt
		self.image = self.frames[int(self.frame_index % len(self.frames))]
		self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))

	def move(self,dt):
		move_vector = self.direction * self.speed * dt
		self.rect.x += move_vector.x
		self.rect.y += move_vector.y
		current_pos = vector(self.rect.topleft)
		target_pos = self.end_pos if self.moving_to_end else self.start_pos
		if (self.moving_to_end and current_pos.distance_to(self.end_pos) < self.speed * dt) or \
		(not self.moving_to_end and current_pos.distance_to(self.start_pos) < self.speed * dt):
			self.rect.topleft = target_pos
			self.moving_to_end = not self.moving_to_end
			self.direction = (self.end_pos if self.moving_to_end else self.start_pos) - current_pos
			self.direction = self.direction.normalize()

	def update(self,dt):
		self.old_rect = self.rect.copy()
		self.move(dt)
		self.animate(dt) 

class Oxygen(Object):
	def __init__(self,pos,group):
		super().__init__(pos,group)
		self.image = self.get_image(21,19,"ui","oxygen.png",scale=3)

	def flicker(self):
		if sin(pygame.time.get_ticks() / 25) >= 0:
			white_mask = pygame.mask.from_surface(self.image)
			white_surface = white_mask.to_surface()
			white_surface.set_colorkey((0,0,0))
			self.image = white_surface
	
	def draw(self):
		self.flicker()
		self.window.blit(self.image, (self.rect.x, self.rect.y))

class Enemy(Object):
	def __init__(self,pos,groups,end_pos):
		super().__init__(pos,groups)
		self.is_enemy = True
		
		self.frames = self.get_images()
		self.frame_index = 0
		self.image = self.frames[self.frame_index]

		#movement
		self.rect = self.image.get_rect(topleft = pos)
		self.old_rect = self.rect.copy()
		self.speed = 150
		self.point_index = 0
		self.start_pos = vector(pos)
		self.end_pos = vector(end_pos)
		self.moving_to_end = True
		self.direction = (self.end_pos - self.start_pos).normalize()

	def get_images(self):
		width,height = 32,32
		sprite_sheet = load_sprite("traps","frog.png")
		#sprite_sheet = pygame.image.load("../images/traps/frog.png").convert_alpha()
		sprites = []
		for i in range(sprite_sheet.get_width() // width):
			surface = pygame.Surface((width,height), pygame.SRCALPHA, 32)
			rect = pygame.Rect(i * width, 0, width, height)
			surface.blit(sprite_sheet, (0,0), rect)
			sprites.append(pygame.transform.scale2x(surface))
		return sprites

	
	def animate(self,dt):
		self.frame_index += ANIMATION_SPEED * dt
		self.image = self.frames[int(self.frame_index % len(self.frames))]
		self.image = pygame.transform.flip(self.image,True,False) if self.direction.x < 0 else self.image
		self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))

	def move(self,dt):
		move_vector = self.direction * self.speed * dt
		self.rect.x += move_vector.x
		current_pos = vector(self.rect.topleft)
		target_pos = self.end_pos if self.moving_to_end else self.start_pos
		if (self.moving_to_end and current_pos.distance_to(self.end_pos) < self.speed * dt) or \
		(not self.moving_to_end and current_pos.distance_to(self.start_pos) < self.speed * dt):
			self.rect.topleft = target_pos
			self.moving_to_end = not self.moving_to_end
			self.direction = (self.end_pos if self.moving_to_end else self.start_pos) - current_pos
			self.direction = self.direction.normalize()

	def update(self,dt):
		self.old_rect = self.rect.copy()
		self.move(dt)
		self.animate(dt) 