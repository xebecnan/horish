
import os
import random
import pygame
from pygame.locals import *

from locals import *

# Globals
world = None
stage = None
images = {}

def load_images():
	global images
	
	data = {
		'FLOOR-1-T': ['tile-t.png', (255,255,255), False],
		'FLOOR-1-F': ['tile-f.png', (255,255,255), False],
		'FLOOR-1-L': ['tile-l.png', (255,255,255), False],
		'FLOOR-2-T': ['tile-2-t.png', (255,255,255), False],
		'CHAR-1': ['character-1.png', None, True],
		'CHAR-2': ['character-2.png', None, True],
		'BG-3': ['bg-3.png', None, False],
		'BG-4': ['bg-4.png', None, False],
		'BG-5': ['bg-5.png', None, False],
		'BG-6': ['bg-6.png', None, False],
		'SMOBJ-1':['sm_obj.gif', None, False],
	}
	
	for key, val in data.iteritems():
		filename, colorkey, is_alpha = val
		img = pygame.image.load(os.path.join('images', filename))
		
		if is_alpha:
			img = img.convert_alpha()
		else:
			img = img.convert()
			
		if colorkey is not None:
			img.set_colorkey(colorkey)
			
		images[key] = img
	
def pos_world_to_scr(wpos):
	offx = 0
	x, y, h = wpos
	offx += y
	y = BASE_Y + y - h
	x = BASE_X + x + offx
	return [x, y]
		

class World:
	def __init__(self):
		self.map = []
		self.map_depth = 4
		self.map_width = 40
		for i in xrange(self.map_depth*self.map_width):
			tile = {
				'type': 'g',
				'height': 0,
				'dirty': False,
				'sprites': [],
			}
			self.map.append(tile)
			
		return
			
		for i in xrange(self.map_depth*self.map_width/3):
			self.map[random.randrange(self.map_depth*self.map_width)] = '_'
		self.map[60] = '_'
		self.map[8] = 'g'
		
	def get_tile(self, x, y, mode):
		if mode == 'index':
			i = x
			if i < 0 or i >= self.map_width * self.map_depth:
				return None
		else:
			if mode != 'map':
				x /= TILE_WIDTH
				y /= TILE_HEIGHT
			if x < 0 or x >= self.map_width or y < 0 or y >= self.map_depth:
				return None
			i = y*self.map_width+x
		return self.map[i]

def main():
	global world, stage, images
	
	pygame.init()
	screen = pygame.display.set_mode(WINSIZE)
	clock = pygame.time.Clock()
	load_images()
	
	world = World()
	
	from stage_mgr import InplayStageMgr
	stage = InplayStageMgr(screen)
	
	done = False
	step_mode = False
	stage_update_used = 0
	stage_paint_used = 0
	frame_n = 0
	while not done:
		
		if not step_mode or step_cd > 0:
			stage_update_start = pygame.time.get_ticks()
			stage.update()
			stage_update_used += pygame.time.get_ticks() - stage_update_start
			
			stage_paint_start = pygame.time.get_ticks()
			stage.paint()
			stage_paint_used += pygame.time.get_ticks() - stage_paint_start
			
			frame_n += 1
		if step_mode and step_cd > 0:
			step_cd -= 1
		
		pygame.display.update()
		
		for e in pygame.event.get():
			if e.type == KEYUP:
				if e.key == K_p:
					step_mode = True
					step_cd = 1
				elif e.key == K_o:
					step_mode = False
			
			if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
				done = True
				break
					
			stage.handle_event(e)
				
		clock.tick(50)
		
	
#~ if __name__ == '__main__':
	#~ main()

import traceback,sys

if __name__ == "__main__":
    if "profile" in sys.argv:
        import hotshot
        import hotshot.stats
        import tempfile
        import os
 
        profile_data_fname = tempfile.mktemp("prf")
        try:
            prof = hotshot.Profile(profile_data_fname)
            prof.run('main()')
            del prof
            s = hotshot.stats.load(profile_data_fname)
            s.strip_dirs()
            print "cumulative\n\n"
            s.sort_stats('cumulative').print_stats()
            print "By time.\n\n"
            s.sort_stats('time').print_stats()
            del s
        finally:
            # clean up the temporary file name.
            try:
                os.remove(profile_data_fname)
            except:
                # may have trouble deleting ;)
                pass
    else:
        try:
            main()
        except:
            traceback.print_exc(sys.stderr)