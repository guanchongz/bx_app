[app]

# 应用名称
title = Item Tracker

# 包名
package.name = itemtracker

# 包域名
package.domain = org.example

# 源代码目录
source.dir = .

# 源代码包含的文件
source.include_exts = py,png,jpg,kv,atlas,json,jpeg

# 版本号
version = 1.0.0

# 应用需要的权限
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET

# 支持的架构
android.archs = arm64-v8a,armeabi-v7a

# Python 依赖
requirements = python3,kivy==2.2.1,pillow,plyer,android

# 应用图标（可选，如果有的话）
icon.filename = %(source.dir)s/assets/icon.jpeg

# 启动画面（可选）
presplash.filename = %(source.dir)s/assets/icon.jpeg

# Android API 版本
android.api = 31
android.minapi = 21
android.ndk = 25b

# 应用方向
orientation = portrait

# 全屏模式
fullscreen = 0

# Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# Android app theme
android.apptheme = "@android:style/Theme.NoTitleBar"

# 日志级别
log_level = 2

# 警告级别
warn_on_root = 1

[buildozer]

# 日志级别
log_level = 2

# 警告显示
warn_on_root = 1