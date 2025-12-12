from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.utils import platform
from kivy.logger import Logger
from kivy.core.text import LabelBase
from kivy.clock import Clock
import json
import os
from datetime import datetime

# 注册中文字体
if platform == 'android':
    chinese_fonts = [
        '/system/fonts/NotoSansCJK-Regular.ttc',
        '/system/fonts/NotoSansSC-Regular.otf',
        '/system/fonts/DroidSansFallback.ttf',
        '/system/fonts/NotoSansHans-Regular.otf',
    ]
    
    for font_path in chinese_fonts:
        if os.path.exists(font_path):
            try:
                LabelBase.register(name='Roboto', fn_regular=font_path)
                Logger.info(f"App: Registered Chinese font: {font_path}")
                break
            except Exception as e:
                Logger.warning(f"App: Failed to register font {font_path}: {e}")

# Android 权限和类
if platform == 'android':
    try:
        from android.permissions import request_permissions, Permission
        from jnius import autoclass, cast, PythonJavaClass, java_method
        
        request_permissions([
            Permission.CAMERA,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE
        ])
        
        # Android 类
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        MediaStore = autoclass('android.provider.MediaStore')
        Uri = autoclass('android.net.Uri')
        File = autoclass('java.io.File')
        Bitmap = autoclass('android.graphics.Bitmap')
        BitmapFactory = autoclass('android.graphics.BitmapFactory')
        FileOutputStream = autoclass('java.io.FileOutputStream')
        ByteArrayOutputStream = autoclass('java.io.ByteArrayOutputStream')
        CompressFormat = autoclass('android.graphics.Bitmap$CompressFormat')
        
        Logger.info("App: Android modules loaded successfully")
    except Exception as e:
        Logger.error(f"App: Failed to load Android modules: {e}")


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
            image_path = item_data['image_path']
            Logger.info(f"ItemCard: Loading image from: {image_path}")
            
            if os.path.exists(image_path):
                img = Image(
                    source=image_path,
                    size_hint_x=0.3,
                    allow_stretch=True,
                    keep_ratio=True
                )
                Logger.info(f"ItemCard: Image loaded successfully")
            else:
                Logger.warning(f"ItemCard: Image file not found: {image_path}")
                img = Label(text='No Image', size_hint_x=0.3, font_name='Roboto')
        except Exception as e:
            Logger.error(f"ItemCard: Failed to load image: {e}")
            img = Label(text='Error', size_hint_x=0.3, font_name='Roboto')
        
        self.add_widget(img)
        
        # 信息区域
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.5)
        
        time_text = item_data.get('timestamp', 'N/A')
        time_label = Label(
            text=f"Time: {time_text}",
            size_hint_y=0.5,
            halign='left',
            valign='middle',
            font_name='Roboto'
        )
        time_label.bind(size=time_label.setter('text_size'))
        
        item_id = item_data.get('id', 'unknown')
        id_label = Label(
            text=f"ID: {item_id[:8] if len(item_id) >= 8 else item_id}", 
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
            text='Delete',
            size_hint_x=0.2,
            background_color=(1, 0.3, 0.3, 1),
            font_name='Roboto'
        )
        delete_btn.bind(on_press=self.confirm_delete)
        self.add_widget(delete_btn)
    
    def confirm_delete(self, instance):
        """确认删除对话框"""
        try:
            content = BoxLayout(orientation='vertical', padding=10, spacing=10)
            msg_label = Label(text='Delete this item?', font_name='Roboto')
            content.add_widget(msg_label)
            
            btn_layout = BoxLayout(size_hint_y=0.3, spacing=10)
            
            popup = Popup(
                title='Confirm Delete',
                content=content,
                size_hint=(0.8, 0.4),
                auto_dismiss=False
            )
            
            confirm_btn = Button(
                text='Confirm',
                background_color=(1, 0.3, 0.3, 1),
                font_name='Roboto'
            )
            cancel_btn = Button(text='Cancel', font_name='Roboto')
            
            confirm_btn.bind(on_press=lambda x: self.delete_item(popup))
            cancel_btn.bind(on_press=popup.dismiss)
            
            btn_layout.add_widget(cancel_btn)
            btn_layout.add_widget(confirm_btn)
            content.add_widget(btn_layout)
            
            popup.open()
        except Exception as e:
            Logger.error(f"ItemCard: Failed to show delete dialog: {e}")
    
    def delete_item(self, popup):
        """执行删除"""
        try:
            popup.dismiss()
            self.delete_callback(self.item_data['id'])
        except Exception as e:
            Logger.error(f"ItemCard: Failed to delete item: {e}")


class ItemTrackerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_file = None
        self.images_dir = None
        self.items = []
        self.current_photo_path = None
        self._activity_result_listener = None
        Logger.info("App: ItemTrackerApp initialized")
    
    def build(self):
        """构建应用界面"""
        try:
            Logger.info("App: Building UI")
            self.setup_storage()
            self.load_data()
            
            # 设置 Activity 结果监听器
            if platform == 'android':
                self.setup_activity_listener()
            
            # 主布局
            main_layout = BoxLayout(orientation='vertical')
            
            # 顶部按钮
            top_layout = BoxLayout(size_hint_y=0.1, padding=10, spacing=10)
            
            camera_btn = Button(
                text='Take Photo',
                background_color=(0.2, 0.6, 1, 1),
                font_size='18sp',
                font_name='Roboto'
            )
            camera_btn.bind(on_press=self.take_photo)
            
            refresh_btn = Button(
                text='Refresh',
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
            
            self.display_items()
            
            Logger.info("App: UI built successfully")
            return main_layout
            
        except Exception as e:
            Logger.error(f"App: Failed to build UI: {e}")
            import traceback
            traceback.print_exc()
            error_layout = BoxLayout(orientation='vertical', padding=20)
            error_label = Label(
                text=f'App startup failed:\n{str(e)}',
                halign='center',
                valign='middle',
                font_name='Roboto'
            )
            error_label.bind(size=error_label.setter('text_size'))
            error_layout.add_widget(error_label)
            return error_layout
    
    def setup_storage(self):
        """设置存储路径"""
        try:
            Logger.info("App: Setting up storage")
            
            if platform == 'android':
                try:
                    context = PythonActivity.mActivity
                    
                    # 使用应用专属的外部文件目录
                    files_dir = context.getExternalFilesDir(None)
                    if files_dir:
                        self.data_dir = files_dir.getAbsolutePath()
                    else:
                        files_dir = context.getFilesDir()
                        self.data_dir = files_dir.getAbsolutePath()
                    
                    Logger.info(f"App: Using storage dir: {self.data_dir}")
                    
                except Exception as e:
                    Logger.error(f"App: Failed to get Android storage: {e}")
                    from android.storage import app_storage_path
                    self.data_dir = app_storage_path()
            else:
                self.data_dir = os.path.dirname(os.path.abspath(__file__))
            
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
            
            self.data_file = os.path.join(self.data_dir, 'items_data.json')
            self.images_dir = self.data_dir
            
            Logger.info(f"App: Data file: {self.data_file}")
            Logger.info(f"App: Images dir: {self.images_dir}")
            
        except Exception as e:
            Logger.error(f"App: Storage setup failed: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_activity_listener(self):
        """设置 Activity 结果监听器"""
        try:
            Logger.info("App: Setting up activity listener")
            
            class ActivityResultListener(PythonJavaClass):
                __javainterfaces__ = ['org/kivy/android/PythonActivity$ActivityResultListener']
                
                def __init__(self, callback):
                    super().__init__()
                    self.callback = callback
                    Logger.info("ActivityResultListener: Initialized")
                
                @java_method('(IILandroid/content/Intent;)V')
                def onActivityResult(self, requestCode, resultCode, intent):
                    Logger.info(f"ActivityResultListener: onActivityResult called - code={requestCode}, result={resultCode}")
                    self.callback(requestCode, resultCode, intent)
            
            self._activity_result_listener = ActivityResultListener(self.on_activity_result)
            PythonActivity.mActivity.registerActivityResultListener(self._activity_result_listener)
            Logger.info("App: Activity result listener registered successfully")
            
        except Exception as e:
            Logger.error(f"App: Failed to setup activity listener: {e}")
            import traceback
            traceback.print_exc()
    
    def on_activity_result(self, request_code, result_code, intent):
        """处理 Activity 结果"""
        try:
            Logger.info(f"App: on_activity_result called")
            Logger.info(f"App: request_code={request_code}, result_code={result_code}")
            Logger.info(f"App: intent={intent}")
            
            if request_code == 1001:  # 相机请求码
                RESULT_OK = -1
                if result_code == RESULT_OK:
                    Logger.info("App: Camera result OK, processing...")
                    
                    if intent is not None:
                        # 从 Intent 获取缩略图
                        extras = intent.getExtras()
                        if extras is not None:
                            Logger.info("App: Intent has extras")
                            bitmap = extras.get("data")
                            if bitmap is not None:
                                Logger.info("App: Got bitmap from intent")
                                Clock.schedule_once(lambda dt: self.save_bitmap(bitmap), 0.1)
                            else:
                                Logger.warning("App: No bitmap in extras")
                                self.show_message('Error', 'No image data received')
                        else:
                            Logger.warning("App: Intent has no extras")
                            self.show_message('Error', 'No image data received')
                    else:
                        Logger.warning("App: Intent is None")
                        self.show_message('Error', 'No image data received')
                else:
                    Logger.warning(f"App: Camera cancelled or failed: {result_code}")
                    self.show_message('Cancelled', 'Photo was cancelled')
            else:
                Logger.warning(f"App: Unknown request code: {request_code}")
                    
        except Exception as e:
            Logger.error(f"App: Activity result handler failed: {e}")
            import traceback
            traceback.print_exc()
            self.show_message('Error', f'Failed to process photo:\n{str(e)}')
    
    def save_bitmap(self, bitmap):
        """保存 Bitmap 到文件"""
        try:
            Logger.info("App: Saving bitmap to file")
            
            # 生成文件路径
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'item_{timestamp}.jpg'
            filepath = os.path.join(self.images_dir, filename)
            
            Logger.info(f"App: Saving to: {filepath}")
            
            # 将 Bitmap 保存为 JPEG
            output_stream = FileOutputStream(filepath)
            bitmap.compress(CompressFormat.JPEG, 90, output_stream)
            output_stream.flush()
            output_stream.close()
            
            Logger.info("App: Bitmap saved successfully")
            
            # 验证文件
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                Logger.info(f"App: File size: {file_size} bytes")
                
                if file_size > 0:
                    # 保存记录
                    item_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
                    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    item = {
                        'id': item_id,
                        'image_path': filepath,
                        'timestamp': timestamp_str
                    }
                    
                    self.items.append(item)
                    self.save_data()
                    self.display_items()
                    self.show_message('Success', 'Item recorded!')
                    Logger.info(f"App: Item saved: {item_id}")
                else:
                    Logger.warning("App: File is empty")
                    self.show_message('Error', 'Photo file is empty')
            else:
                Logger.warning("App: File not created")
                self.show_message('Error', 'Failed to save photo')
            
        except Exception as e:
            Logger.error(f"App: Save bitmap failed: {e}")
            import traceback
            traceback.print_exc()
            self.show_message('Error', f'Save failed:\n{str(e)}')
    
    def take_photo(self, instance):
        """拍照功能"""
        try:
            Logger.info("App: Take photo button pressed")
            
            if platform == 'android':
                self.take_photo_android()
            else:
                self.create_test_item()
                
        except Exception as e:
            Logger.error(f"App: Take photo failed: {e}")
            import traceback
            traceback.print_exc()
            self.show_message('Error', f'Photo function error:\n{str(e)}')
    
    def take_photo_android(self):
        """Android 拍照 - 使用 Intent（获取缩略图）"""
        try:
            Logger.info("App: Starting Android camera with Intent")
            
            # 创建相机 Intent（不指定输出，获取缩略图）
            camera_intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
            
            # 检查是否有相机应用
            context = PythonActivity.mActivity
            package_manager = context.getPackageManager()
            
            if camera_intent.resolveActivity(package_manager) is not None:
                Logger.info("App: Camera app found, starting activity")
                # 启动相机
                PythonActivity.mActivity.startActivityForResult(camera_intent, 1001)
                Logger.info("App: Camera intent started successfully")
            else:
                Logger.error("App: No camera app found")
                self.show_message('Error', 'No camera app found')
            
        except Exception as e:
            Logger.error(f"App: Android camera failed: {e}")
            import traceback
            traceback.print_exc()
            self.show_message('Error', f'Camera failed:\n{str(e)}')
    
    def create_test_item(self):
        """创建测试物品（用于桌面测试）"""
        try:
            Logger.info("App: Creating test item")
            
            item_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            filepath = os.path.join(self.images_dir, f'item_{item_id}.jpg')
            
            try:
                from PIL import Image as PILImage
                img = PILImage.new('RGB', (300, 300), color=(73, 109, 137))
                img.save(filepath)
            except:
                with open(filepath, 'wb') as f:
                    f.write(b'\xff\xd8\xff\xe0')
            
            item = {
                'id': item_id,
                'image_path': filepath,
                'timestamp': timestamp
            }
            
            self.items.append(item)
            self.save_data()
            self.display_items()
            self.show_message('Success', 'Test item added!')
            Logger.info(f"App: Test item created: {item_id}")
            
        except Exception as e:
            Logger.error(f"App: Create test item failed: {e}")
            import traceback
            traceback.print_exc()
            self.show_message('Error', f'Add failed:\n{str(e)}')
    
    def display_items(self):
        """显示物品列表"""
        try:
            Logger.info(f"App: Displaying {len(self.items)} items")
            self.items_layout.clear_widgets()
            
            if not self.items:
                empty_label = Label(
                    text='No records\nClick "Take Photo" to add items',
                    size_hint_y=None,
                    height=100,
                    halign='center',
                    valign='middle',
                    font_name='Roboto'
                )
                empty_label.bind(size=empty_label.setter('text_size'))
                self.items_layout.add_widget(empty_label)
                return
            
            sorted_items = sorted(
                self.items,
                key=lambda x: x.get('timestamp', ''),
                reverse=True
            )
            
            for item in sorted_items:
                try:
                    card = ItemCard(item, self.delete_item)
                    self.items_layout.add_widget(card)
                except Exception as e:
                    Logger.error(f"App: Failed to create card for item {item.get('id')}: {e}")
                    
        except Exception as e:
            Logger.error(f"App: Display items failed: {e}")
    
    def delete_item(self, item_id):
        """删除物品"""
        try:
            Logger.info(f"App: Deleting item: {item_id}")
            
            item_to_delete = None
            for item in self.items:
                if item.get('id') == item_id:
                    item_to_delete = item
                    break
            
            if item_to_delete:
                image_path = item_to_delete.get('image_path')
                if image_path and os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                        Logger.info(f"App: Deleted image: {image_path}")
                    except Exception as e:
                        Logger.error(f"App: Failed to delete image: {e}")
                
                self.items.remove(item_to_delete)
                self.save_data()
                self.display_items()
                self.show_message('Success', 'Item deleted!')
            else:
                Logger.warning(f"App: Item not found: {item_id}")
                
        except Exception as e:
            Logger.error(f"App: Delete item failed: {e}")
            self.show_message('Error', f'Delete failed:\n{str(e)}')
    
    def refresh_list(self, instance):
        """刷新列表"""
        try:
            Logger.info("App: Refreshing list")
            self.load_data()
            self.display_items()
            self.show_message('Info', 'List refreshed!')
        except Exception as e:
            Logger.error(f"App: Refresh failed: {e}")
            self.show_message('Error', f'Refresh failed:\n{str(e)}')
    
    def load_data(self):
        """加载数据"""
        try:
            if os.path.exists(self.data_file):
                Logger.info(f"App: Loading data from: {self.data_file}")
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.items = json.load(f)
                Logger.info(f"App: Loaded {len(self.items)} items")
            else:
                Logger.info("App: No data file found, starting fresh")
                self.items = []
        except Exception as e:
            Logger.error(f"App: Load data failed: {e}")
            self.items = []
    
    def save_data(self):
        """保存数据"""
        try:
            Logger.info(f"App: Saving {len(self.items)} items to: {self.data_file}")
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.items, f, ensure_ascii=False, indent=2)
            Logger.info("App: Data saved successfully")
        except Exception as e:
            Logger.error(f"App: Save data failed: {e}")
    
    def show_message(self, title, message):
        """显示消息提示"""
        try:
            Logger.info(f"App: Showing message - {title}: {message}")
            
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
                text='Close',
                size_hint_y=0.3,
                font_name='Roboto'
            )
            close_btn.bind(on_press=popup.dismiss)
            content.add_widget(close_btn)
            
            popup.open()
            
        except Exception as e:
            Logger.error(f"App: Show message failed: {e}")


if __name__ == '__main__':
    try:
        Logger.info("App: Starting ItemTrackerApp")
        ItemTrackerApp().run()
    except Exception as e:
        Logger.error(f"App: Fatal error: {e}")
        import traceback
        traceback.print_exc()