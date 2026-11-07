[app]
title = Drone FPV App
package.name = dronefpv
package.domain = org.drone
source.include_exts = py,png,jpg,kv,atlas
requirements = python3,kivy
orientation = portrait
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.build_tools_version = 33.0.0
android.sdk = 33
android.skip_sdk_update = False
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
