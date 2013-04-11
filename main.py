#!/usr/bin/env python
# -*- coding: utf-8 *-*
import sys
import pygame
#from pygame.locals import *		# import pygame.locals as pyloc
from pygame.locals import K_LEFT, K_RIGHT, K_SPACE, K_RETURN, K_ESCAPE, K_p, KEYUP, KEYDOWN, QUIT
from random import randint

DEBUG = False

pygame.init()

MENU_FONT = pygame.font.Font("res/starcraft.ttf", 20)
HUD_FONT = pygame.font.Font("res/pixel.ttf", 20)
MSG_FONT = pygame.font.Font("res/pixel.ttf", 54)
LOST_FONT = pygame.font.Font("res/pixel.ttf", 120)

MUSIC = {	'active': True,
			'menu': "res/ObservingTheStar.ogg",
			'game': "res/DataCorruption.ogg",
			'lost': "res/TragicAmbient.ogg"
		}
TIMER = pygame.time.Clock()
FPS = 30 # 30 frames per second seem reasonable
tick = 0
TEXT_COLOR = (200, 200, 200)
MOVEMENT_KEYS = [K_LEFT, K_RIGHT, K_SPACE]
CONTROL_KEYS = [K_RETURN, K_ESCAPE, K_p]
KEYS = MOVEMENT_KEYS + CONTROL_KEYS
LEAGUE = [0, 10, 50, 100, 500, 1000, 5000]

# pygame inits
pygame.display.set_caption('PyInSpace!')
DISPLAY = pygame.display.set_mode((900, 500))

# load all sprites at the beginning
SPRITES = {s : pygame.image.load('res/' + str(s) + '.png').convert_alpha()
			for s in [ 'award_bronze', 'award_silver', 'award_gold',
				'coin_bronze', 'coin_silver', 'coin_gold',
				'coin_stack', 'coin_stacks',
				'ufo', 'enemyshot', 'dead3', 'dead4',
				'player', 'playershot',
				'empty', 'logo',
				'heart', 'shield', 'lightning',
				'fire', 'diamond', 'ruby' ]
				+ ["enemy"+str(i)+s+str(x) for x in range(3,5) for s in ['a','b'] for i in range(1,4)]
				+ ["league"+str(i) for i in range(0,6)]
		}
# load sounds
SOUNDS = {s : pygame.mixer.Sound('res/' + str(s) + '.ogg')
			for s in ['laser_single', 'menu-confirm', 'confirm', 'playerdeath',
					  'enemy123deathA', 'enemy123deathB', 'ufodeath']
		 }


# helper functions
getsurface = lambda s: SPRITES[s] if s in SPRITES else pygame.image.load('res/' + s + '.png').convert_alpha()
getogg = lambda s: SOUNDS[s] if s in SOUNDS else pygame.mixer.Sound('res/' + s + '.ogg')
playsound = lambda s: getogg(s).play()


