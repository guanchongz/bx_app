[app]

# (str) Title of your application
title = 拍照时间线

# (str) Package name
package.name = phototimeline

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin, venv

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 1.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.1.0,plyer,android,pyjnius

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

# (str) OS X specific plist additions (let empty to not add)
#osx.plist_add = 

# (bool) Android API 31 support
android.api = 31

# (int) Minimum API required
android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 23

# (str) Android NDK version to use
#android.ndk = 23b

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid an infinite loop while waiting for the sdk to install
# android.skip_update = False

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.renpy.android.PythonActivity

# (list) Pattern to whitelist for the whole project
#android.whitelist =

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a custom blacklist file
#android.blacklist_src =

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process. Allows wildcards matching, for example:
# OUYA-ODK/libs/*.jar
#android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
#android.add_src =

# (list) Android AAR archives to add (currently works only with sdl2_gradle
# bootstrap)
#android.add_aars =

# (list) Gradle dependencies to add
#android.gradle_dependencies =

# (str) python-for-android branch to use, defaults to master
#p4a.branch = master

# (str) OUYA Console category. For games, declare as GAME or APP
# If you leave this blank, OUYA support will not be enabled
#android.ouya.category = GAME

# (str) Filename of OUYA Console icon. It must be a 732x412 png image.
#android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) XML file to include as an intent filters in <activity> tag
#android.manifest.intent_filters =

# (list) Android additionnal permissions to add to the manifest
#android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (list) Android additional permissions to add to the manifest
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET

# (int) Android API to use for the permissions
android.permissions_api = 31

# (int) Android API level to use for the build
android.api = 31

# (int) Minimum Android API required
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 31

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid an infinite loop while waiting for the sdk to install
# android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
# android.accept_sdk_license = False

# (str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme, default is ok for Kivy-based app
# android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Pattern to whitelist for the whole project
#android.whitelist =

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a custom blacklist file
#android.blacklist_src =

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process. Allows wildcards matching, for example:
# OUYA-ODK/libs/*.jar
android.add_jars = 

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
android.add_src =

# (list) Android AAR archives to add
#android.add_aars =

# (list) Gradle dependencies to add
android.gradle_dependencies = 'androidx.core:core:1.7.0'

# (list) add java compile options
# this can for example be necessary when importing certain java libraries using the 'android.gradle_dependencies' option
# see https://developer.android.com/studio/write/java8-support for further information
# android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"

# (list) Gradle repositories to add
android.add_gradle_repositories =

# (list) packaging options to add
# see https://google.github.io/android-gradle-dsl/current/com.android.build.gradle.internal.dsl.PackagingOptions.html
# can be necessary to solve conflicts in gradle_dependencies
# please enclose in double quotes
# e.g. android.add_packaging_options = "exclude 'META-INF/common.kotlin_module'", "exclude 'META-INF/*.kotlin_module'"
#android.add_packaging_options =

# (list) Java classes to add as activities to the manifest.
#android.add_activities = com.example.ExampleActivity

# (str) OUYA Console category. For games, declare as GAME or APP
# If you leave this blank, OUYA support will not be enabled
#android.ouya.category = GAME

# (str) Filename of OUYA Console icon. It must be a 732x412 png image.
#android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) XML file to include as an intent filters in <activity> tag
android.manifest.intent_filters = ./android/intent_filters.xml

# (list) Android additionnal permissions to add to the manifest
#android.permissions = INTERNET

# (str) The format used to package the app for release mode (aab or apk).
# android.release_artifact = aab

# (str) The format used to package the app for debug mode (apk).
# android.debug_artifact = apk

#
# Python for android (p4a) specific
#

# (str) python-for-android branch to use, defaults to master
#p4a.branch = master

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#p4a.source_dir =

# (str) The directory where the python distribution (python3.9) will be installed
#p4a.python_dir =

# (str) The directory where the python distribution (python3.9) will be installed
#p4a.python_dir =

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# buildozer.storage_dir =

# (str) Buildozer will store builds here
buildozer.storage_dir = .buildozer

# (str) buildozer target directory for downloads, etc.
# buildozer.global_storage_dir = ~/.buildozer

# (str) Path to a custom buildozer (file or directory)
# buildozer.bin_dir =

# (str) Path to the directory where the application will be built.
# This directory will be cleaned on each run.
# buildozer.build_dir = .buildozer/platform/android/build

# (str) Path to the directory where the cross compilation toolchain will be installed.
# This directory will be cleaned on each run.
# buildozer.cross_dir = .buildozer/platform/android/cross

# (list) List of buildozer targets to execute. Possible targets: android, android_old, ios, ios_old
# Default is ['android']
targets = android

# (list) List of adb devices IDs that should be excluded from automatic detection.
# Default is []
# adb_exclude_devices =

# (list) List of device IDs that should be excluded from automatic detection.
# Default is []
# device_exclude_devices =

# (bool) Update the Android sdk before building.
# This will accept the sdk license if you didn't previously accept it.
# Default is False
# update_android_sdk = False

# (str) Android sdk license key hash. Only needed if update_android_sdk is True and the sdk license needs to be accepted.
# Default is ''
# android_sdk_license_key_hash =

# (bool) Skip the Android sdk update. Only needed if update_android_sdk is True and you want to skip the sdk update.
# Default is False
# skip_android_sdk_update = False

# (bool) Skip the Android ndk update. Only needed if update_android_ndk is True and you want to skip the ndk update.
# Default is False
# skip_android_ndk_update = False

# (bool) Skip the Android platform-tools update. Only needed if update_android_platform_tools is True and you want to skip the platform-tools update.
# Default is False
# skip_android_platform_tools_update = False

[app:source]

# (str) URL to the app source code
url = https://github.com/yourusername/photo-timeline-app

# (str) app source code revision to use
# revision = HEAD

[app:android]

# (bool) Indicates whether the app should be fullscreen or not
fullscreen = 0

# (str) Android app icon
icon.filename = icon.png

# (str) Android app round icon (used on Android 7.0 and above)
icon.adaptive.foreground.filename = icon.png
icon.adaptive.background.filename = icon.png

# (str) Android app splash screen
presplash.filename = presplash.png

# (str) Adaptive icon background color (used on Android 8.0 and above)
icon.adaptive.background.color = '#2196F3'

# (str) Adaptive icon foreground color (used on Android 8.0 and above)
icon.adaptive.foreground.color = '#FFFFFF'

[app:ios]

# (str) Path to app icon
icon.filename = icon.png

# (str) Path to app splash screen
presplash.filename = presplash.png