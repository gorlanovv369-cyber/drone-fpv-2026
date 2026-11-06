[app]
title = Drone FPV Control
package.name = droneapp
package.domain = org.drone.fpv
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,opencv,pyjnius

orientation = landscape
fullscreen = 1
android.permissions = INTERNET,CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33
android.minapi = 26
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1
