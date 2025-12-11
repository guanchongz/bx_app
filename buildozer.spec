[app]

# 应用信息
title = Item Tracker
package.name = itemtracker
package.domain = org.example

# 源代码
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

# 版本
version = 1.0

# 依赖 - 使用稳定版本
requirements = python3,kivy==2.1.0,pillow,plyer,android

# 权限
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 只构建一个架构
android.archs = arm64-v8a

# Android 配置 - 使用更低的 API 级别
android.api = 29
android.minapi = 21
android.ndk = 23b
android.accept_sdk_license = True

# 应用设置
orientation = portrait
fullscreen = 0

# Android entry point
android.entrypoint = org.kivy.android.PythonActivity
android.apptheme = @android:style/Theme.NoTitleBar

[buildozer]

# 日志级别
log_level = 2

# 警告
warn_on_root = 1