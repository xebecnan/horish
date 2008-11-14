# -*- coding: gb2312 -*-

import sys
import pygame
from pygame.locals import *

from locals import *

# Module Constants
DIRTY_RECT_WIDTH = 40
DIRTY_RECT_HEIGHT = 40

world = sys.modules['__main__'].world
images = sys.modules['__main__'].images
pos_world_to_scr = sys.modules['__main__'].pos_world_to_scr

# HELPER FUNCTIONS
	
def dict_list_add(dict, key, value):
	if not dict.has_key(key):
		dict[key] = [value]
	else:
		arr = dict[key]
		for i in xrange(len(arr)):
			sprite = arr[i]
			x, y, h = sprite.pos
			if y>value.pos[1]:
				arr.insert(i, value)
				return
		arr.insert(len(arr), value)

def rect_collide_tiles(rect):
	map_start_y = (rect.top - BASE_Y) / TILE_HEIGHT
	if map_start_y < 0:
		map_start_y = 0
	elif map_start_y >= world.map_depth:
		return []
	map_end_y = (rect.bottom - BASE_Y) / TILE_HEIGHT
	if map_end_y < 0:
		return []
	elif map_end_y >= world.map_depth:
		map_end_y = world.map_depth - 1
		
	ret = []
	for map_y in xrange(map_start_y, map_end_y+1):
		offx = (world.map_depth - map_y) * TILE_HEIGHT - (TILE_PIC_WIDTH - TILE_WIDTH)
		map_start_x = (rect.left + offx) / TILE_WIDTH
		if map_start_x < 0:
			map_start_x = 0
		elif map_start_x >= world.map_width:
			continue
		map_end_x = (rect.right + offx - 1) / TILE_WIDTH + 1
		if map_end_x < 0:
			continue
		elif map_end_x >= world.map_width:
			map_end_x = world.map_width-1
		for map_x in xrange(map_end_x+1, map_start_x-1, -1):
			ret.append((map_x, map_y))
	return ret

class StageMgr:
	def __init__(self, surface):
		pass
		
