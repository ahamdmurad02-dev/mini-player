#!/usr/bin/env python3
"""MiniPlayer — compact desktop video player."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent, QKeySequence
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QStyle,
    QVBoxLayout,
    QWidget,
)


VIDEO_FILTER = (
    "Video Files (*.mp4 *.mkv *.avi *.mov *.webm *.wmv *.m4v);;"
    "All Files (*.*)"
)


def fmt_time(ms: int) -> str:
    seconds = max(0, ms) // 1000
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


class MiniPlayer(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MiniPlayer")
        self.resize(900, 560)
        self.setMinimumSize(640, 400)
        self.setAcceptDrops(True)

        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.player.setAudioOutput(self.audio)
        self.audio.setVolume(0.8)
        self._seeking = False

        self._build()
        self._connect()
        self._apply_style()

    def _build(self) -> None:
        video = QVideoWidget(self)
        video.setObjectName("video")
        self.player.setVideoOutput(video)

        self.title_label = QLabel("افتح ملف فيديو أو اسحبه إلى النافذة")
        self.title_label.setObjectName("title")
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setObjectName("time")

        self.seek = QSlider(Qt.Orientation.Horizontal)
        self.seek.setRange(0, 0)

        self.btn_open = QPushButton("فتح")
        self.btn_play = QPushButton()
        self.btn_play.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.btn_stop = QPushButton()
        self.btn_stop.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.btn_full = QPushButton("ملء الشاشة")

        vol_text = QLabel("صوت")
        self.volume = QSlider(Qt.Orientation.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(80)
        self.volume.setFixedWidth(120)

        bar = QHBoxLayout()
        bar.setSpacing(8)
        for widget in (
            self.btn_open,
            self.btn_play,
            self.btn_stop,
            self.btn_full,
            self.seek,
            self.time_label,
            vol_text,
            self.volume,
        ):
            bar.addWidget(widget)
        bar.setStretch(4, 1)

        root = QVBoxLayout()
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)
        root.addWidget(self.title_label)
        root.addWidget(video, 1)
        root.addLayout(bar)

        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)

        open_act = QAction("فتح", self)
        open_act.setShortcut(QKeySequence.StandardKey.Open)
        open_act.triggered.connect(self.open_file)
        self.addAction(open_act)

        play_act = QAction("تشغيل", self)
        play_act.setShortcut(Qt.Key.Key_Space)
        play_act.triggered.connect(self.toggle_play)
        self.addAction(play_act)

        full_act = QAction("ملء الشاشة", self)
        full_act.setShortcut(Qt.Key.Key_F)
        full_act.triggered.connect(self.toggle_fullscreen)
        self.addAction(full_act)

        esc_act = QAction("خروج من ملء الشاشة", self)
        esc_act.setShortcut(Qt.Key.Key_Escape)
        esc_act.triggered.connect(self.exit_fullscreen)
        self.addAction(esc_act)

    def _connect(self) -> None:
        self.btn_open.clicked.connect(self.open_file)
        self.btn_play.clicked.connect(self.toggle_play)
        self.btn_stop.clicked.connect(self.player.stop)
        self.btn_full.clicked.connect(self.toggle_fullscreen)
        self.volume.valueChanged.connect(lambda v: self.audio.setVolume(v / 100))
        self.seek.sliderPressed.connect(lambda: setattr(self, "_seeking", True))
        self.seek.sliderReleased.connect(self._seek_release)
        self.player.positionChanged.connect(self._on_position)
        self.player.durationChanged.connect(self._on_duration)
        self.player.playbackStateChanged.connect(self._on_state)
        self.player.errorOccurred.connect(self._on_error)

    def open_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "اختيار فيديو", str(Path.home()), VIDEO_FILTER)
        if path:
            self.load_path(path)

    def load_path(self, path: str) -> None:
        file_path = Path(path)
        self.player.setSource(QUrl.fromLocalFile(str(file_path)))
        self.title_label.setText(file_path.name)
        self.setWindowTitle(f"MiniPlayer — {file_path.name}")
        self.player.play()

    def toggle_play(self) -> None:
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def exit_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()

    def _seek_release(self) -> None:
        self.player.setPosition(self.seek.value())
        self._seeking = False

    def _on_position(self, position: int) -> None:
        if not self._seeking:
            self.seek.setValue(position)
        self.time_label.setText(f"{fmt_time(position)} / {fmt_time(self.player.duration())}")

    def _on_duration(self, duration: int) -> None:
        self.seek.setRange(0, max(0, duration))

    def _on_state(self, state: QMediaPlayer.PlaybackState) -> None:
        playing = state == QMediaPlayer.PlaybackState.PlayingState
        icon = (
            QStyle.StandardPixmap.SP_MediaPause
            if playing
            else QStyle.StandardPixmap.SP_MediaPlay
        )
        self.btn_play.setIcon(self.style().standardIcon(icon))

    def _on_error(self, *_args) -> None:
        message = self.player.errorString() or "تعذر تشغيل الملف"
        self.title_label.setText(message)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:
            self.load_path(urls[0].toLocalFile())

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: #111111;
                color: #EEEEEE;
                font-family: Segoe UI;
                font-size: 13px;
            }
            QLabel#title { font-size: 15px; font-weight: 600; }
            QLabel#time { color: #BBBBBB; min-width: 110px; }
            QVideoWidget#video { background: #000000; }
            QPushButton {
                background: #1F1F1F;
                border: 1px solid #2C2C2C;
                padding: 7px 12px;
                border-radius: 6px;
            }
            QPushButton:hover { background: #2A2A2A; }
            QSlider::groove:horizontal {
                height: 6px;
                background: #2A2A2A;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                width: 14px;
                margin: -5px 0;
                background: #E53935;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal { background: #E53935; border-radius: 3px; }
            """
        )


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("MiniPlayer")
    window = MiniPlayer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
