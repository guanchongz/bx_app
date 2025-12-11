[app]

title = Item Tracker
package.name = itemtracker
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0

requirements = python3,kivy==2.1.0,pillow,plyer,android

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

[buildozer]

log_level = 2
warn_on_root = 1