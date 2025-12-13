import sqlite3
import os
from datetime import datetime
from kivy.utils import platform

class Database:
    def __init__(self):
        self.db_path = self.get_db_path()
        self.init_database()
        
    def get_db_path(self):
        if platform == 'android':
            from android.storage import app_storage_path
            return os.path.join(app_storage_path(), 'photos.db')
        else:
            return 'photos.db'
            
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filepath TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def add_photo(self, filepath):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO photos (filepath, timestamp) VALUES (?, datetime("now"))',
            (filepath,)
        )
        
        photo_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return photo_id
        
    def get_all_photos(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, filepath, timestamp,
                   (julianday('now') - julianday(timestamp)) * 24 * 60 as minutes_ago
            FROM photos 
            ORDER BY timestamp DESC
        ''')
        
        photos = []
        for row in cursor.fetchall():
            photo = {
                'id': row[0],
                'filepath': row[1],
                'timestamp': row[2],
                'minutes_ago': row[3]
            }
            photos.append(photo)
            
        conn.close()
        return photos
        
    def delete_photo(self, photo_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 先获取文件路径以便删除文件
            cursor.execute('SELECT filepath FROM photos WHERE id = ?', (photo_id,))
            result = cursor.fetchone()
            
            if result:
                filepath = result[0]
                # 删除数据库记录
                cursor.execute('DELETE FROM photos WHERE id = ?', (photo_id,))
                conn.commit()
                
                # 尝试删除文件
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                except:
                    pass
                    
                return True
        except:
            return False
        finally:
            conn.close()
            
        return False