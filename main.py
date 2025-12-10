import os
import json
import time
from datetime import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView

from plyer import camera

KV = """
<RootWidget>:
    orientation: "vertical"
    padding: dp(10)
    spacing: dp(10)

    BoxLayout:
        size_hint_y: None
        height: dp(48)
        spacing: dp(10)

        Button:
            text: "拍照添加物品"
            on_release: root.take_picture()

        Button:
            text: "刷新列表"
            on_release: root.load_records()

    RecycleView:
        id: rv
        viewclass: "ItemRow"
        data: root.rv_data
        scroll_type: ['bars', 'content']
        bar_width: dp(8)

        RecycleBoxLayout:
            default_size: None, dp(80)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'

<ItemRow@BoxLayout>:
    orientation: "horizontal"
    size_hint_y: None
    height: dp(80)
    padding: dp(5)
    spacing: dp(5)

    # 绑定到 data 中的字段
    image_path: ""
    timestamp: 0
    item_id: 0

    Image:
        source: root.image_path
        size_hint_x: None
        width: dp(80)
        allow_stretch: True
        keep_ratio: True

    BoxLayout:
        orientation: "vertical"
        Label:
            text: "ID: " + str(root.item_id)
            text_size: self.size
            halign: "left"
            valign: "middle"

        Label:
            text: "时间: " + app.format_time(root.timestamp)
            text_size: self.size
            halign: "left"
            valign: "middle"

    Button:
        text: "删除"
        size_hint_x: None
        width: dp(80)
        on_release: app.delete_record(root.item_id)
"""

class RootWidget(BoxLayout):
    rv_data = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.records_file = "records.json"
        self.pictures_dir = "pictures"
        if not os.path.exists(self.pictures_dir):
            os.makedirs(self.pictures_dir, exist_ok=True)
        self.load_records()

    def _read_records(self):
        if not os.path.exists(self.records_file):
            return []
        try:
            with open(self.records_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_records(self, records):
        with open(self.records_file, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    def load_records(self):
        records = self._read_records()
        # 按时间倒序
        records.sort(key=lambda r: r.get("timestamp", 0), reverse=True)
        self.rv_data = [
            {
                "image_path": r["image_path"],
                "timestamp": r["timestamp"],
                "item_id": r["id"],
            }
            for r in records
        ]

    def take_picture(self):
        # 生成唯一文件名
        ts = int(time.time())
        filename = f"item_{ts}.jpg"
        filepath = os.path.join(self.pictures_dir, filename)

        # plyer camera 调用
        try:
            camera.take_picture(
                filename=filepath,
                on_complete=self.on_picture_taken
            )
        except Exception as e:
            print("Error taking picture:", e)

    def on_picture_taken(self, filepath):
        if not filepath or not os.path.exists(filepath):
            print("Picture not taken or file not found.")
            return

        records = self._read_records()
        new_id = (max([r["id"] for r in records]) + 1) if records else 1
        ts = int(time.time())

        record = {
            "id": new_id,
            "image_path": filepath,
            "timestamp": ts,
        }
        records.append(record)
        self._write_records(records)
        self.load_records()


class MyApp(App):
    def build(self):
        self.title = "物品记录APP"
        Builder.load_string(KV)
        return RootWidget()

    def format_time(self, ts):
        try:
            return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return str(ts)

    def delete_record(self, item_id):
        root = self.root
        records = root._read_records()
        new_records = []
        for r in records:
            if r["id"] == item_id:
                # 删除本地图片文件
                img = r.get("image_path")
                if img and os.path.exists(img):
                    try:
                        os.remove(img)
                    except Exception as e:
                        print("Error removing image:", e)
            else:
                new_records.append(r)

        root._write_records(new_records)
        root.load_records()


if __name__ == "__main__":
    MyApp().run()