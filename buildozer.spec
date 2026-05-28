[app]

# (str) Title of your application
title = FishBattle

# (str) Package name
package.name = fishbattle

# (str) Package domain (needed for android packaging)
package.domain = com.antigravity

# (str) Source code directory
source.dir = .

# (list) Source files to include (let's include all game-related file types)
source.include_exts = py,png,jpg,jpeg,ttf,json,csv,xlsm

# (list) List of directory to exclude (let's exclude the .github, buildozer and virtualenvs)
source.exclude_dirs = bin, .buildozer, .git, .github, venv, .venv, __pycache__

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3==3.10.12, pygame==2.6.1

# (str) Supported orientations (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Use fullscreen or not
fullscreen = 1

# =============================================================================
# Android specific
# =============================================================================

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use private storage or external (True or False)
android.private_storage = True

# (str) Android entry point, default is to use start.py or main.py
# android.entrypoint = main

# (list) List of Java .jar files to add to the libs so that Pygame/SDL can load correctly
# android.add_jars = foo.jar

# (list) Java files to add to the project
# android.add_src =

# (list) Gradle dependencies
# android.gradle_dependencies =

# (bool) Enable AndroidX support. Required for newer APIs
android.enable_androidx = True

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (str) Android additional libraries to copy into libs/armeabi
# android.add_libs_armeabi = libs/android-support-v4.jar

# (list) The Android architectures to build for.
android.archs = armeabi-v7a, arm64-v8a

# (bool) Allow service and/or activity to run on separate process
# android.allow_backup = True

# (str) Path to custom activity to use
# android.activity_class = org.kivy.android.PythonActivity

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
