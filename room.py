#!/usr/bin/python
#-*- coding:utf-8 -*-
import copy
from PIL import Image, ImageDraw, ImageFont
from sympy import Polygon, Ray, Line, Segment, Point


class Model(object):
    """模型类"""

    boundary = [0, 0, 0, 0]
    # directions = []
    direction = [1, 1]
    percent = 0

    def __init__(self, p):
        self.x = p[0]
        self.y = p[1]

    @property
    def point(self):
        return Point(self.x, self.y)

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y

    @staticmethod
    def loadString(dataString):
        # print eval(dataString)
        return [Model(p) for p in eval(dataString)]

class Ordered_Segment(Segment):
    """有序线段类，Segment中的构造点顺序不可预知"""

    def __init__(self, p1, p2):
        super(Ordered_Segment, self).__init__(p1, p2)

        if self.p1 == p1:
            self.reversed = False
        else:
            self.reversed = True

    @property
    def op1(self):
        if self.reversed:
            return self.p2
        else:
            return self.p1

    @property
    def op2(self):
        if self.reversed:
            return self.p1
        else:
            return self.p2

class RaySegments(object):
    """射线线段集合类"""
    def __init__(self, segments):

        self.segments = segments
        self.segLength = [seg.length for seg in segments]
        self.segValidation = [True] * len(segments)
        # self.sumLength = sum(self.segLength)

    def _linearIntersection(self, p1, p2, p):
        """线性插值"""
        f = lambda x1,x2,p:(x2-x1)*p / 100.0 + x1
        return Point(f(p1.x, p2.x, p), f(p1.y, p2.y, p))

    def getPointByPercent(self, percent):
        """根据百分比来获取segments上的点"""

        result = None
        sumLength = sum([self.segLength[i] for i in range(len(self.segments)) if self.segValidation[i]])
        target_length = sumLength * percent / 100.0
        for i in range(len(self.segments)):
            if not self.segValidation[i]:
                continue
            if target_length <= self.segLength[i]:
                p = target_length / self.segLength[i] * 100
                result = self._linearIntersection(self.segments[i].op1, self.segments[i].op2, p)
                break
            else:
                target_length -= self.segLength[i]

        return result

    def getPercentByPoint(self, point):
        """根据点来获取在射线线段上的百分比"""
        percent = 0
        sumLength = sum([self.segLength[i] for i in range(len(self.segments)) if self.segValidation[i]])

        # f = lambda x: (int(x.x),int(x.y))

        for i in range(len(self.segments)):
            if not self.segValidation[i]:
                continue
            if self.segments[i].contains(point):
                # print f(self.segments[i].op1), f(point), f(self.segments[i].op2), int(sumLength)
                percent += Ordered_Segment(self.segments[i].op1, point).length / sumLength * 100
                break
            else:
                percent += self.segments[i].length / sumLength * 100

        return round(percent, 1)


