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
source.include_exts = py,png,jpg,kv,atlas,json

# 版本号
version = 1.0.0

# 应用需要的权限
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET

# 支持的架构
android.archs = arm64-v8a, armeabi-v7a

# Python 依赖
requirements = python3,kivy==2.2.1,pillow,plyer,android

# Android API 版本
android.api = 31
android.minapi = 21

# NDK 版本
android.ndk = 25b

# SDK 构建工具版本（重要！）
android.sdk_build_tools = 30.0.3

# 自动接受 SDK 许可证
android.accept_sdk_license = True

# 应用方向
orientation = portrait

# 全屏模式
fullscreen = 0

# Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# Android app theme
android.apptheme = "@android:style/Theme.NoTitleBar"

# 跳过更新（加快构建速度）
android.skip_update = False

# 日志级别
log_level = 2

# 警告级别
warn_on_root = 1

[buildozer]

# 日志级别
log_level = 2

# 警告显示
warn_on_root = 1