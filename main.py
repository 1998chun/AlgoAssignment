import random
from math import *

from kivy.properties import NumericProperty, ObjectProperty, ListProperty, AliasProperty, BooleanProperty, StringProperty
from kivy.app import App
from kivy.clock import Clock

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout


from kivy.graphics import Color, Line
from kivy.graphics.transformation import Matrix
from kivy.graphics.context_instructions import Translate, Scale

from kivy.garden.mapview import MapView, MapMarker, MapLayer#, MIN_LONGITUDE, MIN_LATITUDE, MAX_LATITUDE, MAX_LONGITUDE
from mapview.utils import clamp

MIN_LATITUDE = -90.
MAX_LATITUDE = 90.
MIN_LONGITUDE = -180.
MAX_LONGITUDE = 180.


class LineMapLayer(MapLayer):
    def __init__(self, **kwargs):
        super(LineMapLayer, self).__init__(**kwargs)
        self._coordinates = []
        self._line_points = None
        self._line_points_offset = (0, 0)
        self.zoom = 0

    @property
    def coordinates(self):
        return self._coordinates

    @coordinates.setter
    def coordinates(self, coordinates):
        self._coordinates = coordinates
        self.invalidate_line_points()
        self.clear_and_redraw()

    @property
    def line_points(self):
        if self._line_points is None:
            self.calc_line_points()
        return self._line_points

    @property
    def line_points_offset(self):
        if self._line_points is None:
            self.calc_line_points()
        return self._line_points_offset

    def calc_line_points(self):
        # Offset all points by the coordinates of the first point, to keep coordinates closer to zero.
        # (and therefore avoid some float precision issues when drawing lines)
        self._line_points_offset = (self.get_x(self.coordinates[0][1]), self.get_y(self.coordinates[0][0]))
        # Since lat is not a linear transform we must compute manually
        self._line_points = [(self.get_x(lon) - self._line_points_offset[0], self.get_y(lat) - self._line_points_offset[1]) for lat, lon in self.coordinates]

    def invalidate_line_points(self):
        self._line_points = None
        self._line_points_offset = (0, 0)

    def get_x(self, lon):
        '''Get the x position on the map using this map source's projection
        (0, 0) is located at the top left.
        '''
        return clamp(lon, MIN_LONGITUDE, MAX_LONGITUDE) * self.ms / 360.0

    def get_y(self, lat):
        '''Get the y position on the map using this map source's projection
        (0, 0) is located at the top left.
        '''
        lat = radians(clamp(-lat, MIN_LATITUDE, MAX_LATITUDE))
        return ((1.0 - log(tan(lat) + 1.0 / cos(lat)) / pi)) * self.ms / 2.0

    def reposition(self):
        mapview = self.parent
        print(mapview.zoom)
        # Must redraw when the zoom changes
        # as the scatter transform resets for the new tiles
        if (True):#self.zoom != mapview.zoom):
            map_source = mapview.map_source
            self.ms = pow(2.0, mapview.zoom) * map_source.dp_tile_size
            self.invalidate_line_points()
            self.clear_and_redraw()

    def clear_and_redraw(self, *args):
        with self.canvas:
            # Clear old line
            self.canvas.clear()

        # FIXME: Why is 0.05 a good value here? Why does 0 leave us with weird offsets?
        Clock.schedule_once(self._draw_line, 0.05)

    def _draw_line(self, *args):
        mapview = self.parent
        self.zoom = mapview.zoom
        
        # When zooming we must undo the current scatter transform
        # or the animation distorts it
        scatter = mapview._scatter
        sx, sy, ss = scatter.x, scatter.y, scatter.scale

        # Account for map source tile size and mapview zoom
        vx, vy, vs = mapview.viewport_pos[0], mapview.viewport_pos[1], mapview.scale

        with self.canvas:
            # Clear old line
            self.canvas.clear()

            # Offset by the MapView's position in the window
            Translate(*mapview.pos)

            # Undo the scatter animation transform
            Scale(1 / ss, 1 / ss, 1)
            Translate(-sx, -sy)

            # Apply the get window xy from transforms
            Scale(vs, vs, 1)
            Translate(-vx, -vy)

            # Apply the what we can factor out of the mapsource long, lat to x, y conversion
            Translate(self.ms / 2, 0)

            # Translate by the offset of the line points (this keeps the points closer to the origin)
            Translate(*self.line_points_offset)

            # Draw line
            Color(0, 0.2, 0.7, 0.25)
            Line(points=self.line_points, width=6.5 / 2)
            Color(0, 0.2, 0.7, 1)
            Line(points=self.line_points, width=6 / 2)
            Color(0, 0.3, 1, 1)
            Line(points=self.line_points, width=4 / 2)


