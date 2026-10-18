[app]
title = 后台录制
package.name = backgroundrecorder
package.domain = org.workbuddy.demo
source.dir = .
source.include_exts = py,png,kv,jpg
version = 1.0
requirements = python3,kivy==2.3.0,pyjnius,android

# 定义前台服务：后台录制核心（foreground = 状态栏常驻通知）
# 注意语法：服务名 = 服务文件:类型
services = Recorder:service.py:foreground

# 运行时权限
android.permissions = RECORD_AUDIO,CAMERA,POST_NOTIFICATIONS,WAKE_LOCK,FOREGROUND_SERVICE,FOREGROUND_SERVICE_CAMERA,FOREGROUND_SERVICE_MICROPHONE

# Android 版本：Android 9 (API 28) 起允许前台服务使用摄像头
android.api = 34
android.minapi = 28
android.ndk_api = 21
android.archs = arm64-v8a

orientation = portrait
fullscreen = 0

# 日志输出（调试时可改为 1 并用 adb logcat 查看）
android.logcat = 0

[buildozer]
log_level = 2
warn_on_root = 1
