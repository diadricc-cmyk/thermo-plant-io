[app]

title = THERMO-PLANT IO
package.name = thermoplantio
package.domain = org.thermoplant

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

version = 0.1

requirements = python3,kivy,plyer

orientation = portrait
fullscreen = 0

# Permisos Android
android.permissions = INTERNET

# Arquitecturas Android
android.archs = arm64-v8a, armeabi-v7a

# Nombre del APK
android.entrypoint = org.kivy.android.PythonActivity


[buildozer]

log_level = 2
warn_on_root = 1
