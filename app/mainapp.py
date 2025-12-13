import os
from datetime import datetime
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.utils import platform
from kivy.properties import ListProperty, StringProperty
from kivy.clock import Clock

from .camera_handler import AndroidCamera
from .database import Database
from .widgets import PhotoItem

# 加载KV文件
Builder.load_string('''
<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        spacing: '10dp'
        padding: '10dp'
        
        Label:
            text: '拍照时间线'
            font_name: app.font_path
            font_size: '24sp'
            size_hint_y: 0.1
            halign: 'center'
            
        Button:
            text: '拍照'
            font_name: app.font_path
            font_size: '18sp'
            size_hint_y: 0.1
            on_press: root.take_photo()
            background_color: 0.2, 0.6, 1, 1
            
        ScrollView:
            GridLayout:
                id: photo_grid
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: '10dp'
                padding: '5dp'
                
<PhotoItemWidget>:
    orientation: 'horizontal'
    size_hint_y: None
    height: '120dp'
    padding: '10dp'
    spacing: '10dp'
    
    canvas.before:
        Color:
            rgba: 0.95, 0.95, 0.95, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [15]
    
    AsyncImage:
        id: thumbnail
        size_hint: None, 1
        width: self.height
        source: ''
        allow_stretch: True
    
    BoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.7
        
        Label:
            id: time_label
            text: ''
            font_name: app.font_path
            font_size: '16sp'
            size_hint_y: 0.5
            halign: 'left'
            valign: 'middle'
            text_size: self.width, None
            
        Label:
            id: duration_label
            text: ''
            font_name: app.font_path
            font_size: '14sp'
            size_hint_y: 0.5
            halign: 'left'
            valign: 'middle'
            text_size: self.width, None
            color: 0.3, 0.3, 0.3, 1
    
    Button:
        text: '删除'
        font_name: app.font_path
        font_size: '14sp'
        size_hint: None, None
        size: '80dp', '40dp'
        pos_hint: {'center_y': 0.5}
        on_press: root.delete_item()
        background_color: 1, 0.3, 0.3, 1
''')

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = AndroidCamera()
        self.db = Database()
        self.app = None
        
    def on_pre_enter(self):
        self.load_photos()
        
    def take_photo(self):
        if platform == 'android':
            self.camera.take_picture(self.photo_callback)
            
    def photo_callback(self, filepath):
        if filepath:
            # 保存到数据库
            photo_id = self.db.add_photo(filepath)
            # 重新加载照片列表
            self.load_photos()
            
    def load_photos(self):
        grid = self.ids.photo_grid
        grid.clear_widgets()
        
        photos = self.db.get_all_photos()
        for photo in photos:
            item = PhotoItem(
                photo_id=photo['id'],
                image_path=photo['filepath'],
                timestamp=photo['timestamp']
            )
            item.app = self.app
            grid.add_widget(item)
            
    def delete_photo(self, photo_id):
        if self.db.delete_photo(photo_id):
            self.load_photos()

class PhotoTimelineApp(App):
    font_path = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.CAMERA,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])
        
    def build(self):
        # 设置中文字体
        self.font_path = '/system/fonts/DroidSansFallback.ttf'
            
        # 创建屏幕管理器
        sm = ScreenManager()
        main_screen = MainScreen(name='main')
        main_screen.app = self
        sm.add_widget(main_screen)
        
        return sm
        
    def on_pause(self):
        return True
        
    def on_resume(self):
        pass