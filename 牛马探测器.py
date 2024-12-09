#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: barrylee9527
@Filename: 牛马探测器.py
@Createdtime: 2024/12/8 14:13
@Description: 
"""
import threading

import cv2
from PySide6.QtCore import QThread, Signal, Qt, QUrl
from PySide6.QtGui import QImage, QPixmap, QFont
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QProgressBar
from qfluentwidgets import PushButton
from win32api import SetCursorPos, mouse_event


class MainWinodw(QWidget):
    start_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('牛马探测器')
        self.setStyleSheet("background-color: black; color: white;")
        self.resize(1080, 720)
        self.initUI()

    def initUI(self):
        self.label = QLabel("牛马探测器，点击开始按钮开始检测牛马 ！")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 30px; font-weight: bold;")
        self.label.setWordWrap(True)
        self.label.setScaledContents(True)
        # self.label.setFixedHeight(100)
        # self.label.setFixedWidth(300)
        self.startBtn = PushButton("开始探测", self)
        self.startBtn.clicked.connect(self.start)
        layout = QVBoxLayout()
        # 探测进度条
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.hide()
        layout.addWidget(self.progressBar)
        layout.addWidget(self.label)
        layout.addWidget(self.startBtn)
        self.setLayout(layout)
        self.music_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.music_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.80)

    def start(self):
        # 播放音乐
        self.music_player.setSource(QUrl.fromLocalFile("./ss.mp3"))
        self.music_player.play()
        self.search_cow()

    def search_cow(self):
        self.label.setText("正在探测...")
        self.progressBar.show()
        # 显示视频
        self.load_video()

    def load_video(self):
        self.video_thread = LoadVideoThread(self)
        self.video_thread.frame.connect(self.show_video)
        self.video_thread.progress.connect(self.update_progress)
        self.video_thread.finished.connect(self.show_result)
        self.video_thread.start()

    def show_video(self, frame):
        self.label.setPixmap(QPixmap.fromImage(frame))

    def show_result(self):
        import win32con
        # 移动鼠标到(0,0)的位置
        SetCursorPos((0, 0))
        # 模拟按下并释放左键
        mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        self.music_player.stop()

    def update_progress(self, value):
        self.progressBar.setValue(value)
        self.label.setText("正在探测牛马中...{}%".format(value))
        if value == 100:
            self.label.setText("探测完成！")
            self.progressBar.hide()
            self.showFullScreen()
            # 让电脑息屏
            import os
            os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
            self.show_result()


class LoadVideoThread(QThread):
    frame = Signal(QImage)
    progress = Signal(int)
    finished = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cap = cv2.VideoCapture(0)
        self.tip = False

    def run(self):
        for i in range(101):
            self.progress.emit(i)
            import time
            time.sleep(0.1)
        time.sleep(3)
        self.finished.emit()
        while True:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytesPerLine = ch * w
                qImg = QImage(frame.data, w, h, bytesPerLine, QImage.Format.Format_RGB888)
                self.frame.emit(qImg)


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication()
    mainWinodw = MainWinodw()
    mainWinodw.show()
    app.exec()
