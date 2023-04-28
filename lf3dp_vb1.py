import pyxel
import math
import random

from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
Circle = namedtuple('Circle', ['center', 'radius'])

class LineSegment:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def get_start(self):
        return self.start

    def get_end(self):
        return self.end

    def get_point(self, t):
        return Point(self.start.x + t*(self.end.x-self.start.x), self.start.y + t*(self.end.y-self.start.y))

class Utils:
    def get_distance(point1, point2):
        return math.sqrt((point1.x-point2.x)**2 + (point1.y-point2.y)**2)

class Printer:
    def __init__(self, circle_center_point, laser_points, circle_radius, circle_color):
        self.circle_center_point = circle_center_point
        self.screen_center_point = Point(pyxel.width/2, pyxel.height/2)
        self.laser_points = laser_points
        self.laser_point = circle_center_point
        self.circle_radius = circle_radius
        self.circle_color = circle_color

        # circle
        self.circle = []
        self.circle_angle = 0.0
        self.circle_finish = False

        # laser line
        self.laser_line_color = pyxel.COLOR_WHITE
        self.laser_line = []

    def get_finish_status(self):
        return self.circle_finish

    def get_circle(self):
        return self.circle

    def update(self):
        draw_speed = 0.1
        screen_dist = 100
        to_center = LineSegment(Point(self.circle_center_point.x+self.circle_radius*math.cos(self.circle_angle), self.circle_center_point.y), self.screen_center_point)
        circle_point = to_center.get_point(self.circle_radius*math.sin(self.circle_angle)/screen_dist)
        if not (circle_point.x < 0 or circle_point.x > pyxel.width or circle_point.y < 0 or circle_point.y > pyxel.height):
            self.circle.append(circle_point)
        self.laser_point = circle_point
        self.circle_angle += draw_speed
        if self.circle_angle > 2*math.pi:
            self.circle_angle = 0.0
            self.circle_finish = True

    def draw(self):
        if not self.circle_finish:
            for laser_point in self.laser_points:
                pyxel.line(laser_point.x, laser_point.y, self.laser_point.x, self.laser_point.y, self.laser_line_color)

class Painter:
    def __init__(self, color):
        self.painting = []
        self.painting_finished = False
        self.min_painting_num = 5
        self.printers = []
        self.painting_color = color
        self.printing_cnt = 0
        self.printing_finished = False
        self.final_painting = set()

    def get_finish_status(self):
        if len(self.painting) < self.min_painting_num:
            return False
        return self.painting_finished

    def update_painting(self, point):
        min_interval = 1
        if len(self.painting) >= 1:
            if self.painting[-1].x == point.x and self.painting[-1].y == point.y:
                return
            if len(self.painting) > self.min_painting_num and Utils.get_distance(self.painting[0], point) < 5:
                self.painting_finished = True
                self.painting.sort(key=lambda p: p.y, reverse=True)
                return
            if abs(self.painting[-1].y - point.y) > min_interval:
                if (self.painting[-1].y - point.y) > 0:
                    lower_point = point
                    higher_point = self.painting[-1]
                else:
                    lower_point = self.painting[-1]
                    higher_point = point
                for i in range(lower_point.y, higher_point.y, min_interval):
                    line = LineSegment(lower_point, higher_point)
                    ratio = (i-lower_point.y) / (higher_point.y-lower_point.y)
                    self.painting.append(line.get_point(ratio))
        self.painting.append(point)

    def update_printers(self, laser_points):
            if self.printing_cnt < len(self.painting) - 1:
                if self.painting[self.printing_cnt].y == self.painting[self.printing_cnt+1].y:
                    circle_center_point = Point((self.painting[self.printing_cnt].x+self.painting[self.printing_cnt+1].x)/2,self.painting[self.printing_cnt].y)
                    circle_radius = Utils.get_distance(self.painting[self.printing_cnt], self.painting[self.printing_cnt+1])/2.0
                    self.printers.append(Printer(circle_center_point, laser_points, circle_radius, self.painting_color))
                    self.printing_cnt += 2
                else:
                    self.printing_cnt += 1

            for printer in self.printers:
                printer.update()

            if self.printing_cnt >= len(self.painting) - 1:
                for printer in self.printers:
                    if not printer.get_finish_status():
                        return
                self.printing_finished = True

    def update(self, point, laser_points):
        if not self.painting_finished:
            self.update_painting(point)
        elif not self.printing_finished:
            self.update_printers(laser_points)
        else:
            return

    def draw(self):
        if not self.printing_finished:
            for point in self.painting:
                pyxel.pset(point.x, point.y, self.painting_color)

        for printer in self.printers:
            if printer.get_finish_status():
                continue
            circle = printer.get_circle()
            for point in circle:
                self.final_painting.add(point)

        for point in self.final_painting:
            pyxel.pset(point.x, point.y, self.painting_color)

        for printer in self.printers:
            printer.draw()