class Room(object):

    im = None       #原始图
    imp = None      #模型图
    impm = None     #模型射线图
    models = []
    image_size = (300, 300)
    intersection_dict = {}
    intersection_segment_dict = {}

    def __init__(self, room_points, image_size = (300, 300)):
        self.room_points = [Point(p) for p in room_points]
        self.image_size = image_size

        self.room_polygon = Polygon(*room_points)

        assert isinstance(self.room_polygon, Polygon)

        self.centroid = self.room_polygon.centroid

        pd = 20
        xs, ys = zip(*room_points)
        self.min_x = min(xs)
        self.min_y = min(ys)
        self.max_x = max(xs)
        self.max_y = max(ys)

        self.midpoint = Point(sum(xs)/len(xs), sum(ys)/len(ys))
        self.midpoint = self.centroid

        width = self.max_x - self.min_x
        height = self.max_y - self.min_y

        longer = float(max([width, height]))

        scale = (self.image_size[0]-pd) / longer
        offset_x = (self.image_size[0] - width*scale)/2
        offset_y = (self.image_size[0] - height*scale)/2

        self.projectx = lambda x: int(offset_x + (x - self.min_x) * scale)
        self.projecty = lambda y: int(self.image_size[0] - offset_y - (y - self.min_y) * scale)

    def _local2scene(self, points):
        """将点从房间原始坐标系转换成绘图坐标系"""
        return [(self.projectx(p[0]), self.projecty(p[1])) for p in points]

    def _drawPoints(self, points, imdraw, width, color='red'):
        """绘制点"""
        scene_points = self._local2scene(points)

        f = lambda p:(p[0]-width,p[1]-width,p[0]+width, p[1]+width)

        for point in scene_points:
            imdraw.ellipse(f(point) ,fill=color)
            imdraw.arc(f(point), 0, 360,fill='black')

    def _drawLines(self, points, imdraw, width, color='black'):
        """绘制线段"""
        points = self._local2scene(points)
        imdraw.line(points, fill = color, width=width)

    def getImage(self):
        """获取房间原始的Image"""
        if self.im:
            return self.im

        self.im = Image.new('RGBA', self.image_size, 'white')
        points = self.room_points[:]
        points.append(points[0])

        imdraw = ImageDraw.Draw(self.im)
        self._drawLines(points, imdraw, 2, 'black')
        self._drawPoints([self.midpoint], imdraw, 2, 'green')

        r = lambda x:round(x, 2)

        imdraw.text((0,0),'%s'% r(self.max_y),fill='red')
        imdraw.text((10,self.image_size[1]-10),'%s' % r(self.min_x),fill='red')
        imdraw.text((0,self.image_size[1]-20),'%s' % r(self.min_y),fill='red')
        imdraw.text((self.image_size[0]-40, self.image_size[1]-10),'%s' % r(self.max_x),fill='red')
        return self.im

    def addModel(self, models, mode = 'override'):
        """向房间中添加Model类"""
        if mode == 'override':
            self.models = []

        self.models.extend(models)
        self.intersection_dict = {}

    def getImageWithModel(self):
        """在房间中绘制模型"""
        if not self.models:
            return self.im

        self.imp = copy.deepcopy(self.im)
        impdraw = ImageDraw.Draw(self.imp)
        self._drawPoints(self.models,impdraw, 4, 'red')
        return self.imp

    def _getIntersection(self, l1, l2):
        """计算l1与l2的交点"""
        return l1.intersection(l2)

    def _getIntersectionByDirection(self, direction):
        """给定方向，计算房间中心点方向上与房间的交点 并返回"""
        intersections = []

        direction_ray = Ray(self.midpoint, \
            (self.midpoint.x + direction.x, self.midpoint.y + direction.y))
        for wall_segment in self.room_polygon.sides:
            inters = self._getIntersection(direction_ray, wall_segment)
            if inters:
                intersections.extend(inters)
        return intersections

    def _getModelIntersection(self):
        """计算房间中所有模型的射线交点，结果存入intersection_dict"""
        if self.intersection_dict:
            return

        self.intersection_dict = {}
        for model in self.models:
            intersections = []
            model_ray = Ray(self.midpoint, model.point)
            for wall_segment in self.room_polygon.sides:
                inters = self._getIntersection(model_ray, wall_segment)
                if inters:
                    intersections.extend(inters)
            # print intersections
            self.intersection_dict[model.point] = \
                sorted(intersections, key=lambda x:Ordered_Segment(self.midpoint, x).length)
        # print self.intersection_dict

    def _getSegmentsByDirection(self, direction):
        """根据方向获取合法线段 返回RaySegments对象"""
        valid_segments = []
        last_point = self.midpoint
        for current_point in self._getIntersectionByDirection(direction):
            current_segment = Ordered_Segment(last_point, current_point)
            if self.room_polygon.encloses_point(current_segment.midpoint):
                # self._drawLines([last_point, current_point], impmdraw, 1,'blue')
                valid_segments.append(current_segment)
        raysegments = RaySegments(valid_segments)
        return raysegments

    def getPointByPercentDirection(self, percent, direction):
        """射线方向和百分比获取房间内的点"""
        raysegments = self._getSegmentsByDirection(direction)
        point = raysegments.getPointByPercent(percent)
        return point

    def getImageWithModelRay(self):
        """获取房间的模型射线图"""
        if not self.imp:
            return

        self._getModelIntersection()
        self.impm = copy.deepcopy(self.imp)
        impmdraw = ImageDraw.Draw(self.impm)
        # f = lambda x: (int(x.x),int(x.y))
        # print f(self.midpoint)
        for model in self.models:
            # print '123',[self.midpoint, self.intersection_dict[model][-1]]
            last_point = self.midpoint
            valid_segments = []

            for current_point in self.intersection_dict[model.point]:
                # print 'last,current', f(last_point),f(current_point)
                current_segment = Ordered_Segment(last_point, current_point)
                # print '1,2', f(current_segment.p1), f(current_segment.p2)
                if self.room_polygon.encloses_point(current_segment.midpoint):
                    self._drawLines([last_point, current_point], impmdraw, 1,'blue')
                    valid_segments.append(current_segment)
                last_point = current_point
            self.intersection_segment_dict[model.point] = RaySegments(valid_segments)
            percent = self.intersection_segment_dict[model.point].getPercentByPoint(model.point)
            # print percent
            model.direction = Ray(self.midpoint, model.point).direction
            model.percent = percent

            # print f(model.point)
            # print f(self.intersection_segment_dict[model.point].getPointByPercent(percent))
            # print f(self.intersection_segment_dict[model.point].segments[0].p1)
            # print f(self.intersection_segment_dict[model.point].segments[0].p2)
            self._drawPoints(self.intersection_dict[model.point], impmdraw, 2, 'green')
        return self.impm

    @staticmethod
    def loadData(data_string):
        try:
            data = eval(data_string)
            assert isinstance(data, list)
        except:
            return None
        if isinstance(data[0],(list, tuple)):
            pass
        elif isinstance(data[0],dict):
            data = [(each['x'], each['y']) for each in data]
        else:
            return None
        return Room(data)

    @staticmethod
    def emptyRoomImage():
        """返回空图"""
        return Image.new('RGBA', Room.image_size, 'white')
