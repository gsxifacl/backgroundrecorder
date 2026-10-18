# 后台录像录音 App（Python / Kivy / Android）

一个用 **纯 Python（Kivy + python-for-android）** 编写的安卓后台录音录像应用。
录制逻辑运行在 **前台服务** 中，App 退到后台、锁屏后仍持续录制。

## 项目结构

| 文件 | 作用 |
|---|---|
| `main.py` | Kivy 界面：开始录音 / 开始录像 / 停止，实时显示录制时长 |
| `service.py` | 前台服务：真正执行录制的进程，通过 MediaRecorder 输出 mp4 |
| `buildozer.spec` | 打包配置（权限、前台服务声明、API 版本） |

## 技术原理

1. **UI 层（main.py）**：Kivy 界面，点击按钮后通过 `AndroidService` 启动前台服务，并先用 `request_permissions` 动态申请录音 / 摄像头权限。
2. **服务层（service.py）**：p4a 前台服务（状态栏常驻通知），用 **pyjnius 直接调用 Android 原生 `MediaRecorder`**：
   - 录音模式：麦克风 → AAC → mp4
   - 录像模式：摄像头 H.264 (720p/30fps) + 麦克风 AAC → mp4
3. **进程通信**：主程序与服务是两个独立 Python 进程，通过应用目录下的控制文件 `.rec_cmd`（命令）和 `.rec_status`（状态）通信，简单可靠，不依赖 Binder。

## 不装 Linux 也想得到 APK？用 GitHub 云端打包（免费）

1. 注册/登录 [github.com](https://github.com)，新建一个仓库
2. 把本项目（`main.py`、`service.py`、`buildozer.spec`、`.github/` 目录）上传到仓库根目录
3. 进入仓库的 **Actions** 页 → 选择 **Build Android APK** → 点 **Run workflow**
4. 等 10~20 分钟构建完成后，在该次运行页面下载 **backgroundrecorder-apk** 附件，就是做好的 APK

## 网页版（无需打包，马上能用）

直接用手机浏览器打开 `手机录制器.html`（或把它放到任意静态托管上），即可录像/录音，
文件保存到手机下载目录。也可通过浏览器菜单「添加到主屏幕」当作 App 使用。
注意：网页版锁屏后可能被浏览器暂停，真正的不间断后台录制请用上面的 APK 方案。

## 构建步骤

Kivy 打包只能在 **Linux / macOS / WSL** 上进行（Windows 用户建议用 WSL2 或 Docker）。

```bash
# 1. 安装 buildozer（在 WSL/Linux 中）
pip install buildozer cython

# 2. 首次构建会自动下载 Android SDK/NDK（需要网络通畅）
cd phone-recorder-app
buildozer android debug

# 3. 构建产物在 bin/ 目录，安装到手机（需打开 USB 调试）
adb install bin/backgroundrecorder-1.0-arm64-v8a-debug.apk
```

构建成功后也可以直接把 apk 传到手机上点击安装。

## 使用说明

1. 打开 App，首次点击会弹出录音 / 摄像头权限申请，**必须允许**。
2. 点击「开始后台录音」或「开始后台录像」，状态栏出现「后台录制服务」常驻通知。
3. 可以按 Home 键、锁屏，录制继续进行。
4. 点击「停止录制」结束，文件保存在：
   - 优先：`/sdcard/Recordings/REC_audio_xxx.mp4` 或 `REC_video_xxx.mp4`
   - 兜底：应用私有目录（`adb shell run-as org.workbuddy.demo.backgroundrecorder ls files/..` 查看）

## 已知限制（重要）

- **仅支持 Android**。Python 无法为 iOS 打包后台服务，如需 iOS 需改用 Swift 原生开发。
- **Android 10+ 对后台录像限制严格**：必须以前台服务形式运行（本项目已实现），部分国产 ROM（小米/华为等）还会「杀后台」，需在系统设置中给 App 开启「后台运行 / 无限制省电」白名单。
- **录像画面**：使用 MediaRecorder 无预览硬编码路径，个别机型可能要求相机有预览 Surface，若启动失败可尝试先在界面上加一个相机预览页再开始录像。
- Android 14（API 34）要求前台服务声明 `foregroundServiceType`（camera/microphone），请使用 **新版 buildozer / python-for-android（2023.10 以上）** 打包，其会自动补全该声明。
- 屏幕内录制（录屏）不属于本项目范围，录屏需 MediaProjection API。

## 二次开发建议

- 修改分辨率 / 码率 / 帧率：改 `service.py` 中 `create_recorder()` 的参数。
- 改保存路径：改 `service.py` 中 `get_output_dir()`。
- 增加暂停恢复：可在控制命令中扩展 `pause / resume`，配合 `MediaRecorder.pause()` / `resume()`（API 24+）。
