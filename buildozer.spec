[app]

# (str) Title of your application
title = Drone FPV App

# (str) Package name
package.name = dronefpv

# (str) Package domain (needed for android packaging)
package.domain = org.drone

# (str) Source where the app lives
source.dir = .

# (list) Source files to include (let it select all)
source.include_exts = py,png,jpg,kv,atlas

# (str) Version of your application
version = 1.0

# (list) Application requirements
requirements = python3,kivy

# (str) Supported orientations
orientation = portrait

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK / AAB will support
android.minapi = 21

# (str) Android build tools version
android.build_tools_version = 33.0.0

# (str) Android SDK version
android.sdk = 33

# (bool) If True, then skip trying to update the SDK
android.skip_sdk_update = False

# (str) Supported architectures
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
