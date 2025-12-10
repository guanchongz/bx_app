[app]

# 应用信息
title = Item Tracker
package.name = itemtracker
package.domain = org.example

# 源代码
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

# 版本
version = 1.0.0

# 依赖（重要：只包含必要的）
requirements = python3,kivy==2.2.1,pillow,plyer,android

# 权限
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 只构建一个架构（节省空间和时间）
android.archs = arm64-v8a

# Android 配置
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# 应用设置
orientation = portrait
fullscreen = 0

[buildozer]

# 日志级别
log_level = 2
warn_on_root = 1