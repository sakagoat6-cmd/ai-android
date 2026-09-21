[app]

# Vibes Only V11 Android build

title = Vibes Only
package.name = vibesonly
package.domain = org.vibes

# main.py must be in this directory.
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,txt
source.exclude_dirs = .buildozer,bin,__pycache__,.git

version = 11.0

# Keep the Android dependency set focused on packages that p4a can build.
requirements = python3,kivy,requests,beautifulsoup4,wikipedia,PyPDF2,youtube-transcript-api,pillow

orientation = portrait
fullscreen = 0

# Android SDK configuration.
android.api = 35
android.minapi = 24
android.archs = arm64-v8a
android.permissions = INTERNET
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 0
build_dir = ./.buildozer
bin_dir = ./bin
