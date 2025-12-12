[app]

title = Item Tracker
package.name = itemtracker
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0

requirements = python3,kivy==2.1.0,pillow,plyer,android,pyjnius

android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.archs = arm64-v8a

# 使用 API 31
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# 跳过 SDK 更新检查
android.skip_update = False
android.accept_sdk_license = True

orientation = portrait
fullscreen = 0

android.entrypoint = org.kivy.android.PythonActivity
android.apptheme = @android:style/Theme.NoTitleBar

android.gradle_dependencies = androidx.core:core:1.6.0
android.enable_androidx = True

[buildozer]

log_level = 2
warn_on_root = 1

# 使用系统的 Android SDK
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.2.9519653