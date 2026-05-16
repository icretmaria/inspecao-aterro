[app]
title = Inspeção de Aterro
package.name = inspecaoaterro
package.domain = org.obra
source.dir = .
source.main = main.py
version = 1.0
requirements = python3,kivy==2.2.1,kivymd==1.1.1,fpdf2==2.7.9,ezdxf==1.3.4,plyer,android,pillow
orientation = portrait
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.minapi = 21
android.sdk = 33
android.ndk = 23b
android.archs = arm64-v8a
android.accept_sdk_license = True
[buildozer]
log_level = 2
warn_on_root = 1
