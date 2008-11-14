
import sys, random, math
import pygame
from pygame.locals import *

from locals import *

world = sys.modules['__main__'].world
images = sys.modules['__main__'].images
pos_world_to_scr = sys.modules['__main__'].pos_world_to_scr

class ImageExtractor:
	def __init__(self, img, rows, cols):
		self.image = img
		self.rows = rows
		self.cols = cols
		self.cache = {}
		self.mode = 'normal'
		self.colorkey = None
		
	def set_mode_alpha(self):
		self.mode = 'alpha'
		
	def set_mode_colorkey(self, colorkey):
		self.mode = 'colorkey'
		self.colorkey = colorkey
		
	def get_image(self, index):
		if not self.cache.has_key(index):
			rows, cols = self.rows, self.cols
			x, y = index % cols, index / cols
			w, h = self.image.get_width() / cols, self.image.get_height() / rows
			if self.mode == 'alpha':
				img = pygame.Surface((w,h), SRCALPHA, 32)
			elif self.mode == 'colorkey':
				img = pygame.Surface((w,h))
				img.set_colorkey(self.colorkey)
			else:
				img = pygame.Surface((w,h))
			img.blit(self.image, (0,0), (x*w, y*h, w, h))
			self.cache[index] = img
		return self.cache[index]

class ImageExtractorEx:
	def __init__(self, img):
		self.image = img
		self.cache = {}
		self.mode = 'normal'
		self.colorkey = None
		
	def set_mode_alpha(self):
		self.mode = 'alpha'
		
	def set_mode_colorkey(self, colorkey):
		self.mode = 'colorkey'
		self.colorkey = colorkey
		
	def get_image(self, simple_rect):
		x, y, w, h = simple_rect
		if not self.cache.has_key(simple_rect):
			if self.mode == 'alpha':
				img = pygame.Surface((w,h), SRCALPHA, 32)
			elif self.mode == 'colorkey':
				img = pygame.Surface((w,h))
				img.set_colorkey(self.colorkey)
			else:
				img = pygame.Surface((w,h))
			img.blit(self.image, (0,0), (x, y, w, h))
			self.cache[simple_rect] = img
		return self.cache[simple_rect]
		
	
class MySprite:
	def __init__(self):
		self.images = []
		self.frames = []
		self.frame_index = 0
		self.frame_loop = True
		self.frame_rate = 8
		self.frame_cd = self.frame_rate
		self.frame_run = False
		self.dirty = True
		self.rect = None
		self.stage = None
		self.pos = [0, 0, 0]
		
	def set_stage(self, stage):
		self.stage = stage
	
	def get_image(self):
		assert len(self.frames) >= 1, "[%s] length of frames is 0" % self.__class__.__name__
		index = self.frames[self.frame_index]
		return self.images[index]
		
	def __on_frame_loop(self):
		if self.frame_loop:
			self.frame_index = 0
		else:
			self.frame_index -= 1
			self.frame_run = False
			
	def set_dirty(self):
		#if self.dirty: return
		self.dirty = True
		
	def update(self):
		pass
		
	def update_wrap(self):
		assert self.rect is not None
		ori_rect = pygame.Rect(self.rect)
		self.update()
		if self.dirty or self.rect != ori_rect:
			assert self.stage is not None, "self.stage is None"
			self.stage.add_dirty(ori_rect.union(self.rect))
		
	def on_before_paint(self):
		if self.frame_run:
			if self.frame_cd > 0:
				self.frame_cd -= 1
			else:
				self.frame_cd = self.frame_rate
				self.frame_index += 1
				if self.frame_index >= len(self.frames):
					self.__on_frame_loop()
		
	def on_paint(self):
		self.dirty = False
	