class Laser:
    def __init__(self, point):
        self.center_point = point

        self.laser_num = 4
        self.laser_color = []
        color_choice = [pyxel.COLOR_LIME, pyxel.COLOR_GREEN]
        for i in range(self.laser_num):
            self.laser_color.append(random.choice(color_choice))

        self.laser_radius = []
        for i in range(self.laser_num):
            self.laser_radius.append(random.randint(10, 15))

        self.laser_angle = []
        for i in range(self.laser_num):
            self.laser_angle.append(random.random()*math.pi/self.laser_num+i*math.pi/self.laser_num)

        self.laser_speed = []
        for i in range(self.laser_num):
            self.laser_speed.append(random.randint(1, 2)/10)

    def update(self):
        for i in range(self.laser_num):
            self.laser_angle[i] = (self.laser_angle[i] + self.laser_speed[i]) % (2*math.pi)

    def draw(self):
        for i in range(self.laser_num):
            laser_line_1 = self.get_laser_line(self.laser_radius[i], self.laser_angle[i])
            laser_line_2 = self.get_laser_line(self.laser_radius[i], self.laser_angle[i]+math.pi)
            pyxel.line(laser_line_1.get_start().x+self.center_point.x, laser_line_1.get_start().y+self.center_point.y, laser_line_1.get_end().x+self.center_point.x, laser_line_1.get_end().y+self.center_point.y, self.laser_color[i])
            pyxel.line(laser_line_2.get_start().x+self.center_point.x, laser_line_2.get_start().y+self.center_point.y, laser_line_2.get_end().x+self.center_point.x, laser_line_2.get_end().y+self.center_point.y, self.laser_color[i])

    def get_laser_line(self, radius, angle):
        return LineSegment(Point(radius*math.cos(angle+math.pi), radius*math.sin(angle+math.pi)), Point(radius*math.cos(angle), radius*math.sin(angle)))

class Mouse:
    def __init__(self, point):
        self.center_point = point

        # cross
        self.cross_angle = 0
        self.cross_radius = 4
        self.cross_color = pyxel.COLOR_RED

        # thunder
        self.thunder_num = 5
        self.thunder_seg = []
        self.thunder_color = pyxel.COLOR_WHITE
        self.thunder_update_cnt = 3

    def update(self, color):
        # update cross
        self.cross_angle = (self.cross_angle + 0.1) % (2*math.pi)
        self.thunder_color = color

        # update thunder
        self.thunder_update_cnt -= 1
        if self.thunder_update_cnt > 0:
            return
        self.thunder_update_cnt = 3
        noise = 3
        mouse_point = Point(pyxel.mouse_x, pyxel.mouse_y)
        self.thunder_seg = [mouse_point]
        mouse_line = LineSegment(mouse_point, self.center_point)
        for i in range(self.thunder_num):
            point_on_line = mouse_line.get_point(random.random()/3+i/3)
            self.thunder_seg.append(Point(point_on_line.x+random.randint(-noise, noise), point_on_line.y+random.randint(-noise, noise)))
        self.thunder_seg.append(self.center_point)

    def draw(self):
        # draw thunder
        for i in range(len(self.thunder_seg)-1):
            pyxel.line(self.thunder_seg[i].x, self.thunder_seg[i].y, self.thunder_seg[i+1].x, self.thunder_seg[i+1].y, self.thunder_color)

        # draw cross
        cross_line_1 = self.get_cross_line(self.cross_radius, self.cross_angle)
        cross_line_2 = self.get_cross_line(self.cross_radius, self.cross_angle+math.pi/2)
        pyxel.line(cross_line_1.get_start().x+pyxel.mouse_x, cross_line_1.get_start().y+pyxel.mouse_y, cross_line_1.get_end().x+pyxel.mouse_x, cross_line_1.get_end().y+pyxel.mouse_y, self.cross_color)
        pyxel.line(cross_line_2.get_start().x+pyxel.mouse_x, cross_line_2.get_start().y+pyxel.mouse_y, cross_line_2.get_end().x+pyxel.mouse_x, cross_line_2.get_end().y+pyxel.mouse_y, self.cross_color)

    def get_cross_line(self, radius, angle):
        return LineSegment(Point(radius*math.cos(angle+math.pi), radius*math.sin(angle+math.pi)), Point(radius*math.cos(angle), radius*math.sin(angle)))