class PyInSpaceSprite(pygame.sprite.Sprite):
	def __init__(self, pic, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = getsurface(pic)
		self.rect = self.image.get_rect()
		self.rect.topleft = (x,y)


def render(func=None):
	''' decorator function for rendering '''
	# store function
	if func:
		render.funcs.append(func)
		return func

	# rendering process
	else:
		DISPLAY.fill((0, 0, 0))
		for f in render.funcs:
			f()
		TIMER.tick(FPS)
		pygame.display.update()
render.funcs = []


@render
def starsky():
	''' render astonishing star sky. '''
	if tick % 100 == 0:
		for _ in range(randint(0, 25 - len(starsky.stars))):
			starsky.stars.append((randint(22, 882), randint(-500, 0), 0))
	# update and delete starsja, aber da hast du nirgendwo anders state geschrieben
	if tick % 3 == 0:
		starsky.stars = [(x, y + 1, z if z == 0 or z > 190 else z + 7)
						for x, y, z in starsky.stars if y < 500]
	if tick % 100 == 0:
		r = randint(0, len(starsky.stars) - 1)
		if starsky.stars[r][2] == 0: starsky.stars[r] = (starsky.stars[r][0], starsky.stars[r][1], 1)

	# render stars
	for x, y, z in starsky.stars:
		b = 60 + z % 190
		pygame.draw.circle(DISPLAY, (b, b, b), (x, y), 2)
# mode doesn't matter for the bg, so initialsing it once is ok
starsky.stars = [(randint(50, 850), randint(50, 450), 0) for _ in range(randint(5, 10))]


@render
def lost():
	# no global inference
	global state
	if state not in [game, lost]: return

	# game over screen
	if lost.show > 0:
		label = LOST_FONT.render("GAME OVER!", 1, (200, 50, 50))
		pos = label.get_rect(centerx = 450, centery = 250)
		DISPLAY.blit(label, pos)
		lost.show -= 1

		if lost.show  == 0: state = menu
	# end game
	elif player.health < 0:
		lost.show = 300
		state = lost
lost.show = 0


@render
def milestone():
	''' shows milestone '''
	if state is not game: return

	# show level label
	if milestone.show > 0:
		milestone.show -= 1
		label = MSG_FONT.render("LEVEL " + str(milestone.level), 1, (200, 50, 50))
		pos = label.get_rect(centerx = 450, centery = 350)
		DISPLAY.blit(label, pos)

	# next level
	if not LEAGUE or player.score < LEAGUE[0]: return

	# initializing
	milestone.level += 1
	milestone.show = 45
	LEAGUE.pop(0)

	# increase difficulty
	player.thunderMax = 9 - milestone.level
	player.shield = max(0, player.shield - 1)
milestone.level = 0
milestone.show = 0


@render
def menu():
	''' render the menu '''
	if state is not menu: return

	DISPLAY.blit(getsurface('logo'), (157, 100))
	pygame.draw.rect(DISPLAY, (192, 192, 192), (250, 300, 400, 60))
	pygame.draw.rect(DISPLAY, (80, 80, 80), (255, 305, 390, 50))
	label = MENU_FONT.render("Press ENTER to start", 1, TEXT_COLOR)
	pos = label.get_rect(centerx = 450, centery = 330)
	DISPLAY.blit(label, pos)


@render
def game():
	''' Render Heads Up Display '''
	# no rendering if not in-game
	if state is not game: return

	info = list(zip(list(map(getsurface, ['heart', 'shield', 'lightning', 'coin_stacks'])),
			[0, 80, 160, 800],
			list(map(str, [player.health, player.shield, player.thunder, player.score]))))

	for img, px, txt in info:
		DISPLAY.blit(img, (4+px, 4))
		label = HUD_FONT.render(txt, 1, TEXT_COLOR)
		pos = label.get_rect(left = 40+px, centery = 20)
		DISPLAY.blit(label, pos)


@render
def player():
	''' Player function which renders the player and holds its state '''
	# no rendering if not in-game
	if state is not game: return
	# reload thunder
	player.reload += 1

	if player.reload == 99 and player.thunder < player.thunderMax:
		player.thunder += 1
		player.reload = 0

	# release cooldown
	if player.cooldown > 0:
		player.cooldown -= 1

	# move shots
	for shot in player.shots:
		shot.rect.y -= player.shotspeed
		if shot.rect.y < -20:
			player.shots.remove(shot)

	# rendering
	#DISPLAY.blit(getsurface('player'), (32 + 7 * player.xUnits, 440))
	player.group.draw(DISPLAY)
	player.shots.draw(DISPLAY)
player.xUnits = 56
#player.speed = 7
player.shotspeed = 7
player.thunderMax = 9


@render
def invaders():
	''' Renders enemies and their shots '''
	if state is not game: return

	def move(e, x, y):
		e.pos = (e.pos[0] + x, e.pos[1] + y)

	# no rendering if not in-game
	if state is not game or len(invaders.mob) == 0: return

	# mob variables
	xMin = min(map(lambda e: e.pos[0], invaders.mob))
	xMax = max(map(lambda e: e.pos[0], invaders.mob))
	yMax = max(map(lambda e: e.pos[1], invaders.mob))

	if tick % 50 == 0:
		if invaders.dir == (True, 0):
			if xMax >= 30: invaders.dir = (True, 1)
		elif invaders.dir == (False, 0):
			if xMin <= 0: invaders.dir = (False, 1)
		else:
			a, b = invaders.dir
			invaders.dir = (not a, b - 1)

	# move and render all invaders
	for grps in [invaders.mob, invaders.corpses]:
		for inv in grps:
			x, y = inv.pos
			# TODO: smoother movement
			if tick % 50 == 0:
				if invaders.dir == (True, 0):
					if xMax < 30: x += 1
				elif invaders.dir == (False, 0):
					if xMin > 0: x -= 1
				else:
					if yMax < 30: y += 1
				inv.pos = (x, y)
			inv.rect.topleft = (26+25*x, 45+10*y)
	for inv in invaders.mob:
		inv.anim += randint(1,1) # animation: (0,0)=none  (0,1)=indiviual (1,1)=uniform
		if inv.anim >= 20:
			inv.image = getsurface('enemy1a3')
		if inv.anim >= 40:
			inv.image = getsurface('enemy1b3')
			inv.anim = 0

	invaders.mob.draw(DISPLAY)

	# timeout for corpses
	for corp in invaders.corpses:
		corp.ttl = corp.ttl - 1 if corp.ttl > 0 else corp.ttl
		if corp.ttl == 0: invaders.corpses.remove(corp)
	invaders.corpses.draw(DISPLAY)

	# move and render all shots
	for shot in invaders.shots:
		shot.rect.y += invaders.shotspeed
		if shot.rect.y > 520:
			invaders.shots.remove(shot)
	invaders.shots.draw(DISPLAY)
#invaders.speed = 7
invaders.shotspeed = 10


@render
def invaders_spawn():
	if state is not game: return
	if len(invaders.mob) > 0 or len(invaders.shots) > 0 or len(player.shots) > 0: return

	# full reload
	player.thunder = player.thunderMax

	# new invaders
	for x in range(0,30,3):
		for y in range(0, 18, 3):
			newenemy = PyInSpaceSprite('enemy'+str(y%3+1)+'a3', 26+25*x, 45+10*y)
			newenemy.pos = (x, y)
			newenemy.ttl = -1
			newenemy.anim = 0
			invaders.mob.add(newenemy)


@render
def invaders_shots_spawn():
	if state is not game: return
	if len(invaders.mob) == 0 or tick % 10 == 0: return

	# get the list of the bottom invaders
	bottom = {}
	for mob in invaders.mob:
		x, y = mob.pos
		if x not in bottom or y > bottom[x][1]:
			bottom[x] = (x, y)

	# randomly creates a shot
	if randint(1, 1000) > 980: # default 990
		elem = bottom.items()[randint(0, len(bottom)-1)][1] # random pos
		newshot = PyInSpaceSprite('enemyshot', 26+25*elem[0]+15, 45+10*elem[1]+6)
		invaders.shots.add(newshot)


def initialize_game():
	if DEBUG: print("initializing game mode")
	player.health	= 3
	player.shield	= 0
	player.thunder	= 9
	player.shots	= pygame.sprite.Group()
	player.cooldown	= 0
	player.score	= 0
	player.reload	= 0
	player.sprite = PyInSpaceSprite('player', 0, 440)
	player.group = pygame.sprite.Group()
	player.group.add(player.sprite)
	invaders.dir = (True, 0)
	invaders.mob = pygame.sprite.Group()
	invaders.corpses = pygame.sprite.Group()
	invaders.shots = pygame.sprite.Group()


def adjust_music(state):
	if adjust_music.laststate != state:
		try:
			#pygame.mixer.music.fadeout(200) # TODO: BLOCKS WHILE FADING OUT
			pygame.mixer.music.load(MUSIC[str(state.__name__)])
			pygame.mixer.music.play()
			if DEBUG: print("current music: %s" % MUSIC[str(state.__name__)])
			adjust_music.laststate = state
		except AttributeError:
			pass


# final inits
state = menu
adjust_music.laststate = game # just needs to be something else than state
events = []

if DEBUG: print("entering main game loop")
# main game loop
while state:

	# event handling
	for e in pygame.event.get():
		# quit event
		if e.type == QUIT:
			state = None
			continue

		# skip event
		if e.type not in [KEYDOWN, KEYUP] or e.key not in KEYS:
			continue

		# store events
		if e.type == KEYDOWN:
			events.append(e.key)
		elif e.key in events:
			events.remove(e.key)

	# start game
	if state is menu and K_RETURN in events:
		if DEBUG: print("entering game")
		initialize_game()
		#playsound('menu-confirm')
		state = game
		continue

	# back to menu
	if state is game and K_ESCAPE in events:
		#cleanup_game() # ?
		if DEBUG: print("leaving game")
		state = menu
		continue

	if (MUSIC['active']):
		adjust_music(state)

	if state is game:
		# move player
		if K_LEFT in events and player.xUnits > 0:
			player.xUnits -= 1
		elif K_RIGHT in events and player.xUnits < 112:
			player.xUnits += 1
		player.sprite.rect.x = 32 + 7 * player.xUnits

		# player shoots
		if K_SPACE in events and player.thunder > 0 and player.cooldown == 0:
			player.thunder -= 1
			player.cooldown = 7
			newshot = PyInSpaceSprite('playershot', (55+7*player.xUnits), 440)
			player.shots.add(newshot)
			if DEBUG: print("player fired a shot at x=%d" % newshot.rect.x)
			playsound('laser_single')

		# It'z time to make the magicz...
		# noo, just doing the collision detection and dying in one line
		enemies_hit = pygame.sprite.groupcollide(invaders.mob, player.shots, False, True)
		player.score += len(enemies_hit)
		player.thunder = min(player.thunderMax, len(enemies_hit) + player.thunder)
		if len(enemies_hit) > 0:
			player.reload = 0

		for enem in enemies_hit:
			playsound('enemy123deathA')
			invaders.mob.remove(enem)
			enem.image = getsurface('dead3')
			enem.ttl = 10
			invaders.corpses.add(enem)

		# enemy shots hit the player
		playercollide = pygame.sprite.spritecollide(player.sprite, invaders.shots, True)
		if len(playercollide) > 0:
			if DEBUG: print("Hit player!")
			player.health -= 1

	render() # waiting is done in render
	tick = tick % 3000 + 1 # avoid overflow


# tidy up and quit
if DEBUG: print("quitting pygame")
pygame.quit()
if DEBUG: print("terminating process")
sys.exit()

