#!/usr/bin/python
# -*- coding: utf-8 -*-

# programmiert von Matthias Büchse, Dresden
# nach einer Idee von Christian Kothe (aus Jugendtagen)
# Lizenz: LGPL oder sowas

import cProfile
import pstats
import pygame
import random
import math

(WIDTH, HEIGHT) = (640, 384)
WIDTH2 = WIDTH * 2
HEIGHT2 = HEIGHT * 2
WIDTHD2 = WIDTH // 2
HEIGHTD2 = HEIGHT // 2
ADJ_WIDTH = WIDTH // 128
ADJ_HEIGHT = HEIGHT // 128
BLACK, WHITE, YELLOW = (0, 0, 0), (255, 255, 255), (255, 255, 0)
COL0R = [(0, 0, 127), (127, 0, 0), (0, 127, 0), (127, 127, 0)]
COL1R = [(0, 0, 255), (255, 0, 0), (0, 255, 0), (255, 255, 0)]
OOPI = 1 / math.pi

screen = None
world = None
time = 0


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "(%6.2f, %6.2f)" % (self.x, self.y)

    def add(self, p):
        self.x += p.x
        self.y += p.y
        return self

    def add_radius(self, r):
        return Point(self.x + r, self.y + r)

    def copy(self):
        return Point(self.x, self.y)

    def norm_sq(self):
        return self.x * self.x + self.y * self.y

    def norm(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def scale(self, r):
        self.x *= r
        self.y *= r
        return self

    def scaled(self, r):
        return Point(self.x * r, self.y * r)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)


def from_polar(angle, length):
    return Point(length * math.cos(angle), length * math.sin(angle))


# "workaround" for pygame_cffi
def __test_circle(surface, color, pos, radius, width):
    pygame.draw.rect(surface, color, pygame.Rect(pos[0] - radius, pos[1] - radius, 2 * radius, 2 * radius), width)

# pygame.draw.circle = __test_circle


def circle(color, pos, r, w):
    pygame.draw.circle(screen, color, (int(2*pos.x), int(2*pos.y)), int(2*r), w)


def double_circle(color, color2, pos, r2):
    p = (int(2*pos.x), int(2*pos.y))
    r = int(2*r2)
    pygame.draw.circle(screen, color, p, r, 0)
    pygame.draw.circle(screen, color2, p, r, 1)

    if p[0] - r < 0:
        p1 = (p[0] + WIDTH2, p[1])
        pygame.draw.circle(screen, color, p1, r, 0)
        pygame.draw.circle(screen, color2, p1, r, 1)
        if p1[1] - r < 0:
            p2 = (p1[0], p1[1] + HEIGHT2)
            pygame.draw.circle(screen, color, p2, r, 0)
            pygame.draw.circle(screen, color2, p2, r, 1)
        elif p[1] + r > HEIGHT2:
            p2 = (p1[0], p1[1] - HEIGHT2)
            pygame.draw.circle(screen, color, p2, r, 0)
            pygame.draw.circle(screen, color2, p2, r, 1)
    elif p[0] + r > WIDTH2:
        p1 = (p[0] - WIDTH2, p[1])
        pygame.draw.circle(screen, color, p1, r, 0)
        pygame.draw.circle(screen, color2, p1, r, 1)
        if p1[1] - r < 0:
            p2 = (p1[0], p1[1] + HEIGHT2)
            pygame.draw.circle(screen, color, p2, r, 0)
            pygame.draw.circle(screen, color2, p2, r, 1)
        elif p[1] + r > HEIGHT2:
            p2 = (p1[0], p1[1] - HEIGHT2)
            pygame.draw.circle(screen, color, p2, r, 0)
            pygame.draw.circle(screen, color2, p2, r, 1)
    if p[1] - r < 0:
        p1 = (p[0], p[1] + HEIGHT2)
        pygame.draw.circle(screen, color, p1, r, 0)
        pygame.draw.circle(screen, color2, p1, r, 1)
    elif p[1] + r > HEIGHT2:
        p1 = (p[0], p[1] - HEIGHT2)
        pygame.draw.circle(screen, color, p1, r, 0)
        pygame.draw.circle(screen, color2, p1, r, 1)


