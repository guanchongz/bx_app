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
        Environment = autoclass('android.os.Environment')
        
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


# 全局变量用于存储 app 实例
_app_instance = None


class ItemTrackerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global _app_instance
        _app_instance = self
        
        self.data_file = None
        self.images_dir = None
        self.items = []
        self.current_photo_path = None
        self._activity_result_listener = None
        self.callback_count = 0
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
            
            # 添加测试按钮
            test_btn = Button(
                text='Test',
                background_color=(0.8, 0.5, 0.2, 1),
                size_hint_x=0.3,
                font_size='18sp',
                font_name='Roboto'
            )
            test_btn.bind(on_press=self.test_callback)
            
            refresh_btn = Button(
                text='Refresh',
                background_color=(0.3, 0.7, 0.3, 1),
                size_hint_x=0.3,
                font_size='18sp',
                font_name='Roboto'
            )
            refresh_btn.bind(on_press=self.refresh_list)
            
            top_layout.add_widget(camera_btn)
            top_layout.add_widget(test_btn)
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
    
    def test_callback(self, instance):
        """测试回调是否工作"""
        try:
            Logger.info("App: Test button pressed")
            self.callback_count += 1
            
            # 模拟拍照回调
            if platform == 'android':
                Logger.info("App: Simulating camera callback")
                self.on_activity_result(1001, -1, None)
            else:
                self.create_test_item()
            
            self.show_message('Test', f'Callback test #{self.callback_count}')
        except Exception as e:
            Logger.error(f"App: Test failed: {e}")
            import traceback
            traceback.print_exc()
    
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
            
            # 使用全局函数作为回调
            def global_callback(request_code, result_code, intent):
                Logger.info(f"GLOBAL CALLBACK: request={request_code}, result={result_code}")
                if _app_instance:
                    _app_instance.on_activity_result(request_code, result_code, intent)
                else:
                    Logger.error("GLOBAL CALLBACK: No app instance!")
            
            class ActivityResultListener(PythonJavaClass):
                __javainterfaces__ = ['org/kivy/android/PythonActivity$ActivityResultListener']
                
                def __init__(self):
                    super().__init__()
                    Logger.info("ActivityResultListener: Created")
                
                @java_method('(IILandroid/content/Intent;)V')
                def onActivityResult(self, requestCode, resultCode, intent):
                    Logger.info(f"ActivityResultListener.onActivityResult: CALLED! request={requestCode}, result={resultCode}")
                    try:
                        global_callback(requestCode, resultCode, intent)
                    except Exception as e:
                        Logger.error(f"ActivityResultListener: Callback failed: {e}")
                        import traceback
                        traceback.print_exc()
            
            self._activity_result_listener = ActivityResultListener()
            activity = PythonActivity.mActivity
            activity.registerActivityResultListener(self._activity_result_listener)
            Logger.info("App: Activity result listener registered")
            
            # 验证注册
            Logger.info(f"App: Listener object: {self._activity_result_listener}")
            Logger.info(f"App: Activity object: {activity}")
            
        except Exception as e:
            Logger.error(f"App: Failed to setup activity listener: {e}")
            import traceback
            traceback.print_exc()
    
    def on_activity_result(self, request_code, result_code, intent):
        """处理 Activity 结果"""
        try:
            Logger.info("=" * 50)
            Logger.info(f"App.on_activity_result: ENTERED")
            Logger.info(f"App: request_code={request_code}")
            Logger.info(f"App: result_code={result_code}")
            Logger.info(f"App: intent={intent}")
            Logger.info("=" * 50)
            
            if request_code == 1001:
                RESULT_OK = -1
                if result_code == RESULT_OK:
                    Logger.info("App: Result is OK")
                    
                    if intent is not None:
                        Logger.info("App: Intent is not None")
                        try:
                            extras = intent.getExtras()
                            Logger.info(f"App: Extras: {extras}")
                            
                            if extras is not None:
                                bitmap = extras.get("data")
                                Logger.info(f"App: Bitmap: {bitmap}")
                                
                                if bitmap is not None:
                                    Logger.info("App: Got bitmap, scheduling save")
                                    Clock.schedule_once(lambda dt: self.save_bitmap(bitmap), 0.1)
                                else:
                                    Logger.warning("App: Bitmap is None")
                                    # 尝试创建测试项
                                    Clock.schedule_once(lambda dt: self.create_test_item(), 0.1)
                            else:
                                Logger.warning("App: Extras is None")
                                Clock.schedule_once(lambda dt: self.create_test_item(), 0.1)
                        except Exception as e:
                            Logger.error(f"App: Error processing intent: {e}")
                            import traceback
                            traceback.print_exc()
                            Clock.schedule_once(lambda dt: self.create_test_item(), 0.1)
                    else:
                        Logger.warning("App: Intent is None")
                        Clock.schedule_once(lambda dt: self.create_test_item(), 0.1)
                else:
                    Logger.warning(f"App: Result not OK: {result_code}")
                    Clock.schedule_once(lambda dt: self.show_message('Cancelled', f'Photo cancelled (code: {result_code})'), 0.1)
            else:
                Logger.warning(f"App: Unknown request code: {request_code}")
                    
        except Exception as e:
            Logger.error(f"App: on_activity_result failed: {e}")
            import traceback
            traceback.print_exc()
    
    def save_bitmap(self, bitmap):
        """保存 Bitmap 到文件"""
        try:
            Logger.info("App: save_bitmap called")
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'item_{timestamp}.jpg'
            filepath = os.path.join(self.images_dir, filename)
            
            Logger.info(f"App: Saving bitmap to: {filepath}")
            
            output_stream = FileOutputStream(filepath)
            bitmap.compress(CompressFormat.JPEG, 90, output_stream)
            output_stream.flush()
            output_stream.close()
            
            Logger.info("App: Bitmap saved")
            
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                Logger.info(f"App: File size: {file_size} bytes")
                
                if file_size > 0:
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
            Logger.error(f"App: save_bitmap failed: {e}")
            import traceback
            traceback.print_exc()
            self.show_message('Error', f'Save failed:\n{str(e)}')
    
    def take_photo(self, instance):
        """拍照功能"""
        try:
            Logger.info("App: take_photo called")
            
            if platform == 'android':
                self.take_photo_android()
            else:
                self.create_test_item()
                
        except Exception as e:
            Logger.error(f"App: take_photo failed: {e}")
            import traceback
            traceback.print_exc()
            self.show_message('Error', f'Photo error:\n{str(e)}')
    
    def take_photo_android(self):
        """Android 拍照"""
        try:
            Logger.info("App: take_photo_android called")
            
            camera_intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
            context = PythonActivity.mActivity
            package_manager = context.getPackageManager()
            
            if camera_intent.resolveActivity(package_manager) is not None:
                Logger.info("App: Starting camera activity")
                context.startActivityForResult(camera_intent, 1001)
                Logger.info("App: Camera activity started")
            else:
                Logger.error("App: No camera app")
                self.show_message('Error', 'No camera app found')
            
        except Exception as e:
            Logger.error(f"App: take_photo_android failed: {e}")
            import traceback
            traceback.print_exc()
            self.show_message('Error', f'Camera failed:\n{str(e)}')
    
    def create_test_item(self):
        """创建测试物品"""
        try:
            Logger.info("App: create_test_item called")
            
            item_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            filepath = os.path.join(self.images_dir, f'item_{item_id}.jpg')
            
            # 创建简单的 JPEG 文件头
            with open(filepath, 'wb') as f:
                # JPEG 文件头
                f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00')
                # 填充一些数据
                f.write(b'\x00' * 1000)
                # JPEG 文件尾
                f.write(b'\xff\xd9')
            
            Logger.info(f"App: Test file created: {filepath}")
            
            item = {
                'id': item_id,
                'image_path': filepath,
                'timestamp': timestamp
            }
            
            self.items.append(item)
            self.save_data()
            self.display_items()
            self.show_message('Success', 'Test item added!')
            Logger.info(f"App: Test item saved: {item_id}")
            
        except Exception as e:
            Logger.error(f"App: create_test_item failed: {e}")
            import traceback
            traceback.print_exc()
            self.show_message('Error', f'Add failed:\n{str(e)}')
    
    def display_items(self):
        """显示物品列表"""
        try:
            Logger.info(f"App: display_items called, {len(self.items)} items")
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
                    Logger.error(f"App: Failed to create card: {e}")
                    
        except Exception as e:
            Logger.error(f"App: display_items failed: {e}")
    
    def delete_item(self, item_id):
        """删除物品"""
        try:
            Logger.info(f"App: delete_item called: {item_id}")
            
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
            Logger.error(f"App: delete_item failed: {e}")
            self.show_message('Error', f'Delete failed:\n{str(e)}')
    
    def refresh_list(self, instance):
        """刷新列表"""
        try:
            Logger.info("App: refresh_list called")
            self.load_data()
            self.display_items()
            self.show_message('Info', f'Refreshed! {len(self.items)} items')
        except Exception as e:
            Logger.error(f"App: refresh_list failed: {e}")
            self.show_message('Error', f'Refresh failed:\n{str(e)}')
    
    def load_data(self):
        """加载数据"""
        try:
            if os.path.exists(self.data_file):
                Logger.info(f"App: Loading from: {self.data_file}")
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.items = json.load(f)
                Logger.info(f"App: Loaded {len(self.items)} items")
            else:
                Logger.info("App: No data file")
                self.items = []
        except Exception as e:
            Logger.error(f"App: load_data failed: {e}")
            self.items = []
    
    def save_data(self):
        """保存数据"""
        try:
            Logger.info(f"App: Saving {len(self.items)} items")
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.items, f, ensure_ascii=False, indent=2)
            Logger.info("App: Data saved")
        except Exception as e:
            Logger.error(f"App: save_data failed: {e}")
    
    def show_message(self, title, message):
        """显示消息"""
        try:
            Logger.info(f"App: show_message: {title} - {message}")
            
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
            Logger.error(f"App: show_message failed: {e}")


if __name__ == '__main__':
    try:
        Logger.info("=" * 50)
        Logger.info("App: STARTING ItemTrackerApp")
        Logger.info("=" * 50)
        ItemTrackerApp().run()
    except Exception as e:
        Logger.error(f"App: FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()