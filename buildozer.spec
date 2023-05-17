[app]

#GENERAL

title = Calendar Tracker
version = 0.2.0
package.name = cal_tracker
package.domain = org.cal_tracker

source.dir = .
source.exclude_dirs = .vs, __pycache__, build
source.include_exts = 
source.exclude_exts = spec,html,htm,gitattributes,gitignore,db
#source.include_patterns = assets/*,images/*.png
#source.exclude_patterns = license,images/*/*.jpg

icon.filename = calendar_icon.png
presplash.filename = calendar_icon.png
requirements = python3,kivy==2.1.0,kivymd==1.0.2,multipledispatch,sqlite3,pillow

orientation = portrait

# OSX Specific

osx.python_version = 3


# Android specific

fullscreen = 0
android.presplash_color = #000000
android.permissions = INTERNET, STORAGE
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True


# iOS specific
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master

ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0

ios.codesign.allowed = false

[buildozer]

log_level = 2
warn_on_root = 1
