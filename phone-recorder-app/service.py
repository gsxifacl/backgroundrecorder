# -*- coding: utf-8 -*-
"""
后台录像录音 App —— 前台服务（p4a service）

该文件由 python-for-android 作为前台服务启动（见 buildozer.spec 中
services = Recorder:service.py:foreground）。
服务运行时状态栏会显示常驻通知，满足 Android 对后台使用
摄像头 / 麦克风的前台服务要求。

工作流程：
1. 启动后轮询控制文件 .rec_cmd，等待命令（audio / video）
2. 用 MediaRecorder 开始录制，输出 mp4
3. 每秒把录制时长 / 文件路径写入 .rec_status，供 UI 轮询显示
4. 收到 stop 命令后停止录制并正常收尾
"""
import os
import time

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CMD_FILE = os.path.join(APP_DIR, '.rec_cmd')
STATUS_FILE = os.path.join(APP_DIR, '.rec_status')


def write_status(text):
    try:
        with open(STATUS_FILE, 'w') as f:
            f.write(text)
    except Exception:
        pass


def read_cmd():
    try:
        if os.path.exists(CMD_FILE):
            with open(CMD_FILE, 'r') as f:
                return f.read().strip()
    except Exception:
        pass
    return ''


def get_output_dir():
    """优先写到公共 Recordings 目录（方便用户用文件管理器找到），失败则退回应用私有目录"""
    candidates = ['/storage/emulated/0/Recordings',
                  '/storage/emulated/0/Movies',
                  APP_DIR]
    for d in candidates:
        try:
            os.makedirs(d, exist_ok=True)
            probe = os.path.join(d, '.probe')
            with open(probe, 'w') as f:
                f.write('ok')
            os.remove(probe)
            return d
        except Exception:
            continue
    return APP_DIR


def create_recorder(mode, out_path):
    """创建并启动 MediaRecorder。返回 recorder 实例。"""
    from jnius import autoclass

    MediaRecorder = autoclass('android.media.MediaRecorder')
    AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
    OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
    AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')
    VideoSource = autoclass('android.media.MediaRecorder$VideoSource')
    VideoEncoder = autoclass('android.media.MediaRecorder$VideoEncoder')

    r = MediaRecorder()
    if mode == 'video':
        # 注意：video 模式必须同时设置音频源，否则编码器参数不完整
        r.setVideoSource(VideoSource.CAMERA)
        r.setAudioSource(AudioSource.MIC)
        r.setOutputFormat(OutputFormat.MPEG_4)
        r.setVideoEncoder(VideoEncoder.H264)
        r.setAudioEncoder(AudioEncoder.AAC)
        r.setVideoSize(1280, 720)
        r.setVideoFrameRate(30)
        r.setVideoEncodingBitRate(5000000)
    else:  # audio
        r.setAudioSource(AudioSource.MIC)
        r.setOutputFormat(OutputFormat.MPEG_4)
        r.setAudioEncoder(AudioEncoder.AAC)
        r.setAudioEncodingBitRate(128000)
        r.setAudioSamplingRate(44100)

    r.setOutputFile(out_path)
    r.prepare()
    r.start()
    return r


def main():
    # ---------- 1. 等待主程序下发模式命令（最多等 10 秒） ----------
    mode = ''
    for _ in range(20):
        mode = read_cmd()
        if mode in ('audio', 'video'):
            break
        time.sleep(0.5)

    if mode not in ('audio', 'video'):
        write_status('未收到录制命令，服务退出')
        return

    # 消费掉命令
    try:
        os.remove(CMD_FILE)
    except Exception:
        pass

    # ---------- 2. 开始录制 ----------
    ext = 'mp4'  # 两种模式都用 mp4 容器
    out_dir = get_output_dir()
    out_path = os.path.join(
        out_dir, 'REC_{}_{}.{}'.format(
            mode, time.strftime('%Y%m%d_%H%M%S'), ext))

    write_status('初始化录制…')
    try:
        recorder = create_recorder(mode, out_path)
    except Exception as e:
        write_status('录制启动失败: {}'.format(e))
        return

    write_status('{}中 0s\n{}'.format('录像' if mode == 'video' else '录音', out_path))
    t0 = time.time()

    # ---------- 3. 循环上报状态，等待停止命令 ----------
    while True:
        time.sleep(1)
        elapsed = int(time.time() - t0)
        cmd = read_cmd()
        if cmd == 'stop':
            try:
                os.remove(CMD_FILE)
            except Exception:
                pass
            break
        write_status('{}中 {}s\n{}'.format(
            '录像' if mode == 'video' else '录音', elapsed, out_path))

    # ---------- 4. 收尾 ----------
    try:
        recorder.stop()
        recorder.release()
        write_status('已完成\n文件: {}'.format(out_path))
    except Exception as e:
        write_status('停止时出错: {}'.format(e))


if __name__ == '__main__':
    main()
