from kivy.utils import platform
from datetime import datetime
import os

if platform == 'android':
    from jnius import autoclass, cast
    from android import activity
    from android.permissions import Permission, check_permission
    
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    MediaStore = autoclass('android.provider.MediaStore')
    Environment = autoclass('android.os.Environment')
    Uri = autoclass('android.net.Uri')
    FileProvider = autoclass('android.support.v4.content.FileProvider')
    Context = autoclass('android.content.Context')
    
class AndroidCamera:
    def __init__(self):
        self.current_activity = None
        self.callback = None
        
    def take_picture(self, callback):
        self.callback = callback
        
        if platform == 'android':
            self.current_activity = PythonActivity.mActivity
            
            # 创建Intent
            intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
            
            # 创建临时文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"photo_{timestamp}.jpg"
            
            # 获取外部存储目录
            pics_dir = Environment.getExternalStoragePublicDirectory(
                Environment.DIRECTORY_PICTURES
            )
            app_dir = File(pics_dir, "PhotoTimeline")
            if not app_dir.exists():
                app_dir.mkdirs()
                
            photo_file = File(app_dir, filename)
            
            # 获取FileProvider URI
            context = self.current_activity.getApplicationContext()
            authority = f"{context.getPackageName()}.provider"
            photo_uri = FileProvider.getUriForFile(
                context,
                authority,
                photo_file
            )
            
            # 添加URI到Intent
            intent.putExtra(MediaStore.EXTRA_OUTPUT, photo_uri)
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            intent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
            
            # 启动相机活动
            self.current_activity.startActivityForResult(intent, 100)
            
            # 绑定结果处理
            activity.bind(on_activity_result=self.on_activity_result)
            
    def on_activity_result(self, request_code, result_code, intent):
        if request_code == 100:
            activity.unbind(on_activity_result=self.on_activity_result)
            
            if result_code == -1:  # RESULT_OK
                # 获取最后拍摄的照片
                cursor = self.current_activity.getContentResolver().query(
                    MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                    None,
                    None,
                    None,
                    MediaStore.Images.Media.DATE_ADDED + " DESC"
                )
                
                if cursor and cursor.moveToFirst():
                    path_index = cursor.getColumnIndex(MediaStore.Images.Media.DATA)
                    filepath = cursor.getString(path_index)
                    cursor.close()
                    
                    if self.callback:
                        self.callback(filepath)