class Player(MySprite):
	def __init__(self):
		MySprite.__init__(self)
		imgext = ImageExtractor(images['CHAR-1'], 4, 4)
		imgext.set_mode_alpha()
		for i in xrange(16):
			self.images.append(imgext.get_image(i))
			
		self.left_stand_frames = [5]
		self.right_stand_frames = [9]
		self.down_frames = range(0, 4)
		self.left_frames = range(4, 8)
		self.right_frames = range(8, 12)
		self.up_frames = range(12, 16)
		
		self.frames = self.right_stand_frames
		self.frame_run = False
		self.rect = self.get_image().get_rect()
		self.pos = [500, 10, 0]
		self.rect.bottomleft = pos_world_to_scr(self.pos)
		
		self.vh = 0
		
	def change_frames(self, frames, frame_loop, frame_rate):
		if self.frames == frames: return
		self.frames = frames
		self.frame_index = 0
		if frame_rate is not None:
			self.frame_rate = frame_rate
		if len(self.frames) > 1:
			self.frame_run = True
			self.frame_cd = self.frame_rate
			self.frame_loop = frame_loop
		else:
			self.frame_run = False
		self.set_dirty()
			
	def set_pos_ip(self, dpos):
		x, y, h = self.pos
		dx, dy, dh = dpos
		if h < -1000:
			h = -1000
		self.pos[:] = [x+dx, y+dy, h+dh]
		self.rect.bottomleft = pos_world_to_scr(self.pos)
		
		# land
		if h != 0 and h + dh == 0:
			self.on_jump_land()
		
		# deal with scroll
		win_w, win_h = WINSIZE
		scr_x, scr_y = pos_world_to_scr(self.pos)
		rel_x = scr_x-self.stage.offsetx
		if rel_x >= win_w - SCROLL_MARGIN:
			self.stage.scroll(min(5, rel_x-(win_w-SCROLL_MARGIN)))
		elif rel_x < SCROLL_MARGIN:
			self.stage.scroll(max(-5, rel_x-SCROLL_MARGIN))
			
	def on_jump_land(self):
		pass
		
	def on_start_jump(self):
		for i in xrange(100):
			x = self.rect.left + 8 + random.randrange(self.rect.width-16) - self.stage.offsetx
			y = self.rect.bottom
			self.stage.ptcsys.add_particle((x, y), 'smoke')
		
	def update(self):
		MySprite.update(self)
		key_map = pygame.key.get_pressed()
					
		# DEBUG
		if key_map[K_q]:
			self.stage.scroll(-5)
		elif key_map[K_e]:
			self.stage.scroll(5)
		
		dir_left, dir_right, dir_up, dir_down = False, False, False, False
		if key_map[K_a]:
			if not key_map[K_d]:
				dir_left = True
		elif key_map[K_d]:
			dir_right = True
		if key_map[K_w]:
			if not key_map[K_s]:
				dir_up = True
		elif key_map[K_s]:
			dir_down = True
			
		dx, dy, dh = 0, 0, 0
		x, y, h = self.pos
		
		on_ground = True
		if h > 0 or h < 0 or self.vh > 0:
			on_ground = False
		else:
			tile = world.get_tile(x, y, 'sprite')
			if tile is None or tile['type'] != 'g':
				tile = world.get_tile(x+self.rect.width, y, 'sprite')
				if tile is None or tile['type'] != 'g':
					on_ground = False
				
		if not on_ground:
			self.vh -= 1
		else:
			self.vh = 0
		
		if self.vh != 0:
			dh = self.vh
			
		if dir_up:
			if not dir_left and not dir_right:
				self.change_frames(self.up_frames, True, None)
			if y-2>=0:
				dy -= 2
				dx += 2
		if dir_down:
			if not dir_left and not dir_right:
				self.change_frames(self.down_frames, True, None)
			if y+2 < world.map_depth*TILE_HEIGHT:
				dy += 2
				dx -=2
		if dir_right:
			self.change_frames(self.right_frames, True, None)
			dx += 2
		if dir_left:
			self.change_frames(self.left_frames, True, None)
			dx -= 2
			
		if key_map[K_SPACE] and h==0 and self.vh == 0:
			self.on_start_jump()
			self.vh = 25
			
		if dx != 0 or dy != 0 or dh != 0:
			self.set_pos_ip([dx, dy, dh])
		elif self.frames != self.right_stand_frames and self.frames != self.left_stand_frames:
			if self.frames == self.left_frames:
				self.change_frames(self.left_stand_frames, True, None)
			else:
				self.change_frames(self.right_stand_frames, True, None)
				
