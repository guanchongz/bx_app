from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock
from datetime import datetime

class PhotoItem(BoxLayout):
    photo_id = NumericProperty(0)
    image_path = StringProperty('')
    timestamp = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_duration()
        Clock.schedule_interval(lambda dt: self.update_duration(), 60)  # 每分钟更新一次
        
    def on_image_path(self, instance, value):
        if hasattr(self, 'ids'):
            self.ids.thumbnail.source = value
            
    def on_timestamp(self, instance, value):
        if hasattr(self, 'ids'):
            try:
                dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                time_str = dt.strftime('%Y年%m月%d日 %H:%M:%S')
                self.ids.time_label.text = time_str
            except:
                self.ids.time_label.text = value
                
    def update_duration(self):
        if self.timestamp:
            try:
                dt = datetime.strptime(self.timestamp, '%Y-%m-%d %H:%M:%S')
                now = datetime.now()
                diff = now - dt
                
                minutes = int(diff.total_seconds() / 60)
                if minutes < 60:
                    duration = f"{minutes}分钟前"
                elif minutes < 1440:
                    hours = minutes // 60
                    duration = f"{hours}小时前"
                else:
                    days = minutes // 1440
                    duration = f"{days}天前"
                    
                self.ids.duration_label.text = duration
            except:
                self.ids.duration_label.text = ""
                
    def delete_item(self):
        if hasattr(self, 'app') and self.app:
            screen = self.app.root.get_screen('main')
            screen.delete_photo(self.photo_id)