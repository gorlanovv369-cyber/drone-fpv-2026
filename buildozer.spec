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
# Явно фиксируем стабильную версию build-tools, чтобы избежать запроса лицензий на v37
android.build_tools_version = 33.0.2

[buildozer]
log_level = 2
warn_on_root = 1
