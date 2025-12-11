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
from kivy.core.text import LabelBase
import json
import os
from datetime import datetime

# 注册中文字体
if platform == 'android':
    # Android 系统字体
    LabelBase.register(
        name='Roboto',
        fn_regular='/system/fonts/DroidSansFallback.ttf'
    )
    # 设置默认字体
    from kivy.config import Config
    Config.set('kivy', 'default_font', ['Roboto', 'data/fonts/DroidSansFallback.ttf'])

# Android 权限和 FileProvider
if platform == 'android':
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.CAMERA,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE
        ])
        
        from jnius import autoclass, cast
        
        # Android 类
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        FileProvider = autoclass('androidx.core.content.FileProvider')
        File = autoclass('java.io.File')
        Environment = autoclass('android.os.Environment')
        MediaStore = autoclass('android.provider.MediaStore')
        
    except Exception as e:
        print(f"Android 初始化失败: {e}")


class CameraHelper:
    """相机辅助类，处理 Android 文件 URI"""
    
    @staticmethod
    def get_file_uri(filepath):
        """获取文件的 Content URI（Android 7.0+）"""
        if platform != 'android':
            return filepath
        
        try:
            context = PythonActivity.mActivity
            file_obj = File(filepath)
            
            # 使用 FileProvider 获取 content:// URI
            authority = "org.example.itemtracker.fileprovider"
            uri = FileProvider.getUriForFile(context, authority, file_obj)
            return uri
        except Exception as e:
            print(f"获取文件 URI 失败: {e}")
            return None
    
    @staticmethod
    def take_picture(callback):
        """使用 Intent 拍照"""
        if platform != 'android':
            return None
        
        try:
            context = PythonActivity.mActivity
            
            # 创建图片文件
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pictures_dir = Environment.getExternalStoragePublicDirectory(
                Environment.DIRECTORY_PICTURES
            )
            app_dir = File(pictures_dir, "ItemTracker")
            if not app_dir.exists():
                app_dir.mkdirs()
            
            image_file = File(app_dir, f"item_{timestamp}.jpg")
            filepath = image_file.getAbsolutePath()
            
            # 获取 Content URI
            authority = "org.example.itemtracker.fileprovider"
            image_uri = FileProvider.getUriForFile(context, authority, image_file)
            
            # 创建拍照 Intent
            intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
            intent.putExtra(MediaStore.EXTRA_OUTPUT, image_uri)
            
            # 授予临时权限
            intent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            
            # 启动相机
            context.startActivityForResult(intent, 1)
            
            return filepath
            
        except Exception as e:
            print(f"拍照失败: {e}")
            return None


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
        try:
            img = Image(
                source=item_data['image_path'],
                size_hint_x=0.3,
                allow_stretch=True,
                keep_ratio=True
            )
        except Exception as e:
            print(f"加载图片失败: {e}")
            img = Label(text='[图片]', size_hint_x=0.3)
        
        self.add_widget(img)
        
        # 信息区域
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.5)
        
        time_label = Label(
            text=f"时间: {item_data['timestamp']}", 
            size_hint_y=0.5,
            halign='left',
            valign='middle',
            font_name='Roboto'  # 使用中文字体
        )
        time_label.bind(size=time_label.setter('text_size'))
        
        id_label = Label(
            text=f"ID: {item_data['id'][:8]}", 
            size_hint_y=0.5,
            halign='left',
            valign='middle',
            font_name='Roboto'
        )
        id_label.bind(size=id_label.setter('text_size'))
        
        info_layout.add_widget(time_label)
        info_layout.add_widget(id_label)
        self.add_widget(info_layout)
        
        # 删除按钮
        delete_btn = Button(
            text='删除',
            size_hint_x=0.2,
            background_color=(1, 0.3, 0.3, 1),
            font_name='Roboto'
        )
        delete_btn.bind(on_press=self.confirm_delete)
        self.add_widget(delete_btn)
    
    def confirm_delete(self, instance):
        """确认删除对话框"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        msg_label = Label(
            text='确定要删除这个物品吗？',
            font_name='Roboto'
        )
        content.add_widget(msg_label)
        
        btn_layout = BoxLayout(size_hint_y=0.3, spacing=10)
        
        popup = Popup(
            title='确认删除',
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        
        confirm_btn = Button(
            text='确定',
            background_color=(1, 0.3, 0.3, 1),
            font_name='Roboto'
        )
        cancel_btn = Button(
            text='取消',
            font_name='Roboto'
        )
        
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
        self.pending_photo_path = None
    
    def build(self):
        """构建应用界面"""
        # 设置数据存储路径
        self.setup_storage()
        
        # 加载数据
        self.load_data()
        
        # 主布局
        main_layout = BoxLayout(orientation='vertical')
        
        # 顶部按钮
        top_layout = BoxLayout(size_hint_y=0.1, padding=10, spacing=10)
        
        camera_btn = Button(
            text='拍照记录',
            background_color=(0.2, 0.6, 1, 1),
            font_size='18sp',
            font_name='Roboto'
        )
        camera_btn.bind(on_press=self.take_photo)
        
        refresh_btn = Button(
            text='刷新',
            background_color=(0.3, 0.7, 0.3, 1),
            size_hint_x=0.3,
            font_size='18sp',
            font_name='Roboto'
        )
        refresh_btn.bind(on_press=self.refresh_list)
        
        top_layout.add_widget(camera_btn)
        top_layout.add_widget(refresh_btn)
        
        main_layout.add_widget(top_layout)
        
        # 物品列表
        self.scroll_view = ScrollView(size_hint=(1, 0.9))
        self.items_layout = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=10
        )
        self.items_layout.bind(minimum_height=self.items_layout.setter('height'))
        
        self.scroll_view.add_widget(self.items_layout)
        main_layout.add_widget(self.scroll_view)
        
        # 显示物品列表
        self.display_items()
        
        # 监听 Activity 结果（用于接收拍照结果）
        if platform == 'android':
            try:
                PythonActivity.mActivity.bind(on_activity_result=self.on_activity_result)
            except:
                pass
        
        return main_layout
    
    def setup_storage(self):
        """设置存储路径"""
        if platform == 'android':
            try:
                from android.storage import app_storage_path
                self.data_dir = app_storage_path()
            except Exception as e:
                print(f"获取存储路径失败: {e}")
                # 使用公共目录
                pictures_dir = Environment.getExternalStoragePublicDirectory(
                    Environment.DIRECTORY_PICTURES
                )
                app_dir = File(pictures_dir, "ItemTracker")
                if not app_dir.exists():
                    app_dir.mkdirs()
                self.data_dir = app_dir.getAbsolutePath()
        else:
            self.data_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.data_file = os.path.join(self.data_dir, 'items_data.json')
        self.images_dir = self.data_dir
        
        # 创建目录
        try:
            if not os.path.exists(self.images_dir):
                os.makedirs(self.images_dir)
        except Exception as e:
            print(f"创建目录失败: {e}")
    
    def take_photo(self, instance):
        """拍照功能"""
        if platform == 'android':
            try:
                filepath = CameraHelper.take_picture(self.on_photo_complete)
                if filepath:
                    self.pending_photo_path = filepath
                else:
                    self.show_message('错误', '无法启动相机')
            except Exception as e:
                self.show_message('错误', f'拍照失败: {str(e)}')
        else:
            # 桌面测试
            self.create_test_item()
    
    def on_activity_result(self, request_code, result_code, intent):
        """处理 Activity 结果"""
        if request_code == 1:  # 拍照请求
            if result_code == -1:  # RESULT_OK
                if self.pending_photo_path and os.path.exists(self.pending_photo_path):
                    self.on_photo_complete(self.pending_photo_path)
                else:
                    self.show_message('错误', '照片保存失败')
            else:
                self.show_message('提示', '拍照已取消')
            self.pending_photo_path = None
    
    def on_photo_complete(self, filepath):
        """拍照完成回调"""
        try:
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
                self.show_message('提示', '拍照已取消')
        except Exception as e:
            self.show_message('错误', f'保存失败: {str(e)}')
    
    def create_test_item(self):
        """创建测试物品（用于桌面测试）"""
        try:
            item_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            filepath = os.path.join(self.images_dir, f'item_{item_id}.jpg')
            
            # 创建占位图片
            try:
                from PIL import Image as PILImage
                img = PILImage.new('RGB', (300, 300), color=(73, 109, 137))
                img.save(filepath)
            except:
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
        except Exception as e:
            self.show_message('错误', f'添加失败: {str(e)}')
    
    def display_items(self):
        """显示物品列表"""
        self.items_layout.clear_widgets()
        
        if not self.items:
            empty_label = Label(
                text='暂无记录\n点击"拍照记录"添加物品',
                size_hint_y=None,
                height=100,
                halign='center',
                valign='middle',
                font_name='Roboto'
            )
            empty_label.bind(size=empty_label.setter('text_size'))
            self.items_layout.add_widget(empty_label)
            return
        
        # 按时间倒序排序
        sorted_items = sorted(
            self.items,
            key=lambda x: x['timestamp'],
            reverse=True
        )
        
        for item in sorted_items:
            try:
                if os.path.exists(item['image_path']):
                    card = ItemCard(item, self.delete_item)
                    self.items_layout.add_widget(card)
            except Exception as e:
                print(f"显示物品卡片失败: {e}")
    
    def delete_item(self, item_id):
        """删除物品"""
        try:
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
        except Exception as e:
            self.show_message('错误', f'删除失败: {str(e)}')
    
    def refresh_list(self, instance):
        """刷新列表"""
        try:
            self.load_data()
            self.display_items()
            self.show_message('提示', '列表已刷新！')
        except Exception as e:
            self.show_message('错误', f'刷新失败: {str(e)}')
    
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
        msg_label = Label(
            text=message,
            halign='center',
            valign='middle',
            font_name='Roboto'
        )
        msg_label.bind(size=msg_label.setter('text_size'))
        content.add_widget(msg_label)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.3),
            auto_dismiss=False
        )
        
        close_btn = Button(
            text='关闭',
            size_hint_y=0.3,
            font_name='Roboto'
        )
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()


if __name__ == '__main__':
    ItemTrackerApp().run()