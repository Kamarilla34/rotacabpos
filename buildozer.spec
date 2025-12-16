[app]
title = Taksi POS
package.name = taksipos
package.domain = org.taksi
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.2.0,kivymd,requests,pillow,urllib3,chardet,idna
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 31
android.minapi = 21
p4a.branch = master
icon.filename = %(source.dir)s/logo.png
presplash.filename = %(source.dir)s/logo.png

[buildozer]
log_level = 2
warn_on_root = 1
