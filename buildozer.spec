[app]

#GENERAL

title = Calendar Tracker

version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/main.py

package.name = cal_tracker
package.domain = org.cal_tracker

source.dir = .
source.exclude_dirs = .vs, __pycache__, build
source.include_exts = 
source.exclude_exts = spec,html,htm,gitattributes,gitignore
#source.include_patterns = assets/*,images/*.png
#source.exclude_patterns = license,images/*/*.jpg

icon.filename = calendar_icon.png
presplash.filename = calendar_icon.png

requirements = python3,kivy,kivymd,sqlite3
orientation = portrait

# OSX Specific

osx.python_version = 3


# Android specific

fullscreen = 0
android.presplash_color = #000000
android.permissions = READ_EXTERNAL_STORAGE
# (str) Android logcat filters to use
android.logcat_filters = *:S python:D
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True


[buildozer]

log_level = 2
warn_on_root = 1