class InplayStageMgr(StageMgr):
	def __init__(self, surface):
		StageMgr.__init__(self, surface)
		self.surf = surface
		self.dirty_rects = []
		
		# map screen to several pre-defined dirty rect regions
		win_w, win_h = WINSIZE
		self.dmap_cols = win_w / DIRTY_RECT_WIDTH
		self.dmap_rows = win_h / DIRTY_RECT_HEIGHT
		self.dirty_map = [False] * self.dmap_cols * self.dmap_rows
		
		self.sprites = []
		self.bullets = []
		
		from particle_system import ParticleSystem
		self.ptcsys = ParticleSystem(surface, self)
		
		self.offsetx = 0
		self.add_dirty(((0,0), WINSIZE))
	
		from sprite import Player, EnemyBoy
		player = Player()
		self.add_sprite(player)
		
		em = EnemyBoy()
		self.add_sprite(em)
		
		self.player = player
		
		self.offsetx_limit_left = 0
		self.offsetx_limit_right = None
			
	def scroll(self, offx):
		self.offsetx += offx
		if self.offsetx_limit_left != None and self.offsetx < self.offsetx_limit_left:
			self.offsetx = self.offsetx_limit_left
		if self.offsetx_limit_right != None and self.offset > self.offsetx_limit_right:
			self.offsetx = self.offsetx_limit_right
		self.add_dirty(((self.offsetx,0),WINSIZE))
		
	def scroll_limit(self, left_limit, right_limit):
		self.offsetx_limit_left = left_limit
		self.offsetx_limit_right = right_limit
	
	def add_sprite(self, sprite):
		self.sprites.append(sprite)
		sprite.set_stage(self)
		
	def add_bullet(self, bullet):
		self.bullets.append(bullet)
		bullet.set_stage(self)
		
	def remove_bullet(self, bullet):
		self.bullets.remove(bullet)
		
	def handle_event(self, e):
		if e.type == KEYUP:
			if e.key == K_i:
				self.sprites.remove(self.player)
				from sprite import Player
				self.player = Player()
				self.add_sprite(self.player)
				self.scroll(-self.offsetx)
			elif e.key == K_t:
				x, y, h = self.player.pos
				print self.player.pos, x/TILE_WIDTH, y/TILE_HEIGHT
				
		elif e.type == MOUSEBUTTONDOWN and e.button == 1:
			from sprite import Bullet
			x, y = self.player.rect.center
			tx, ty = e.pos
			b = Bullet([x,y], [tx+self.offsetx,ty])
			self.add_bullet(b)
			#for i in xrange(100):
			#	stage.ptcsys.add_particle(e.pos)
		
	def populate_dirty_rects(self):
		self.dirty_rects[:] = []
		i = 0
		for y in xrange(self.dmap_rows):
			row_flag = False
			adding_left = None
			for x in xrange(self.dmap_cols):
				if self.dirty_map[i]:
					if adding_left == None:
						adding_left = x * DIRTY_RECT_WIDTH + self.offsetx
					self.dirty_map[i] = False
				else:
					if adding_left is not None:
						left = x * DIRTY_RECT_WIDTH + self.offsetx
						top = y * DIRTY_RECT_HEIGHT
						adding_width = left - adding_left
						self.dirty_rects.append(pygame.Rect((adding_left, top, adding_width, DIRTY_RECT_HEIGHT)))
						adding_left = None
					
				i += 1
			if adding_left is not None:
				top = y * DIRTY_RECT_HEIGHT
				adding_width = WINSIZE[0] + self.offsetx - adding_left
				if len(self.dirty_rects) > 0:
					last_rect = self.dirty_rects[-1]
					if last_rect.left == adding_left and last_rect.width == adding_width:
						last_rect.union_ip((adding_left, top, adding_width, DIRTY_RECT_HEIGHT))
					else:
						self.dirty_rects.append(pygame.Rect((adding_left, top, adding_width, DIRTY_RECT_HEIGHT)))
				else:
					self.dirty_rects.append(pygame.Rect((adding_left, top, adding_width, DIRTY_RECT_HEIGHT)))
				
	
	def add_dirty(self, rect):
		if not isinstance(rect, pygame.Rect):
			rect = pygame.Rect(rect)
		x1 = (rect.left - self.offsetx) / DIRTY_RECT_WIDTH
		x2 = (rect.right - self.offsetx) / DIRTY_RECT_WIDTH
		y1 = rect.top / DIRTY_RECT_HEIGHT
		y2 = rect.bottom / DIRTY_RECT_HEIGHT
		for y in xrange(y1, y2+1):
			for x in xrange(x1, x2+1):
				if x < 0 or x >= self.dmap_cols or y < 0 or y >= self.dmap_rows:
					continue
				self.dirty_map[y*self.dmap_cols + x] = True
				
		# old way
		#~ self.dirty_rects.append(pygame.Rect(rect))
		
	def update(self):
		for sprite in self.sprites:
			sprite.update_wrap()
			
		for bullet in self.bullets:
			bullet.update_wrap()
			
		self.ptcsys.update()
		
	def paint(self):
		self.populate_dirty_rects()
		
		for sprite in self.sprites:
			sprite.on_before_paint()
		
		# LAYER - 0
		for r in self.dirty_rects:
			self.paint_background(r)
		
		# LAYER - 1
		wait_draw_up = {}
		wait_draw_down = {}
		
		for sprite in self.sprites:
			if not sprite.dirty and sprite.rect.collidelist(self.dirty_rects) == -1:
				continue
			x, y, h = sprite.pos
			map_x = x / TILE_WIDTH
			map_y = y / TILE_HEIGHT
			
			# 特殊情况，精灵处于地图之外
			if map_x >= world.map_width:
				self.paint_sprite(sprite)
				sprite.on_paint()
				continue
			elif map_x < 0:
				dict_list_add(wait_draw_up, -1, sprite)
				continue
			
			# 将精灵与地图对应起来
			map_i = map_y * world.map_width + map_x
			if h >= 0:
				dict_list_add(wait_draw_up, map_i, sprite)
			else:
				dict_list_add(wait_draw_down, map_i, sprite)
				
				
		for r in self.dirty_rects:
			tiles = rect_collide_tiles(r)
			for map_x, map_y in tiles:
				tile = world.get_tile(map_x, map_y, 'map')
				if tile != None:
					tile['dirty'] = True
				
		scr_rect = pygame.Rect(WINRECT)
		scr_rect.left += self.offsetx
		tiles = rect_collide_tiles(scr_rect)
		for map_x, map_y in tiles:
			map_i = map_y * world.map_width + map_x
			tile = world.get_tile(map_x, map_y, 'map')
			if tile is None: continue
				
			if wait_draw_down.has_key(map_i):
				for sprite in wait_draw_down[map_i]:
					self.paint_sprite(sprite)
					sprite.on_paint()
			
			if tile['dirty'] == True and tile['type'] == 'g':
				tile['dirty'] = False
				
				y = map_y*TILE_HEIGHT
				x = map_x*TILE_WIDTH
				
				# paint floor's top face
				x, y = pos_world_to_scr([x,y,tile['height']])
				rect = pygame.Rect((x,y), (TILE_PIC_WIDTH, TILE_PIC_HEIGHT))
				for dr in self.dirty_rects:
					if rect.colliderect(dr):
						self.paint_floor(x, y, dr, 'top')
				
				# paint floor's front face
				x1, y1 = x+TILE_HEIGHT, y+TILE_HEIGHT
				for dr in self.dirty_rects:
					#if dr.colliderect((x1,y1, TILE_WIDTH, TILE_THICKNESS)):
					if dr.colliderect((x1,y1, TILE_WIDTH, tile['height'])):
						self.paint_floor(x1, y1, dr, 'front')
						
				#paint floor's left face
				x2, y2 = x, y+1
				for dr in self.dirty_rects:
					if dr.colliderect((x2, y2, 49, 89)):
				#	#if rect.colliderect(dr):
						self.paint_floor(x2, y2, dr, 'left')
				
			if wait_draw_up.has_key(map_i):
				for sprite in wait_draw_up[map_i]:
					self.paint_sprite(sprite)
					sprite.on_paint()
						
		if wait_draw_up.has_key(-1):
			for sprite in wait_draw_up[-1]:
				self.paint_sprite(sprite)
				sprite.on_paint()
				
			
		# LAYER - 2
		#for sprite in self.sprites:
			
		self.dirty_rects[:] = []
		
		for bullet in self.bullets:
			self.paint_sprite(bullet)
		
		# particle system
		self.ptcsys.paint()
			
	def paint_background(self, dirty_rect):
		img = images['BG-6']
		clip_rect = pygame.Rect(dirty_rect)
		clip_rect.left -= self.offsetx
		self.surf.set_clip(clip_rect)
		
		#x, y = rect.topleft
		#self.surf.blit(img, (x-self.offsetx, y), ((x-self.offsetx, y),(rect.width, rect.height)))
		
		self.surf.blit(img, clip_rect, clip_rect)
		self.surf.set_clip(WINRECT)
		
	def paint_floor(self, x, y, dirty_rect, mode):
		image_map = {
			'top': images['FLOOR-1-T'],
			'front': images['FLOOR-1-F'],
			'left': images['FLOOR-1-L'],
		}
		assert image_map.has_key(mode)
		img = image_map[mode]
			
		clip_rect = pygame.Rect(dirty_rect)
		clip_rect.left -= self.offsetx
		self.surf.set_clip(clip_rect)
		self.surf.blit(img, (x-self.offsetx,y))
		self.surf.set_clip(WINRECT)
		
	def paint_sprite(self, sprite):
		img = sprite.get_image()
		x, y = sprite.rect.topleft
		self.surf.blit(img, (x - self.offsetx, y))
		