class LowFiThreeDPrinter:
    def __init__(self):
        self.win_width = 480
        self.win_height = 320
        pyxel.init(self.win_width, self.win_height, title="Low-Fi 3D Printer")
        self.screen_color = 0

        # mouse and laser
        pyxel.mouse(False)
        self.mouse_num = 2
        self.mouse = []
        self.laser = []
        self.laser_points = []
        for i in range(self.mouse_num):
            if random.random() >= 0.0:
                laser_point = Point(random.randint(0, self.win_width), 0)
            elif random.random() >= 0.5:
                laser_point = Point(0, random.randint(0, self.win_height))
            elif random.random() >= 0.25:
                laser_point = Point(random.randint(0, self.win_width), self.win_height)
            else:
                laser_point = Point(self.win_width, random.randint(0, self.win_height))
            self.laser_points.append(laser_point)
            self.mouse.append(Mouse(laser_point))
            self.laser.append(Laser(laser_point))

        self.hide_mouse = False

        # painter
        self.painters = []
        self.ready_to_paint = True
        self.painter_color = 1

        pyxel.run(self.update, self.draw)

    def update(self):
        # monitor button status
        if pyxel.btnp(pyxel.KEY_A):
            self.painter_color = (self.painter_color + 1) % 16
        elif pyxel.btnp(pyxel.KEY_D):
            self.painter_color = (self.painter_color - 1) % 16
            if self.painter_color < 0:
                self.painter_color = 15

        if pyxel.btn(pyxel.KEY_S):
            self.screen_color = (self.screen_color + 1) % 16
        elif pyxel.btn(pyxel.KEY_W):
            self.screen_color = (self.screen_color - 1) % 16
            if self.screen_color < 0:
                self.screen_color = 15

        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            if len(self.painters) == 0:
                self.painters.append(Painter(self.painter_color))
            else:
                if self.painters[-1].get_finish_status():
                    self.painters.append(Painter(self.painter_color))
        else:
            if len(self.painters) > 0:
                if not self.painters[-1].get_finish_status():
                    self.painters.pop(-1)

        if pyxel.btnp(pyxel.KEY_H):
            self.hide_mouse = not self.hide_mouse

        if pyxel.btnp(pyxel.KEY_R):
            if len(self.painters) > 0:
                self.painters.pop(-1)

        if pyxel.btnp(pyxel.KEY_C):
            self.painters = []

        # update
        for i in range(self.mouse_num):
            self.mouse[i].update(self.painter_color)
            self.laser[i].update()

        for painter in self.painters:
            painter.update(Point(pyxel.mouse_x, pyxel.mouse_y), self.laser_points)

    def draw(self):
        pyxel.cls(self.screen_color)

        for painter in self.painters:
            painter.draw()

        if not self.hide_mouse:
            for i in range(self.mouse_num):
                self.mouse[i].draw()
                self.laser[i].draw()

LowFiThreeDPrinter()
