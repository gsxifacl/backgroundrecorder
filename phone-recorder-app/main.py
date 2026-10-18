# -*- coding: utf-8 -*-
"""
后台录像录音 App —— 主程序（Kivy UI）

说明：
- 界面提供「开始后台录音 / 开始后台录像 / 停止」三个按钮
- 录制逻辑在独立的前台服务 service.py 中运行，App 退到后台/锁屏仍继续录制
- 主程序与服务通过控制文件 (.rec_cmd / .rec_status) 通信
"""
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform

IS_ANDROID = (platform == 'android')

if IS_ANDROID:
    from android import AndroidService
    from android.permissions import request_permissions, Permission

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CMD_FILE = os.path.join(APP_DIR, '.rec_cmd')
STATUS_FILE = os.path.join(APP_DIR, '.rec_status')


def write_cmd(text):
    """向服务写入控制命令：audio / video / stop"""
    try:
        with open(CMD_FILE, 'w') as f:
            f.write(text)
    except Exception:
        pass


class RecorderApp(App):
    def build(self):
        self.title = '后台录制'
        self.service = None
        self.recording = False

        root = BoxLayout(orientation='vertical', padding=30, spacing=20)

        self.status_label = Label(
            text='未在录制', font_size='22sp', size_hint=(1, 0.3))
        self.hint_label = Label(
            text='录音模式：仅麦克风 AAC\n录像模式：720p H.264 + 麦克风声音\n'
                 '文件保存到 /sdcard/Recordings（不可写时保存到应用私有目录）',
            font_size='14sp', size_hint=(1, 0.25), halign='center')

        self.btn_audio = Button(text='开始后台录音', font_size='20sp',
                                size_hint=(1, 0.25),
                                background_color=(0.2, 0.6, 0.3, 1))
        self.btn_video = Button(text='开始后台录像', font_size='20sp',
                                size_hint=(1, 0.25),
                                background_color=(0.2, 0.4, 0.8, 1))
        self.btn_stop = Button(text='停止录制', font_size='20sp',
                               size_hint=(1, 0.25),
                               background_color=(0.8, 0.25, 0.2, 1),
                               disabled=True)

        self.btn_audio.bind(on_press=lambda *a: self.start('audio'))
        self.btn_video.bind(on_press=lambda *a: self.start('video'))
        self.btn_stop.bind(on_press=self.stop_recording)

        root.add_widget(self.status_label)
        root.add_widget(self.hint_label)
        root.add_widget(self.btn_audio)
        root.add_widget(self.btn_video)
        root.add_widget(self.btn_stop)

        # 每秒轮询服务写入的状态文件，刷新界面
        Clock.schedule_interval(self.poll_status, 1)
        return root

    # ---------- 权限 ----------

    def request_and_start(self, mode):
        if IS_ANDROID:
            request_permissions(
                [Permission.RECORD_AUDIO, Permission.CAMERA],
                lambda permissions, grants: self.start_service(mode))
        else:
            self.start_service(mode)

    # ---------- 启动 / 停止服务 ----------

    def start_service(self, mode):
        if self.recording:
            return
        # 清理旧的控制/状态文件
        for f in (CMD_FILE, STATUS_FILE):
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception:
                pass

        write_cmd(mode)  # 先写好模式命令，服务启动后立即读取

        if IS_ANDROID:
            self.service = AndroidService('后台录制服务', '正在录制中…')
            self.service.start('RecorderService')

        self.recording = True
        self.btn_stop.disabled = False
        self.btn_audio.disabled = True
        self.btn_video.disabled = True
        self.status_label.text = '服务启动中…'

    def stop_recording(self, *args):
        write_cmd('stop')
        if IS_ANDROID and self.service:
            try:
                self.service.stop()
            except Exception:
                pass
            self.service = None
        self.recording = False
        self.btn_stop.disabled = True
        self.btn_audio.disabled = False
        self.btn_video.disabled = False
        self.status_label.text = '未在录制'

    # ---------- 状态轮询 ----------

    def poll_status(self, dt):
        if not self.recording:
            return
        try:
            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE, 'r') as f:
                    self.status_label.text = f.read().strip() or '录制中…'
        except Exception:
            pass

    def on_stop(self):
        # App 退出时停止录制，避免残留服务
        self.stop_recording()


if __name__ == '__main__':
    RecorderApp().run()