class WorldElement(object):
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size


class Adjacent(object):
    def __init__(self, wes):
        self.s = [[[] for _ in range(0, ADJ_WIDTH)] for _ in range(0, ADJ_HEIGHT)]
        for we in wes:
            self.s[int(we.pos.y) // 128][int(we.pos.x) // 128].append(we)

    def get_elements(self, rij):
        s = self.s
        (ri, rj) = rij
        for i in ri:
            for j in rj:
                for l in s[i][j]:
                    yield l


def difference(p1, p2, p):
    x = p1.x - p2.x
    if x > WIDTHD2:
        x -= WIDTH
    if x < -WIDTHD2:
        x += WIDTH
    y = p1.y - p2.y
    if y > HEIGHTD2:
        y -= HEIGHT
    if y < -HEIGHTD2:
        y += HEIGHT
    p.x = x
    p.y = y


def restrict_point(p):
    """restricts p in place, but returns it also for chaining"""
    x = p.x
    while x > WIDTH:
        x -= WIDTH
    while x < 0:
        x += WIDTH
    p.x = x
    x = p.y
    while x > HEIGHT:
        x -= HEIGHT
    while x < 0:
        x += HEIGHT
    p.y = x
    return p


def compute_ranges(xy, r):
    xy1 = restrict_point(xy.add_radius(-r))
    xy2 = restrict_point(xy.add_radius(r))

    il = int(xy1.y) // 128
    ih = int(xy2.y) // 128
    if il <= ih:
        ri = range(il, ih + 1)
    else:
        # does not work
        # ri = itertools.chain(range(0, ih + 1), range(il, self.height // 128))
        ri = list(range(0, ih + 1)) + list(range(il, ADJ_HEIGHT))
    il = int(xy1.x) // 128
    ih = int(xy2.x) // 128
    if il <= ih:
        rj = range(il, ih + 1)
    else:
        # does not work
        # rj = itertools.chain(range(0, ih + 1), range(il, self.width // 128))
        rj = list(range(0, ih + 1)) + list(range(il, ADJ_WIDTH))

    return ri, rj


class World(object):
    """the stage"""

    def __init__(self):
        self.adjacent = None
        self.elements = set()
        self.nutris = list()
        self.gadgets = set()
        self.wdir = 0
        self.wforce = 0
        self.acc = None
        self.d = Point(0, 0)
        self.adder1 = list()
        self.remover1 = list()
        self.adder2 = list()
        self.remover2 = list()

    def tick(self, dt):
        self.adjacent = Adjacent(self.elements)
        self.acc = from_polar(self.wdir, self.wforce)
        self.wdir += (random.random() - 0.5) * dt * 0.01
        self.wforce += (random.random() - 0.5) * dt * 0.00000001

        self.elements.update(self.adder1)
        for e in self.remover1:
            self.elements.remove(e)
        self.gadgets.update(self.adder2)
        for e in self.remover2:
            self.gadgets.remove(e)

        del self.adder1[:]
        del self.remover1[:]
        del self.adder2[:]
        del self.remover2[:]

        for we in self.nutris:
            we.tick(dt)
        for we in self.elements:
            we.tick(dt)
        for we in self.gadgets:
            we.tick(dt)

    def draw(self):
        for we in self.nutris:
            pygame.draw.circle(screen, we.color, we.pos2, int(2 * math.sqrt(OOPI * we.size)), 0)
            # we.draw()
        for we in self.elements:
            we.draw()
        for we in self.gadgets:
            we.draw()

    def add_livator(self, el):
        self.adder1.append(el)

    def remove_livator(self, el):
        self.remover1.append(el)

    def add_nutri(self, el):
        self.nutris.append(el)

    def add_gadget(self, el):
        self.adder2.append(el)

    def remove_gadget(self, el):
        self.remover2.append(el)

    def get_livators(self, rij, xy, r):
        if rij is None:
            rij = compute_ranges(xy, r)
        return self.adjacent.get_elements(rij)


class Scanner(object):
    def __init__(self, interval=100, radius=60, rij=None):
        self.last_time = time - int(interval * random.random())
        self.interval = interval  # in ms
        self.radius = radius
        self.ls = []
        self.rij = rij

    def tick(self, pos):
        if time - self.last_time >= self.interval:
            self.last_time = time
            self.ls = list(world.get_livators(self.rij, pos, self.radius))
        return self.ls


scanners = {}


def make_scanner(radius, rij):
    repr_ = repr(rij)
    if repr_ in scanners:
        return scanners[repr_]
    else:
        sc = Scanner(200, radius, rij)
        scanners[repr_] = sc
        return sc


def get_elements_exact(ls, xy, r):
    d = world.d
    for livator in ls:
        # d = difference(l.xy, xy)
        difference(livator.pos, xy, d)
        br = r + livator.br
        if d.norm_sq() < br * br:
            yield livator


class Nutri(WorldElement):
    def __init__(self, pos, size=0):
        if size == 0:
            size = random.random() * 32.0 + 30.0
        super(Nutri, self).__init__(pos, size)
        c = int(random.random() * 32 + 32)
        self.color = (c, c, c)
        self.scanner = make_scanner(20, compute_ranges(pos, 20))
        self.pos2 = (int(2*self.pos.x), int(2*self.pos.y))
        self.ls = None
        self.last_time = time - 50

    def tick(self, dt):
        if time - self.last_time > 50:
            self.last_time = time
            self.ls = list(get_elements_exact(self.scanner.tick(None), self.pos, math.sqrt(OOPI * self.size)))
        l = len(self.ls)
        if l > 0:
            ds = min(self.size, dt * l / 4.0) / l
            for liv in self.ls:
                self.size -= liv.feed(ds)
        self.size += 0.0065 * dt  # / 128.0

    def draw(self):
        # do not use a dedicated function in order to save the call (yes, it makes a difference)
        # pygame.draw.circle(screen, self.color, self.pos2, int(2 * math.sqrt(OOPI * self.size)), 0)
        pass  # moved to World.draw in order to save a call (NO KIDDING)


class MovingWorldElement(WorldElement):
    def __init__(self, pos, size, vel):
        super(MovingWorldElement, self).__init__(restrict_point(pos), size)
        self.vel = vel.copy()


# possible further development:
# collect parameters in kind of a genome and incorporate mutations
# problem: the genome is hard to visualize
# even more so if we want to move away from teams towards species!
class Genome(object):
    missileTime = 2000
    accProbability = 0.25
    accDuration = 150
    splitSize = 1500
    maxSize = 2000


class Livator(MovingWorldElement):
    def __init__(self, team, pos, vel, size=314.0, gen=0):
        super(Livator, self).__init__(pos, size, vel)
        self.team = team
        self.acc = Point(0.0, 0.0)
        self.br = math.sqrt(OOPI * size)
        self.msl = 2000
        self.gen = gen
        self.born = time
        self.acc_stop = 0
        self.self_acc = None
        self.scanner = Scanner(100, 60)

    def tick(self, dt):
        # add aether currents or so
        self.vel.scale(0.999 ** dt).add((self.acc + world.acc).scale(dt))
        # compute new position
        restrict_point(self.pos.add(self.vel.scaled(dt)))
        # decrease missile timer
        self.msl -= dt
        # scan vicinity
        br = self.br = math.sqrt(OOPI * self.size)
        f = Point(0.0, 0.0)
        isclear = True
        target = None
        tdist = 100
        t = None
        d = world.d
        pos = self.pos
        for l in self.scanner.tick(pos):
            if l != self:
                difference(pos, l.pos, d)
                dnorm = max(br, d.norm())
                if dnorm < 2.5 * br:
                    isclear = False
                ood = 1 / dnorm
                d.scale(ood)
                f.add(d.scaled(ood * ood * l.size))
                if l.team != self.team and dnorm < tdist:
                    target = l
                    tdist = dnorm
                    t = d.copy()
        self.acc = f.scale(0.05 / self.size)

        if time < self.acc_stop:
            self.acc.add(self.self_acc)
            self.size *= 0.9999 ** dt
        elif random.random() > 0.75:
            self.acc_stop = time + random.random() * 150 + 50
            self.self_acc = from_polar(random.random() * 2 * math.pi, 0.0001)

        if target is not None and self.msl < 0 and self.size > 200:
            self.msl = 1500
            self.size -= 50
            world.add_gadget(Missile(self, target, t.scale(-1.15 * self.br).add(self.pos), self.vel))

        if self.size < 15 or time - self.born > 60000:  # max age 60 sec
            world.remove_livator(self)
        elif self.size > 1500 and isclear:
            world.remove_livator(self)
            d = from_polar(2 * math.pi * random.random(), 0.75 * self.br)
            world.add_livator(Livator(self.team, self.pos + d, self.vel, self.size * 0.4, self.gen + 1))
            world.add_livator(Livator(self.team, self.pos + d.scale(-1), self.vel, self.size * 0.4, self.gen + 1))

    def feed(self, ds):
        if self.size < 2000:
            self.size += ds
            return ds
        else:
            return 0

    def hit(self):
        self.size = max(self.size - 100, 10)

    def draw(self):
        (r0, g0, b0) = COL1R[self.team]
        gen = 10 ** (-(time - self.born) * 0.0000166)
        double_circle((int(r0 * gen), int(g0 * gen), int(b0 * gen)), COL1R[self.team], self.pos, self.br)


class Missile(MovingWorldElement):
    def __init__(self, source, target, pos, vel):
        super(Missile, self).__init__(pos, 12.6, vel)
        self.source = source
        self.target = target
        self.acc = Point(0, 0)
        self.scanner = Scanner(33, 65)

    def tick(self, dt):
        self.vel.scale(0.999 ** dt).add((self.acc + world.acc).scale(dt))
        restrict_point(self.pos.add(self.vel.scaled(dt)))
        ls = self.scanner.tick(self.pos)
        d = world.d
        pos = self.pos
        for l in ls:
            difference(l.pos, pos, d)
            dnorm = d.norm()
            if dnorm - l.br < 1:
                if l != self.source:  # new: intelligent weapons
                    l.hit()
                world.remove_gadget(self)
                break
            elif l == self.target:
                ood = 1 / dnorm
                self.acc = d.scaled(ood * 0.001)

    def draw(self):
        circle(WHITE, self.pos, 2, 0)


class Wind(MovingWorldElement):
    def __init__(self, pos):
        super(Wind, self).__init__(pos, 12.6, Point(0.0, 0.0))

    def tick(self, dt):
        self.vel.scale(0.999 ** dt).add(world.acc.scaled(dt))
        restrict_point(self.pos.add(self.vel.scaled(dt)))

    def draw(self):
        circle(YELLOW, self.pos, 2, 0)


def main():
    global screen, world, time
    profiling = False
    profile = cProfile.Profile()
    if profiling:
        profile.enable()

    pygame.init()
    screen = pygame.display.set_mode((WIDTH * 2, HEIGHT * 2))

    vel = Point(0.0, 0.0)

    clock = pygame.time.Clock()
    time = 0
    running = True
    while running:
        world = World()
        for x in range(0, WIDTH // 64):
            for y in range(0, HEIGHT // 64):
                if y % 3 == 1 and x % 5 == 1:
                    for _ in range(0, 4):
                        world.add_livator(
                            Livator(((x + y) // 3) % 4, Point(x * 64 + 64 * random.random(), y * 64 + 64 * random.random()), vel))
                for _ in range(0, 16):
                    world.add_nutri(Nutri(Point(x * 64 + random.random() * 64, y * 64 + random.random() * 64)))

        running2 = running
        paused = False
        step = False
        while running2:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = running2 = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = running2 = False
                    if event.key == pygame.K_RETURN:
                        running2 = False
                    if event.key == pygame.K_SPACE:
                        paused = not paused
                    if event.key == pygame.K_PERIOD:
                        paused = False
                        step = True
            dt = 1.0 * clock.tick(45)
            if not paused:
                time += dt
                world.tick(dt)
            if step:
                paused = True
                step = False
            screen.fill(BLACK)
            world.draw()
            pygame.display.flip()

    print(clock.get_fps())
    if profiling:
        profile.disable()
        stats = pstats.Stats(profile)
        stats.sort_stats('tottime')
        stats.print_stats()
    pygame.quit()

if __name__ == "__main__":
    main()
