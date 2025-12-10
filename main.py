import os
import json
import time
from datetime import datetime
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineAvatarIconListItem, IconRightWidget
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.utils import platform

# KV 布局语言
KV = '''
ScreenManager:
    HomeScreen:
    CameraScreen:

<HomeScreen>:
    name: 'home'
    MDBoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: "物品记录"
            right_action_items: [["camera", lambda x: app.switch_to_camera()]]

        MDRecycleView:
            id: rv
            viewclass: 'ItemWidget'
            RecycleBoxLayout:
                default_size: None, dp(72)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'

<CameraScreen>:
    name: 'camera'
    MDBoxLayout:
        orientation: 'vertical'
        
        Camera:
            id: camera
            resolution: (640, 480)
            play: False
            allow_stretch: True
        
        MDBoxLayout:
            size_hint_y: None
            height: dp(60)
            padding: dp(10)
            spacing: dp(10)
            
            MDRaisedButton:
                text: "取消"
                on_release: app.switch_to_home()
            
            MDFillRoundFlatButton:
                text: "拍照并保存"
                size_hint_x: 1
                on_release: app.capture_photo()

<ItemWidget>:
    IconRightWidget:
        icon: "trash-can"
        on_release: root.delete_item(root)
'''

class ItemWidget(TwoLineAvatarIconListItem):
    def delete_item(self, widget):
        # 调用 App 类中的删除方法
        app = MDApp.get_running_app()
        app.delete_record(self.text) # text 存储的是时间戳字符串作为ID

class HomeScreen(Screen):
    pass

class CameraScreen(Screen):
    pass

class PhotoLogApp(MDApp):
    def build(self):
        self.title = "Photo Log"
        # 数据存储路径
        self.data_dir = self.user_data_dir
        self.json_file = os.path.join(self.data_dir, 'data.json')
        self.records = []
        return Builder.load_string(KV)

    def on_start(self):
        # 请求 Android 权限 (相机)
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
        
        self.load_records()

    def switch_to_camera(self):
        self.root.current = 'camera'
        self.root.get_screen('camera').ids.camera.play = True

    def switch_to_home(self):
        self.root.get_screen('camera').ids.camera.play = False
        self.root.current = 'home'

    def capture_photo(self):
        camera = self.root.get_screen('camera').ids.camera
        timestr = time.strftime("%Y%m%d_%H%M%S")
        filename = f"IMG_{timestr}.png"
        filepath = os.path.join(self.data_dir, filename)
        
        # 保存图片
        camera.export_to_png(filepath)
        
        # 保存记录
        record = {
            "time_display": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "filename": filename,
            "filepath": filepath,
            "id": timestr
        }
        self.records.insert(0, record) # 插入到最前面
        self.save_records()
        self.refresh_list()
        self.switch_to_home()

    def delete_record(self, time_display):
        # 查找并删除
        record_to_remove = None
        for rec in self.records:
            if rec['time_display'] == time_display:
                record_to_remove = rec
                break
        
        if record_to_remove:
            # 删除物理文件
            if os.path.exists(record_to_remove['filepath']):
                try:
                    os.remove(record_to_remove['filepath'])
                except:
                    pass
            self.records.remove(record_to_remove)
            self.save_records()
            self.refresh_list()

    def load_records(self):
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r') as f:
                self.records = json.load(f)
        # 按时间倒序排序
        self.records.sort(key=lambda x: x['id'], reverse=True)
        self.refresh_list()

    def save_records(self):
        with open(self.json_file, 'w') as f:
            json.dump(self.records, f)

    def refresh_list(self):
        data = []
        for rec in self.records:
            data.append({
                "text": rec['time_display'],
                "secondary_text": rec['filename']
            })
        self.root.get_screen('home').ids.rv.data = data

if __name__ == '__main__':
    PhotoLogApp().run()