# 📱 保姆级教程：免费获得可安装的 APK（全程不用写代码）

> 原理：把项目代码传到 GitHub（国外代码托管网站），用它的免费云端服务器帮你把 Python 项目编译成 APK。
> 全程约 20 分钟，其中 15 分钟是等云端自动构建，你只需要点几次鼠标。

---

## 第 1 步：注册 GitHub 账号（已有账号跳过）

1. 浏览器打开 **https://github.com/signup**
2. 输入邮箱 → 设置密码 → 用户名 → 按提示验证即可（全程免费）
3. 注册后登录

## 第 2 步：新建一个仓库（存放代码的"文件夹"）

1. 登录后，点击右上角 **「+」→ New repository**
2. Repository name 填：`backgroundrecorder`（随便起，用英文）
3. 选择 **Public**（公开，免费云构建需要）
4. 其他都不用动，直接点底部绿色按钮 **Create repository**

## 第 3 步：上传我给你准备好的文件

1. 在新建的仓库页面中间，找到 **「uploading an existing file」** 链接，点它
   （或者点 **Add file → Upload files**）
2. 把我给你的压缩包 **先解压**，然后把解压出来的 **全部内容**（main.py、
   service.py、buildozer.spec、README.md，以及 **.github 文件夹**）一起
   **拖拽** 到浏览器的上传区域
   ⚠️ 关键：`.github` 文件夹必须一起传，云端自动打包脚本就在里面
3. 拖完后页面下方点 **Commit changes**（提交）按钮

上传成功后，仓库页面应该能看到：
```
.github/workflows/build-apk.yml
main.py
service.py
buildozer.spec
README.md
```

## 第 4 步：一键启动云端构建

1. 点仓库顶部的 **Actions** 标签页
2. 左侧列表点 **Build Android APK**
3. 右侧点 **Run workflow → 绿色 Run workflow 按钮**

## 第 5 步：等待构建完成（约 10~20 分钟）

- 页面会出现一个黄色圆点 🟡（构建中），变成绿色 ✔️ 就是成功了
- 如果变成红 ❌：点进去截图发给我，我帮你排查

## 第 6 步：下载 APK

1. 点进那次绿色 ✔️ 的构建记录，页面底部有 **Artifacts** 区域
2. 点击下载 **backgroundrecorder-apk**（是一个 zip，解压出 .apk 文件）
3. 把 apk 传到手机（微信文件传输助手 / 数据线 / 网盘都行）

## 第 7 步：手机安装

1. 手机上点击 apk 文件安装
2. 系统提示「未知来源应用」→ 选择 **允许/仍要安装**
3. 打开 App → 点「开始录像/录音」→ 允许摄像头和麦克风权限

✅ 完成！之后锁屏、切后台都能持续录制。

---

## 常见问题

| 问题 | 解决 |
|---|---|
| Actions 页面提示 workflows 被禁用 | 点绿色按钮「I understand my workflows, go ahead and enable them」 |
| 构建失败红叉 | 点进详情截图发给 AI 帮你排查，最常见是 buildozer.spec 被改动 |
| 小米/华为手机装完录不了后台 | 系统设置 → 应用管理 → 本应用 → 省电策略改为「无限制」，并允许后台运行 |
| 下载的 artifact 是 zip | 正常，解压后里面才是 .apk |
