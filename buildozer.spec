[app]

title = Item Tracker
package.name = itemtracker
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf,jpeg,xml,java

version = 1.0

# 添加 pyjnius 用于 Android API 调用
requirements = python3,kivy==2.1.0,pillow,plyer,android,pyjnius

android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.archs = arm64-v8a

android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

orientation = portrait
fullscreen = 0

android.entrypoint = org.kivy.android.PythonActivity
android.apptheme = @android:style/Theme.NoTitleBar
# 添加 FileProvider 支持
android.add_src = java

# Gradle 依赖
android.gradle_dependencies = androidx.core:core:1.6.0
android.enable_androidx = True

# 使用外部 XML 文件
android.extra_manifest_application_arguments = ./android_manifest_application.xml
"""

[buildozer]

log_level = 2
warn_on_root = 1