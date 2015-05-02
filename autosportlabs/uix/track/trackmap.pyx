import kivy
import math
kivy.require('1.8.0')
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.graphics import Rectangle
from kivy.app import Builder
from kivy.metrics import dp
from kivy.graphics import Color, Line
from autosportlabs.racecapture.geo.geopoint import GeoPoint
from utils import *

Builder.load_file('autosportlabs/uix/track/trackmap.kv')

cdef class Point:
    cdef public float x
    cdef public float y
    def __init__(self, x, y):
        self.x = x
        self.y = y

cdef _render_track(object track_color, object canvas, list points, int height, int left, int bottom, float trackWidthScale, float globalRatio, float heightPadding, float widthPadding):
        cdef list linePoints = []
        cdef object point
        cdef object scaledPoint
        cdef int adjustedX
        cdef int adjustedY
        for point in points:
            adjustedX = int((widthPadding + (point.x * globalRatio))) + left
            #need to invert the Y since 0,0 starts at top left
            adjustedY = int((heightPadding + (point.y * globalRatio))) + bottom
            scaledPoint = Point(adjustedX, adjustedY)
            linePoints.append(scaledPoint.x)
            linePoints.append(scaledPoint.y)
        
        with canvas:
            Color(*track_color)
            Line(points=linePoints, width=dp(trackWidthScale * height), closed=True)        

cdef _gen_map_points(object geoPoints):
    cdef list points = []
    
    # min and max coordinates, used in the computation below
    cdef object minXY = Point(-1, -1)
    cdef object maxXY = Point(-1, -1)
    cdef object geoPoint
    cdef float latitude
    cdef float longitude
    cdef object point
    
    for geoPoint in geoPoints:
        latitude = geoPoint.latitude * float(math.pi / 180.0)
        longitude = geoPoint.longitude * float(math.pi / 180.0)
        point = Point(longitude, float(math.log(math.tan((math.pi / 4.0) + 0.5 * latitude))))
        
        minXY.x = point.x if minXY.x == -1 else min(minXY.x, point.x)
        minXY.y = point.y if minXY.y == -1 else min(minXY.y, point.y)
        points.append(point);
    
    # now, we need to keep track the max X and Y values
    for point in points:
        point.x = point.x - minXY.x
        point.y = point.y - minXY.y
        maxXY.x = point.x if maxXY.x == -1 else max(maxXY.x, point.x)
        maxXY.y = point.y if maxXY.y == -1 else max(maxXY.y, point.y);
            
    return minXY, maxXY, points
       
class TrackMap(Widget):
    trackColor = (1.0, 1.0, 1.0, 0.5)    
    trackWidthScale =0.01
    MIN_PADDING = dp(1)
    offsetPoint = Point(0,0)
    
    mapPoints = []
    minXY = Point(-1, -1)
    maxXY = Point(-1, -1)
    
    def set_trackColor(self, color):
        self.trackColor = color
        self.update_map()
        
    def get_trackColor(self):
        return self.trackColor
        
    trackColor = property(get_trackColor, set_trackColor)

    def __init__(self, **kwargs):
        super(TrackMap, self).__init__(**kwargs)
        self.bind(pos=self.update_map)
        self.bind(size=self.update_map)

    def update_map(self, *args):
        self.canvas.clear()
        
        paddingBothSides = self.MIN_PADDING * 2
        
        width = self.size[0] 
        height = self.size[1]
        
        left = self.pos[0]
        bottom = self.pos[1]
        
        # the actual drawing space for the map on the image
        mapWidth = width - paddingBothSides;
        mapHeight = height - paddingBothSides;

        #determine the width and height ratio because we need to magnify the map to fit into the given image dimension
        mapWidthRatio = float(mapWidth) / float(self.maxXY.x)
        mapHeightRatio = float(mapHeight) / float(self.maxXY.y)

        # using different ratios for width and height will cause the map to be stretched. So, we have to determine
        # the global ratio that will perfectly fit into the given image dimension
        self.globalRatio = min(mapWidthRatio, mapHeightRatio);

        #now we need to readjust the padding to ensure the map is always drawn on the center of the given image dimension
        self.heightPadding = (height - (self.globalRatio * self.maxXY.y)) / 2.0
        self.widthPadding = (width - (self.globalRatio * self.maxXY.x)) / 2.0
        self.offsetPoint = self.minXY;
        
        _render_track(self.trackColor, self.canvas, self.mapPoints, self.height, left, bottom, self.trackWidthScale, self.globalRatio, self.heightPadding, self.widthPadding)
        
        
    def setTrackPoints(self, geoPoints):
        self.genMapPoints(geoPoints)
        self.update_map()
        
    def genMapPoints(self, geoPoints):
        self.minXY, self.maxXY, self.mapPoints = _gen_map_points(geoPoints)


