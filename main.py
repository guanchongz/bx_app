from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.properties import BooleanProperty, ListProperty, StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.core.window import Window
import os
import json
from datetime import datetime
import time

# Data storage file
DATA_FILE = 'items.json'

class ItemView(RecycleDataViewBehavior, BoxLayout):
    '''Custom view for each item in the list'''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['item_image'].source = data['image_path']
        self.ids['item_time'].text = data['timestamp']
        return super(ItemView, self).refresh_view_attrs(rv, index, data)
    
    def on_touch_down(self, touch):
        if super(ItemView, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)
    
    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected

class SelectableRecycleBoxLayout(FocusBehavior, RecycleBoxLayout):
    '''Adds selection and focus behavior to the view'''

class ItemList(RecycleView):
    def __init__(self, **kwargs):
        super(ItemList, self).__init__(**kwargs)
        self.data = []
        self.load_items()
    
    def load_items(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                items = json.load(f)
            # Sort by timestamp (newest first)
            items.sort(key=lambda x: x['timestamp'], reverse=True)
            self.data = items
        else:
            self.data = []
    
    def delete_item(self, index):
        if 0 <= index < len(self.data):
            item = self.data[index]
            # Remove image file
            if os.path.exists(item['image_path']):
                os.remove(item['image_path'])
            # Remove from data
            del self.data[index]
            # Save updated data
            with open(DATA_FILE, 'w') as f:
                json.dump(self.data, f)
            # Refresh view
            self.refresh_from_data()

class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super(CameraScreen, self).__init__(**kwargs)
        self.camera = Camera(play=True, resolution=(640, 480))
        self.add_widget(self.camera)
        
        # Layout for buttons
        layout = BoxLayout(orientation='vertical', size_hint=(1, 0.2), pos_hint={'top': 1})
        capture_btn = Button(text='Capture', size_hint=(1, 0.5))
        capture_btn.bind(on_press=self.capture)
        back_btn = Button(text='Back to List', size_hint=(1, 0.5))
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(capture_btn)
        layout.add_widget(back_btn)
        self.add_widget(layout)
    
    def capture(self, instance):
        # Capture image
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        filename = f'item_{int(time.time())}.png'
        self.camera.export_to_png(filename)
        
        # Save to data
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                items = json.load(f)
        else:
            items = []
        
        items.append({'image_path': filename, 'timestamp': timestamp})
        with open(DATA_FILE, 'w') as f:
            json.dump(items, f)
        
        # Go back to list
        self.manager.current = 'list'
        self.manager.get_screen('list').ids.item_list.load_items()
    
    def go_back(self, instance):
        self.manager.current = 'list'

class ListScreen(Screen):
    def __init__(self, **kwargs):
        super(ListScreen, self).__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical')
        
        # Button to go to camera
        camera_btn = Button(text='Take Photo', size_hint=(1, 0.1))
        camera_btn.bind(on_press=self.go_to_camera)
        layout.add_widget(camera_btn)
        
        # RecycleView for items
        self.item_list = ItemList()
        layout.add_widget(self.item_list)
        
        # Delete button
        delete_btn = Button(text='Delete Selected', size_hint=(1, 0.1))
        delete_btn.bind(on_press=self.delete_selected)
        layout.add_widget(delete_btn)
        
        self.add_widget(layout)
    
    def go_to_camera(self, instance):
        self.manager.current = 'camera'
    
    def delete_selected(self, instance):
        # Find selected items and delete them
        to_delete = []
        for i, item in enumerate(self.item_list.data):
            if hasattr(self.item_list.children[0].children[i], 'selected') and self.item_list.children[0].children[i].selected:
                to_delete.append(i)
        
        # Delete in reverse order to maintain indices
        for i in sorted(to_delete, reverse=True):
            self.item_list.delete_item(i)

class ItemApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ListScreen(name='list'))
        sm.add_widget(CameraScreen(name='camera'))
        return sm

if __name__ == '__main__':
    ItemApp().run()