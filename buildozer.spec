
[app]

title = RedPacket Sniper
package.name = redpacketsniper
package.domain = org.nadir

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3,kivy==2.3.1,requests,telethon,pyaes

p4a.branch = develop

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,POST_NOTIFICATIONS

android.api = 35
android.minapi = 24
android.accept_sdk_license = True
android.archs = arm64-v8a

[buildozer]

log_level = 2
warn_on_root = 1
