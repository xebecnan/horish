
import sys
import random, math
import pygame

from locals import *


class Particle:
	def __init__(self, mgr):
		self.pos = [0.0, 0.0]
		self.mgr = mgr
		self.life = 100
		
	def set_palette(self, palette):
		self.palette = palette
		
	def set_dirty(self):
		pass
		#x, y = round(self.pos[0]), round(self.pos[1])
		
	def set_pos(self, pos):
		self.pos[:] = pos
		
	def update(self):
		pass
		
class RadiantParticle(Particle):
	def __init__(self, mgr):
		Particle.__init__(self, mgr)
		self.vel = [0.0, 0.0]
		self.acc = [0.0, -.05]
		self.life = 10
		self.max_life = 10
		
	def test_1(self):
		#radian = math.radians(210+random.randrange(120))
		dir = random.randrange(360)
		radian = math.radians(dir)
		speed = 2.4 + random.random()*0.6
		vx, vy = speed * math.cos(radian), speed * math.sin(radian)
		vx, vy = vx+vy, vy
		self.vel[:] = [vx, vy]
		#self.acc = [random.random()*1.4-0.7, random.random()*2.0]
		
	def test_2(self):
		#radian = math.radians(210+random.randrange(120))
		dir = random.randrange(360)
		radian = math.radians(dir)
		speed = 0.4 + random.random()*0.6
		vx, vy = speed * math.cos(radian), speed * math.sin(radian)
		vx, vy = vx+vy, vy
		self.vel[:] = [vx, vy]
		self.acc = [random.random()*0.6-0.3, -.4-random.random()*.2]
		
	def init_random(self):
		self.test_1()
		
	def update(self):
		Particle.update(self)
		self.set_dirty()
		
		if self.life == 0:
			self.mgr.remove_particle(self)
			return
			
		self.life -= 1
		
		x, y = self.pos
		vx, vy = self.vel
		ax, ay = self.acc
		self.pos[:] = [x+vx, y+vy]
		self.vel[:] = [vx+ax, vy+ay]

def init_particle_tile_expand(particle):
		dir = random.randrange(360)
		radian = math.radians(dir)
		speed = 2.4 + random.random()*0.6
		vx, vy = speed * math.cos(radian), speed * math.sin(radian)
		vx, vy = vx+vy, vy
		particle.vel[:] = [vx, vy]

class ParticleSystem:
	def __init__(self, surf, stage):
		self.particles = []
		self.surf = surf
		self.stage = stage
		
		self.init_palette()
		
		self.particle_types = {
			'smoke': {
				'init': init_particle_tile_expand,
				'palette_name': 'smoke',
			},
			
			'flame': {
				'init': init_particle_tile_expand,
				'palette_name': 'smoke',
			},
		}
		
	def init_palette(self):
		#img = pygame.Surface((8,8))
		#img.fill((255,255,0))
		#self.palettes = [img] * 10
		self.palettes = {}
		palette = []
		for i in xrange(20):
			img = pygame.Surface((8, 8))
			#t = (40-i)*255/40
			t = 255
			img.fill((t, t, t))
			#img.fill(((160-i)*255/160, (20-i)*255/20,0))
			img.set_alpha((20-i)*255/20)
			palette.append(img)
		self.palettes['smoke'] = palette
			
		palette = []
		for i in xrange(30):
			img = pygame.Surface((4,4))
			img.fill((255,(30-i)*255/30,0))
			palette.append(img)
		for i in xrange(10):
			img = pygame.Surface((4,4))
			img.fill(((10-i)*255/10,0,0))
			img.set_alpha((10-i)*255/10)
			palette.append(img)
		self.palettes['flame'] = palette
		
	def add_particle(self, pos, palette_name, **kwargs):
		ptc = RadiantParticle(self)
		ptc.set_palette(self.palettes[palette_name])
		ptc.set_pos(pos)
		ptc.init_random()
		self.particles.append(ptc)
		
	def remove_particle(self, ptc):
		self.particles.remove(ptc)
		
	def update(self):
		rect = None
		for ptc in self.particles:
			x, y = int(ptc.pos[0]), int (ptc.pos[1])
			if rect == None:
				rect = pygame.Rect((x-4, y, 8, 8))
			else:
				rect.union_ip((x-4, y, 8, 8))
			ptc.update()
			
		if rect != None:
			stage = sys.modules['__main__'].stage
			world = sys.modules['__main__'].world
			rect.left += self.stage.offsetx # TODO
			stage.add_dirty(rect)
		
	def paint(self):
		for ptc in self.particles:
			x, y = int(ptc.pos[0]), int(ptc.pos[1])
			alpha = ptc.life*255 / ptc.max_life
			index = (ptc.max_life - ptc.life) * (len(ptc.palette)-1) / ptc.max_life
			img = ptc.palette[index]
			self.surf.blit(img, (x-4,y))
			#self.surf.set_at((x, y), (255,255,255,alpha))
	