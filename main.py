from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.utils import platform
import json
import os
from datetime import datetime

if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])


class ItemCard(BoxLayout):
    """单个物品卡片组件"""
    def __init__(self, item_data, delete_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 150
        self.padding = 10
        self.spacing = 10
        
        self.item_data = item_data
        self.delete_callback = delete_callback
        
        # 图片
        img = Image(source=item_data['image_path'], size_hint_x=0.3)
        self.add_widget(img)
        
        # 信息区域
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.5)
        info_layout.add_widget(Label(
            text=f"时间: {item_data['timestamp']}", 
            size_hint_y=0.5,
            halign='left',
            valign='middle'
        ))
        info_layout.add_widget(Label(
            text=f"ID: {item_data['id'][:8]}", 
            size_hint_y=0.5,
            halign='left',
            valign='middle'
        ))
        self.add_widget(info_layout)
        
        # 删除按钮
        delete_btn = Button(
            text='删除',
            size_hint_x=0.2,
            background_color=(1, 0.3, 0.3, 1)
        )
        delete_btn.bind(on_press=self.confirm_delete)
        self.add_widget(delete_btn)
    
    def confirm_delete(self, instance):
        """确认删除对话框"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text='确定要删除这个物品吗？'))
        
        btn_layout = BoxLayout(size_hint_y=0.3, spacing=10)
        
        popup = Popup(title='确认删除', content=content, size_hint=(0.8, 0.4))
        
        confirm_btn = Button(text='确定', background_color=(1, 0.3, 0.3, 1))
        cancel_btn = Button(text='取消')
        
        confirm_btn.bind(on_press=lambda x: self.delete_item(popup))
        cancel_btn.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(confirm_btn)
        content.add_widget(btn_layout)
        
        popup.open()
    
    def delete_item(self, popup):
        """执行删除"""
        popup.dismiss()
        self.delete_callback(self.item_data['id'])


class ItemTrackerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_file = None
        self.images_dir = None
        self.items = []
    
    def build(self):
        """构建应用界面"""
        # 设置数据存储路径
        if platform == 'android':
            from android.storage import app_storage_path
            self.data_dir = app_storage_path()
        else:
            self.data_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.data_file = os.path.join(self.data_dir, 'items_data.json')
        self.images_dir = os.path.join(self.data_dir, 'item_images')
        
        # 创建图片目录
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
        
        # 加载数据
        self.load_data()
        
        # 主布局
        main_layout = BoxLayout(orientation='vertical')
        
        # 顶部按钮
        top_layout = BoxLayout(size_hint_y=0.1, padding=10, spacing=10)
        
        camera_btn = Button(
            text='📷 拍照记录',
            background_color=(0.2, 0.6, 1, 1),
            font_size='20sp'
        )
        camera_btn.bind(on_press=self.take_photo)
        
        refresh_btn = Button(
            text='🔄 刷新',
            background_color=(0.3, 0.7, 0.3, 1),
            size_hint_x=0.3,
            font_size='20sp'
        )
        refresh_btn.bind(on_press=self.refresh_list)
        
        top_layout.add_widget(camera_btn)
        top_layout.add_widget(refresh_btn)
        
        main_layout.add_widget(top_layout)
        
        # 物品列表
        self.scroll_view = ScrollView(size_hint=(1, 0.9))
        self.items_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        self.items_layout.bind(minimum_height=self.items_layout.setter('height'))
        
        self.scroll_view.add_widget(self.items_layout)
        main_layout.add_widget(self.scroll_view)
        
        # 显示物品列表
        self.display_items()
        
        return main_layout
    
    def take_photo(self, instance):
        """拍照功能"""
        if platform == 'android':
            from plyer import camera
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.join(self.images_dir, f'item_{timestamp}.jpg')
            
            try:
                camera.take_picture(filename=filepath, on_complete=self.on_photo_complete)
            except Exception as e:
                self.show_message('错误', f'拍照失败: {str(e)}')
        else:
            # 桌面测试：创建一个占位图片
            self.create_test_item()
    
    def on_photo_complete(self, filepath):
        """拍照完成回调"""
        if filepath and os.path.exists(filepath):
            item_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            item = {
                'id': item_id,
                'image_path': filepath,
                'timestamp': timestamp
            }
            
            self.items.append(item)
            self.save_data()
            self.display_items()
            self.show_message('成功', '物品已记录！')
        else:
            self.show_message('错误', '拍照失败或已取消')
    
    def create_test_item(self):
        """创建测试物品（用于桌面测试）"""
        item_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 创建一个简单的占位图片路径
        filepath = os.path.join(self.images_dir, f'item_{item_id}.jpg')
        
        # 创建一个空白图片文件（实际应用中会是真实照片）
        try:
            from PIL import Image as PILImage
            img = PILImage.new('RGB', (300, 300), color=(73, 109, 137))
            img.save(filepath)
        except:
            # 如果PIL不可用，创建空文件
            with open(filepath, 'w') as f:
                f.write('')
        
        item = {
            'id': item_id,
            'image_path': filepath,
            'timestamp': timestamp
        }
        
        self.items.append(item)
        self.save_data()
        self.display_items()
        self.show_message('成功', '测试物品已添加！')
    
    def display_items(self):
        """显示物品列表"""
        self.items_layout.clear_widgets()
        
        if not self.items:
            self.items_layout.add_widget(Label(
                text='暂无记录\n点击"拍照记录"添加物品',
                size_hint_y=None,
                height=100
            ))
            return
        
        # 按时间倒序排序
        sorted_items = sorted(self.items, key=lambda x: x['timestamp'], reverse=True)
        
        for item in sorted_items:
            if os.path.exists(item['image_path']):
                card = ItemCard(item, self.delete_item)
                self.items_layout.add_widget(card)
    
    def delete_item(self, item_id):
        """删除物品"""
        item_to_delete = None
        for item in self.items:
            if item['id'] == item_id:
                item_to_delete = item
                break
        
        if item_to_delete:
            # 删除图片文件
            if os.path.exists(item_to_delete['image_path']):
                try:
                    os.remove(item_to_delete['image_path'])
                except Exception as e:
                    print(f"删除图片失败: {e}")
            
            # 从列表中移除
            self.items.remove(item_to_delete)
            self.save_data()
            self.display_items()
            self.show_message('成功', '物品已删除！')
    
    def refresh_list(self, instance):
        """刷新列表"""
        self.load_data()
        self.display_items()
        self.show_message('提示', '列表已刷新！')
    
    def load_data(self):
        """加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.items = json.load(f)
            except Exception as e:
                print(f"加载数据失败: {e}")
                self.items = []
        else:
            self.items = []
    
    def save_data(self):
        """保存数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.items, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存数据失败: {e}")
    
    def show_message(self, title, message):
        """显示消息提示"""
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.3)
        )
        
        close_btn = Button(text='关闭', size_hint_y=0.3)
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()


if __name__ == '__main__':
    ItemTrackerApp().run()