class EnemyBoy(MySprite):
	def __init__(self):
		MySprite.__init__(self)
		imgext = ImageExtractor(images['CHAR-2'], 4, 4)
		imgext.set_mode_alpha()
		for i in xrange(16):
			self.images.append(imgext.get_image(i))
			
		self.left_stand_frames = [5]
		self.right_stand_frames = [9]
		self.down_frames = range(0, 4)
		self.left_frames = range(4, 8)
		self.right_frames = range(8, 12)
		self.up_frames = range(12, 16)
		
		self.frames = self.left_frames
		self.frame_run = True
		self.rect = self.get_image().get_rect()
		self.pos = [800, 10, 0]
		self.rect.bottomleft = pos_world_to_scr(self.pos)
		
		self.vh = 0
		
		self.face_right = False
		
	def update(self):
		MySprite.update(self)
		x, y, h = self.pos
		dx, dy, dh = 0, 0, 0
		if x < 100: self.face_right = True
		elif x > 1000: self.face_right = False
			
		if self.face_right:
			self.frames = self.right_frames
			dx = 1
		else:
			self.frames = self.left_frames
			dx = -1
			
		self.pos[:] = [x+dx, y+dy, h+dh]
		self.rect.bottomleft = pos_world_to_scr(self.pos)

def calc_dir(start_pos, target_pos):
	if int(start_pos[0]) == target_pos[0]:
		if start_pos[1] < target_pos[1]:
			return 90
		else:
			return 270
	elif start_pos[1] == target_pos[1]:
		if start_pos[0] < target_pos[0]:
			return 0
		else:
			return 180
	else:
		return math.degrees(math.atan2((target_pos[1] - start_pos[1]), (target_pos[0] - start_pos[0])))
		
class Bullet(MySprite):
	def __init__(self, from_pos, to_pos):
		MySprite.__init__(self)
		imgext = ImageExtractorEx(images['SMOBJ-1'])
		imgext.set_mode_colorkey((255,0,255))
		for x in xrange(0, 384, 32):
			self.images.append(imgext.get_image((x, 0, 32, 32)))
			
		self.all_frames=[]
		for i in xrange(len(self.images)):
			self.all_frames.append([i])
		
		self.speed = 10.0
		dir = calc_dir(from_pos, to_pos)
		self.set_dir(dir)
		
		self.frames = self.all_frames[0]
		self.frame_run = False
		self.rect = self.get_image().get_rect()
		self.pos = from_pos
		self.rect.center = from_pos

	def set_speed(self, speed):
		self.speed = speed

	def set_dir(self, dir):
		self.dir = dir
		self.vel = [self.speed * math.cos(math.radians(self.dir)), self.speed * math.sin(math.radians(self.dir))]
		
	def update(self):
		MySprite.update(self)
		x, y = self.pos
		vx, vy = self.vel
		self.pos[:] = [x + vx, y+vy]
		
		self.rect.center = int(x+vx), int(y+vy)
		
		if random.random() > .9:
			self.stage.ptcsys.add_particle((self.rect.centerx - self.stage.offsetx, self.rect.centery), 'flame')
		
		scr_rect = pygame.Rect(WINRECT)
		scr_rect.left += self.stage.offsetx
		if not scr_rect.colliderect(self.rect):
			self.stage.remove_bullet(self)
	
	def get_image(self):
		index = ((int(self.dir) + 300) % 360) / 30
		return self.images[index]