class MapViewApp(App):
    mapview = None
 
    def __init__(self, **kwargs):
        super(MapViewApp, self).__init__(**kwargs)
        Clock.schedule_once(self.post, 0)
 
    def build(self):
        layout = BoxLayout(orientation='vertical')
        return layout
 
    def post(self, *args):
        layout = FloatLayout()
        self.mapview = MapView(zoom=9, lat=2.7456, lon=101.7072)
        #for l in locations:
        #    self.mapview.add_widget(MapMarker(lat=l['lat'], lon=l['lon']))
        line = LineMapLayer()
        self.mapview.add_layer(line, mode="scatter")  # window scatter
        layout.add_widget(self.mapview)
        
        self.root.add_widget(layout)
        b = BoxLayout(orientation='horizontal',height='32dp',size_hint_y=None)
        b.add_widget(Button(text="Zoom in",on_press=lambda a: setattr(self.mapview,'zoom',clamp(self.mapview.zoom+1, 0, 10))))
        b.add_widget(Button(text="Zoom out",on_press=lambda a: setattr(self.mapview,'zoom',clamp(self.mapview.zoom-1, 0, 10))))
        b.add_widget(Button(text="AddPoint",on_press=lambda a: line.add_point()))
        self.root.add_widget(b)


locations = {}
locations['Kuala Lumpur'] = {'lat':2.7456, 'lon':101.7072}
locations['Brasilia'] = {'lat':-15.8697, 'lon':-47.9172}
locations['Tokyo'] = {'lat':35.5494, 'lon':139.7798}
locations['London'] = {'lat':51.5048, 'lon':0.0495}
locations['New York'] = {'lat':40.6413, 'lon':-73.7781}
locations['Bangkok'] = {'lat':13.6900, 'lon':100.7501}
locations['Kabul'] = {'lat':34.5609, 'lon':69.2101}
locations['California'] = {'lat':33.6762, 'lon':-117.8675} # testing purpose
destinations = ['Kuala Lumpur', 'Brasilia', 'Tokyo', 'London', 'New York', 'Bangkok', 'Kabul', 'California']


class MainScreen(BoxLayout):

    def choose_destination(self, instance):
        self.destination = instance.text
        self.line.coordinates=[[2.7456, 101.7072], [locations[instance.text]['lat'], locations[instance.text]['lon']]]
        self.left_label.text = 'From Kuala Lumpur\nTo {}'.format(self.destination)

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.destination = 'Kuala Lumpur'
        
        left_layout = BoxLayout(orientation = 'vertical')
        self.left_label = Label(text='From Kuala Lumpur\nTo {}'.format(self.destination))
        left_layout.add_widget(self.left_label)
        for d in destinations:
            btn = Button(text=d)
            #btn.bind(state=self.choose_destination)
            btn.bind(on_press=self.choose_destination)
            left_layout.add_widget(btn)
        b = BoxLayout(orientation='horizontal',height='32dp',size_hint_y=None)
        b.add_widget(Button(text="Zoom in",on_press=lambda a: setattr(self.mapview,'zoom',clamp(self.mapview.zoom+1, 3, 10))))
        b.add_widget(Button(text="Zoom out",on_press=lambda a: setattr(self.mapview,'zoom',clamp(self.mapview.zoom-1, 3, 10))))
        left_layout.add_widget(b)
        self.add_widget(left_layout)
        
        self.mapview = MapView(zoom=8, lat=2.7456, lon=101.7072, size_hint=(1.8, 1))
        #self.mapview.add_widget(MapMarker(lat=2.7456, lon=101.7072))
        self.addMaker()
        self.add_widget(self.mapview)
        self.line.reposition()
        self.line.coordinates=[[2.7456, 101.7072], [2.7456, 101.7072]]
    
    def addMaker(self):
        for l in locations.keys():
            self.mapview.add_widget(MapMarker(lat=locations[l]['lat'], lon=locations[l]['lon']))
        self.line = LineMapLayer()
        self.mapview.add_layer(self.line, mode="scatter")


class MyApp(App):

    def build(self):
        return MainScreen()


if __name__ == '__main__':
    MyApp().run()
    #MapViewApp().run()
