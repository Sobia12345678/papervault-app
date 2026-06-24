[app]
title = PaperVault
package.name = papervault
package.domain = org.papervault

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.include_patterns = assets/*,*.py

requirements = python3,kivy

version = 1.0.0

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 30
android.minapi = 21
android.sdk = 30
android.ndk = 23b

fullscreen = 1
orientation = portrait
bootstrap = sdl2
p4a.branch = release-2022.12.20
