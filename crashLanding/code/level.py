from settings import *
from player import Player
from objects import *


class Level:
	def __init__(self, current_level,ui):
		self.window = pygame.display.get_surface()
		self.current_level = current_level
		self.ui = ui

		#sprite groups
		self.all_sprites = pygame.sprite.Group() #all sprites to draw at once
		self.player_group = pygame.sprite.GroupSingle() #group for the player
		self.collision_group = pygame.sprite.Group() #blocks cannot go through
		self.damage_sprites = pygame.sprite.Group() #blocks that cause damage
		self.untouchable = pygame.sprite.Group() #blocks that player cannot interact with
		self.fruits = pygame.sprite.Group() #powerups
		self.endpoint = pygame.sprite.GroupSingle() #endpoint for winning the level

		#variables
		self.won_level = False
		self.offset_x = 0
		
		self.setup()

	#display ui
	def display_hearts(self):
		for heart in range(self.player.max_health):
			full = True  if heart < self.player.health else False
			Heart(((heart * 50) + 20, 50),self.untouchable,full).draw(0)

	def display_fruit_status(self):
		for count,(name,timer) in enumerate(self.player.fruit_timers.items()):
			if timer.active:
				pos = ((count * 40) + 10, 100)
				Fruit(pos,self.untouchable,name).draw_ui(timer.time_left())

	def display_oxygen(self,game_duration):
		self.ui.print(f"Oxygen Levels: {game_duration // 1000}", 150,25)
		if game_duration < 10000:
			Oxygen((300,25),self.untouchable).draw()

	#collision
	def fruit_collision(self,dt):
		collided_fruits = pygame.sprite.spritecollide(self.player, self.fruits, True)
		if collided_fruits:
			for fruit in collided_fruits:
				print(f"hit with {collided_fruits[0].name}") if DEBUG else None
				self.player.powerup(fruit.name)		

	def hit_collision(self):
		for sprite in self.damage_sprites:
			if pygame.sprite.spritecollide(self.player,self.damage_sprites,False):
				self.player.get_damage()

	def win_collision(self):
		if pygame.sprite.spritecollide(self.player,self.endpoint,False):
			self.won_level = True
			return

	#map maker tools
	def mm_block(self,x,y):
		x,y = max(x,0), max(y,1)
		y = min(y, GAME_WIDTH // BLOCK_SIZE - 1)
		return (BLOCK_SIZE * x,WINDOW_HEIGHT - (y * BLOCK_SIZE))
	
	def mm_hfblock_x(self,x,y):
		x = max(x,0)
		return ((BLOCK_SIZE * x) - (BLOCK_SIZE // 2 + 20),WINDOW_HEIGHT - (y * BLOCK_SIZE))
	
	def mm_hfblock_y(self,x,y):
		y = max(y,1)
		return (BLOCK_SIZE * x,WINDOW_HEIGHT - (y * BLOCK_SIZE) + (BLOCK_SIZE//2))

	def mm_block_chara(self,x,y):
		return (BLOCK_SIZE * x,WINDOW_HEIGHT-(BLOCK_SIZE* y)-CHARA_HEIGHT)

	#level setup
	def setup(self):
		#background
		self.bg_img,self.bg_tiles = self.get_bg_tiles()

		#ground floor blocks
		self.floor = [Block((i * BLOCK_SIZE,WINDOW_HEIGHT - BLOCK_SIZE),(self.all_sprites,self.collision_group),self.current_level) 
				for i in range(GAME_WIDTH // BLOCK_SIZE)]

		#level terrain
		self.blocks = []
		if self.current_level == 0:
			#saw go under blocks
			saw_block1 = pygame.Rect((self.mm_block(5,4)), (BLOCK_SIZE * 2,BLOCK_SIZE))
			Saw((self.all_sprites,self.damage_sprites),saw_block1.topleft,saw_block1.bottomright)

			#blocks
			self.blocks.append(Block((self.mm_block(8,2)), (self.all_sprites,self.collision_group),self.current_level))
			self.blocks.append(Block((self.mm_block(5,4)), (self.all_sprites,self.collision_group),self.current_level))
			self.blocks.append(Block((self.mm_block(6,4)), (self.all_sprites,self.collision_group),self.current_level))
			
			#pipes
			Pipe((self.mm_block(1,5)),(self.all_sprites,self.collision_group),self.current_level)
			Pipe((self.mm_block(13,6)),(self.all_sprites,self.collision_group),self.current_level)
			Pipe((self.mm_block(14,6)),(self.all_sprites,self.collision_group),self.current_level)
			Pipe((self.mm_block(19,6)),(self.all_sprites,self.collision_group),self.current_level)
			
			
			#fruit
			Fruit((150,500),(self.all_sprites,self.fruits),"cherry")
			Fruit((500,500),(self.all_sprites,self.fruits),"banana")
			Fruit((self.mm_hfblock_x(10,2)),(self.all_sprites,self.fruits),"pineapple")
			Fruit((self.mm_hfblock_x(6,5)),(self.all_sprites,self.fruits),"apple")
			Fruit((self.mm_hfblock_x(18,6)),(self.all_sprites,self.fruits),"apple")
			Fruit((self.mm_hfblock_x(15,3)),(self.all_sprites,self.fruits),"apple")
			Fruit((self.mm_hfblock_x(2,6)),(self.all_sprites,self.fruits),"kiwi")
			Fruit((self.mm_hfblock_x(13,4)),(self.all_sprites,self.fruits),"orange")
			Fruit((self.mm_hfblock_x(19,2)),(self.all_sprites,self.fruits),"melon")

			#spikes
			for i in range(5):
				Spikes((self.mm_block(10+i,1)),(self.all_sprites,self.damage_sprites))

			#platform
			Platform(self.mm_block(8,5),(self.all_sprites,self.collision_group), self.mm_block(10,5))
			Platform(self.mm_hfblock_y(12,3),(self.all_sprites,self.collision_group), self.mm_block(12,5))

			#enemy
			self.ene =Enemy(self.mm_block_chara(16,1),(self.all_sprites,self.damage_sprites),self.mm_block_chara(19,1))

			#endpoint
			#self.friend = Friend((BLOCK_SIZE * 1,WINDOW_HEIGHT-(BLOCK_SIZE* 5)-64),(self.all_sprites,self.endpoint),self.current_level,facing_right=True)
			self.friend = Friend(self.mm_block_chara(19,6),(self.all_sprites,self.endpoint),self.current_level,facing_right=False)
			#self.friend = Friend(self.mm_block_chara(1,2),(self.all_sprites,self.endpoint),self.current_level,facing_right=False)


		elif self.current_level == 1:
			#saw go under blocks
			saw_block1 = pygame.Rect((self.mm_block(9,7)), (BLOCK_SIZE * 7,BLOCK_SIZE))
			Saw((self.all_sprites,self.damage_sprites),saw_block1.topleft,saw_block1.bottomright,True)

			#self.blocks.append(Block(200,100, self.current_level))
			#self.blocks.append(Block((self.mm_block(3,2)), (self.all_sprites,self.collision_group),self.current_level))
			Platform(self.mm_block(4, 6), (self.all_sprites, self.collision_group), self.mm_hfblock_x(8, 6))

			# Blocks
			self.blocks.append(Block((self.mm_block(2, 4)), (self.all_sprites, self.collision_group), self.current_level))
			self.blocks.append(Block((self.mm_block(5, 3)), (self.all_sprites, self.collision_group), self.current_level))
			for i in range(7):
				self.blocks.append(Block((self.mm_block(9+i, 7)), (self.all_sprites, self.collision_group), self.current_level))
			self.blocks.append(Block((self.mm_block(9, 4)), (self.all_sprites, self.collision_group), self.current_level))
			self.blocks.append(Block((self.mm_block(11, 4)), (self.all_sprites, self.collision_group), self.current_level))
			self.blocks.append(Block((self.mm_block(13, 4)), (self.all_sprites, self.collision_group), self.current_level))
			self.blocks.append(Block((self.mm_block(15, 4)), (self.all_sprites, self.collision_group), self.current_level))

			# Spikes for added danger
			Spikes((self.mm_block(6, 1)), (self.all_sprites, self.damage_sprites))
			Spikes((self.mm_block(7, 1)), (self.all_sprites, self.damage_sprites))
			for i in range(8):
				Spikes((self.mm_block(10+i,1)),(self.all_sprites,self.damage_sprites))


			# Fruit collectibles
			Fruit((self.mm_hfblock_x(3,2)), (self.all_sprites, self.fruits), "pineapple")
			Fruit((self.mm_hfblock_y(3,8)), (self.all_sprites, self.fruits), "cherry")
			Fruit((self.mm_hfblock_x(11, 3)), (self.all_sprites, self.fruits), "kiwi")
			Fruit((self.mm_hfblock_x(13, 3)), (self.all_sprites, self.fruits), "apple")
			Fruit((self.mm_hfblock_x(18, 3)), (self.all_sprites, self.fruits), "melon")
			Fruit((self.mm_hfblock_x(19, 6)), (self.all_sprites, self.fruits), "pineapple")
			Fruit((self.mm_hfblock_x(18, 5)), (self.all_sprites, self.fruits), "apple")
			Fruit((self.mm_hfblock_x(11, 8)), (self.all_sprites, self.fruits), "kiwi")
			Fruit((self.mm_hfblock_x(15, 8)), (self.all_sprites, self.fruits), "kiwi")
			#Fruit((self.mm_hfblock_x(3, 3)), (self.all_sprites, self.fruits), "cherry")

			# Pipes for visual variety and navigation hints
			Pipe((self.mm_block(4, 7)), (self.all_sprites, self.collision_group), self.current_level)
			Pipe((self.mm_block(3, 7)), (self.all_sprites, self.collision_group), self.current_level)
			Pipe((self.mm_block(19, 5)), (self.all_sprites, self.collision_group), self.current_level)
			#Pipe((self.mm_block(12, 7)), (self.all_sprites, self.collision_group), self.current_level)
			#Pipe((self.mm_block(13, 7)), (self.all_sprites, self.collision_group), self.current_level)

			# Endpoint
			self.friend = Friend(self.mm_block_chara(19,5),(self.all_sprites,self.endpoint),self.current_level,facing_right=False)
			#self.friend = Friend((BLOCK_SIZE * 1,WINDOW_HEIGHT-(BLOCK_SIZE * 19)-64),(self.all_sprites,self.endpoint),self.current_level,facing_right=True)

		#player
		self.player = Player((25,400),(self.player_group),self.collision_group)
		#crash landing
		if self.current_level == 0:
			self.player.health = self.player.max_health - 1

	def get_bg_tiles(self):
		bg_list = ["Blue.png","Pink.png"]
		img = pygame.image.load(join("..","images","background",bg_list[self.current_level]))
		_, _, tile_width, tile_height = img.get_rect() 
		tiles = []
        
		for i in range(WINDOW_WIDTH // tile_width + 1):
			for j in range(WINDOW_HEIGHT // tile_height + 1):
				pos = (i * tile_width, j * tile_height)
				tiles.append(pos) 
		return img,tiles

	#level making & drawing
	def handle_scrolling(self,dt):
		scroll_area_width = 200
		player_velocity = self.player.direction.x * self.player.speed * dt
		if ((self.player.rect.right - self.offset_x >= WINDOW_WIDTH - scroll_area_width) and self.player.direction.x > 0) or (
                (self.player.rect.left - self.offset_x <= scroll_area_width) and self.player.direction.x < 0):
			self.offset_x += player_velocity
		self.offset_x = max(0,min(self.offset_x, GAME_WIDTH - WINDOW_WIDTH))

	def draw_background(self):
		for tile in self.bg_tiles:
			self.window.blit(self.bg_img, tile)

	def draw_sprites(self,game_duration):
		#background
		self.draw_background()

		#other sprites
		for sprite in self.all_sprites:
			sprite.draw(self.offset_x)
		
		#ui
		self.display_hearts()
		self.display_fruit_status()
		self.display_oxygen(game_duration)

		#player
		self.player.draw(self.window,self.offset_x)

	def run(self, dt, game_duration):
		self.handle_scrolling(dt)
		
		#updates
		self.player_group.update(dt)
		self.all_sprites.update(dt)

		#collisions
		self.hit_collision()
		self.fruit_collision(dt)
		self.win_collision()

		#draws
		self.draw_sprites(game_duration)


		
		
		